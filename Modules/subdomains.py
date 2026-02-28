import requests

def get_subdomains(domain):
    # We want to search for cerificates related to the domain
    url = "https://crt.sh/"
    params = {
        'q': f"%.{domain}", # The % is a wildcard for the API
        'output': 'json' # We want the data in a format that easily readable
    }

    try:
        # We add a timeout so the script doesn't have forever
        response = requests.get(url, params=params, timeout=15)

        data = response.json()

        subdomains = {
            sub.strip()
            for item in data
            for sub in item['name_value'].split('\n')
            if not sub.startswith('*.')  # Exclude wildcard subdomains
        }
        return subdomains

    except requests.exceptions.RequestException as e:
        print(f"[!] Error connecting to crt.sh: {e}")
        return set() # Return an empty set so the main script can keep moving