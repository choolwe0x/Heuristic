import requests
from concurrent.futures import ThreadPoolExecutor

def probe_url(url, port):
    """Performs the actual HTTP request."""
    try:
        # We follow redirects to see the final destination
        response = requests.get(url, timeout=5, allow_redirects=True)
        return {
            "port": port,
            "url": url,
            "status": response.status_code,
            "server": response.headers.get("Server", "Unknown")
        }
    except requests.exceptions.RequestException:
        return {"port": port, "url": url, "status": "Error", "server": "N/A"}

def run_prober(scan_results):
    """Processes the scanner dictionary and probes open ports in parallel."""
    print(f"[*] Probing HTTP services for {len(scan_results)} targets...")
    final_results = {}
    
    # We create a list of all URLs that need probing
    tasks = []
    for sub, ports in scan_results.items():
        for port in ports:
            protocol = "https" if port == 443 else "http"
            url = f"{protocol}://{sub}"
            tasks.append((sub, url, port))

    # Use threading to probe all URLs at once
    with ThreadPoolExecutor(max_workers=20) as executor:
        # We submit each task and keep track of which subdomain it belongs to
        future_to_sub = {executor.submit(probe_url, url, port): sub for sub, url, port in tasks}
        
        for future in future_to_sub:
            sub = future_to_sub[future]
            if sub not in final_results:
                final_results[sub] = []
            final_results[sub].append(future.result())
            
    return final_results