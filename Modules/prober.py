import requests

def probe_target(subdomain, ports):
    """Probes all open ports on a subdomain and returns a list of results."""
    results = []
    
    for port in ports:
        # Determine the protocol based on the port
        protocol = "https" if port == 443 else "http"
        url = f"{protocol}://{subdomain}:{port}"
        
        try:
            # We follow redirects but set a timeout so we don't hang
            response = requests.get(url, timeout=5, allow_redirects=True)
            results.append({
                "port": port,
                "url": url,
                "status": response.status_code,
                "server": response.headers.get("Server", "Unknown")
            })
        except requests.exceptions.RequestException:
            # If the connection fails, we can record that the service didn't respond
            results.append({"port": port, "url": url, "status": "Error", "server": "N/A"})
            
    return results