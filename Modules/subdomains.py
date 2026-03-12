import requests

def _is_valid_hostname(hostname: str) -> bool:
    """
    Validates that a hostname is structurally sane before we attempt
    DNS resolution. crt.sh can return malformed entries: concatenated
    wildcard values, merged multi-line names, or strings hundreds of
    characters long. The DNS spec caps the total hostname at 253 chars
    and each individual label (the parts between dots) at 63 chars.
    Anything outside those bounds will crash the resolver.
    """
    if not hostname or len(hostname) > 253:
        return False
    labels = hostname.split(".")
    return all(len(label) <= 63 and len(label) > 0 for label in labels)

def get_subdomains(domain):
    url = "https://crt.sh/"
    params = {
        'q': f"%.{domain}",
        'output': 'json'
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Heuristic-Recon/1.0)"
    }
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        if not response.text.strip():
            print("[!] crt.sh returned an empty response. Try again in a moment.")
            return set()
        data = response.json()
        subdomains = {
            sub.strip()
            for item in data
            for sub in item['name_value'].split('\n')
            if not sub.startswith('*.')
            and _is_valid_hostname(sub.strip())  # drop malformed entries
        }
        print(f"[*] Found {len(subdomains)} subdomains.")
        return subdomains
    except requests.exceptions.RequestException as e:
        print(f"[!] Error connecting to crt.sh: {e}")
        return set()