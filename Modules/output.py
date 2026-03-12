import json
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

def print_results(domain, final_data):
    """Prints results to stdout with color-coded output."""

    print("\n" + Fore.WHITE + "=" * 60)
    print(Fore.CYAN + f"  Recon Results: {domain}")
    print(Fore.WHITE + "=" * 60)

    for sub, results in final_data.items():
        print(Fore.YELLOW + f"\n  Subdomain: {sub}")

        for res in results:
            # Color-code HTTP status codes by class:
            # 2xx green (success), 3xx cyan (redirect),
            # 4xx yellow (client error), 5xx red (server error), Error red
            status = res['status']
            if isinstance(status, int):
                if 200 <= status < 300:
                    status_color = Fore.GREEN
                elif 300 <= status < 400:
                    status_color = Fore.CYAN
                elif 400 <= status < 500:
                    status_color = Fore.YELLOW
                else:
                    status_color = Fore.RED
            else:
                status_color = Fore.RED

            # Line 1: port, status, url
            print(
                Fore.WHITE   + f"    Port: "  + Fore.MAGENTA + f"{res['port']}" +
                Fore.WHITE   + f" | Status: " + status_color  + f"{res['status']}" +
                Fore.WHITE   + f" | URL: "    + Fore.WHITE    + f"{res['url']}"
            )
            # Line 2: server details and security headers on their own line for readability
            print(
                Fore.WHITE   + f"             Server: "      + Fore.CYAN   + f"{res.get('server', '—')}" +
                Fore.WHITE   + f" | Powered By: "            + Fore.CYAN   + f"{res.get('powered_by', '—')}" +
                Fore.WHITE   + f" | CSP Header: "            + (Fore.GREEN if res.get('csp') == 'Yes' else Fore.RED) + f"{res.get('csp', '—')}"
            )

    print(Fore.WHITE + "\n" + "=" * 60 + "\n")


def save_json(domain, final_data, filepath):
    """
    Wraps results in a structured envelope and writes to a JSON file.
    The envelope adds metadata so the file is self-describing
    when you open it later or share it with a client.
    """
    output = {
        "domain": domain,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "total_subdomains": len(final_data),
        "results": final_data
    }
    with open(filepath, "w") as f:
        json.dump(output, f, indent=4)

    print(Fore.GREEN + f"[*] Results saved to {filepath}")