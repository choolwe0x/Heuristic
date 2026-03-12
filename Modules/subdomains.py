import requests

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
        }
        print(f"[*] Found {len(subdomains)} subdomains.")
        return subdomains
    except requests.exceptions.RequestException as e:
        print(f"[!] Error connecting to crt.sh: {e}")
        return set()