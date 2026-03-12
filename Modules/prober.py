import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# A lookup table mapping common raw Server header values to meaningful descriptions.
# Raw headers are often cryptic abbreviations or internal codenames.
# This table translates them so the output is immediately useful without Googling.
SERVER_FINGERPRINTS = {
    "gws":             "Google Web Server",
    "esf":             "Google Edge Serving Framework",
    "nginx":           "Nginx",
    "apache":          "Apache HTTP Server",
    "microsoft-iis":   "Microsoft IIS",
    "cloudflare":      "Cloudflare",
    "lighttpd":        "Lighttpd",
    "openresty":       "OpenResty (Nginx + Lua)",
    "caddy":           "Caddy",
    "gunicorn":        "Gunicorn (Python WSGI)",
    "jetty":           "Eclipse Jetty (Java)",
    "tomcat":          "Apache Tomcat (Java)",
    "envoy":           "Envoy Proxy",
    "cowboy":          "Cowboy (Erlang/Elixir)",
    "werkzeug":        "Werkzeug (Python dev server)",
    "AmazonS3":        "Amazon S3 Static Hosting",
    "awselb":          "AWS Elastic Load Balancer",
}

def _fingerprint_server(raw_value: str) -> str:
    """
    Takes the raw Server header string and returns a human-readable label.
    
    The lookup is case-insensitive because server headers are inconsistently
    cased across vendors. If we don't recognise the value, we return it as-is
    rather than hiding it — an unknown server string is still useful information.
    """
    if not raw_value or raw_value == "Unknown":
        # No Server header was returned at all.
        # This is actually a security hardening practice — the admin has
        # deliberately suppressed the header to avoid leaking stack info.
        return "Hidden (header suppressed)"

    # Check our lookup table first using a case-insensitive partial match.
    # Partial match matters because values like "Apache/2.4.51" contain
    # the vendor name but also a version string we want to preserve.
    lower = raw_value.lower()
    for key, label in SERVER_FINGERPRINTS.items():
        if key.lower() in lower:
            # If the raw value has a version number attached, keep it.
            # e.g. "Apache/2.4.51" becomes "Apache HTTP Server (2.4.51)"
            parts = raw_value.split("/")
            version = f" ({parts[1]})" if len(parts) > 1 else ""
            return f"{label}{version}"

    # Not in our table — return raw so we don't lose information.
    return raw_value


def probe_url(url: str, port: int) -> dict:
    """
    Makes an HTTP GET request to a single URL and extracts useful
    metadata from the response headers.
    
    We collect more than just the Server header because a single header
    rarely tells the full story. X-Powered-By leaks backend language/framework,
    and X-Frame-Options/Content-Security-Policy tell us about the security
    posture of the application.
    """
    try:
        # allow_redirects=True means we follow 301/302s to the final destination.
        # timeout=5 prevents the thread from hanging on a slow or unresponsive host.
        response = requests.get(url, timeout=5, allow_redirects=True)

        raw_server = response.headers.get("Server", "Unknown")

        return {
            "port":          port,
            "url":           url,
            "status":        response.status_code,
            # Human-readable server description instead of raw header value
            "server":        _fingerprint_server(raw_server),
            # X-Powered-By leaks the backend language or framework e.g. PHP/7.4, ASP.NET
            # Many hardened servers strip this header — its absence is also informative
            "powered_by":    response.headers.get("X-Powered-By", "—"),
            # Content-Security-Policy presence indicates the team has thought about
            # client-side injection defences. Its absence is a finding on its own.
            "csp":           "Yes" if "Content-Security-Policy" in response.headers else "No",
        }

    except requests.exceptions.RequestException:
        # Connection failed entirely — host may be up on TCP but not serving HTTP,
        # or the connection timed out. We record the failure rather than silently dropping it.
        return {
            "port":       port,
            "url":        url,
            "status":     "Error",
            "server":     "No response",
            "powered_by": "—",
            "csp":        "—",
        }


def run_prober(scan_results: dict) -> dict:
    """
    Takes the scanner's output — a dict of {subdomain: [open_ports]} —
    and probes every open port on every subdomain in parallel.
    
    Returns a dict of {subdomain: [probe_results]} where each probe result
    is the dictionary returned by probe_url above.
    """
    print(f"[*] Probing HTTP services for {len(scan_results)} targets...")

    final_results = {}

    # Build a flat list of every (subdomain, url, port) combination we need to probe.
    # We flatten here so the thread pool can work across all targets simultaneously
    # rather than processing one subdomain at a time.
    tasks = []
    for sub, ports in scan_results.items():
        for port in ports:
            protocol = "https" if port == 443 or port == 8443 else "http"
            url = f"{protocol}://{sub}"
            tasks.append((sub, url, port))

    # as_completed() yields futures as they finish rather than in submission order.
    # This means faster hosts report back immediately without waiting for slow ones.
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_sub = {
            executor.submit(probe_url, url, port): sub
            for sub, url, port in tasks
        }
        for future in as_completed(future_to_sub):
            sub = future_to_sub[future]
            if sub not in final_results:
                final_results[sub] = []
            final_results[sub].append(future.result())

    return final_results