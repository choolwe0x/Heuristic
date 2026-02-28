import argparse
from modules.subdomains import get_subdomains
from modules.scanner import run_scanner
from modules.prober import run_prober

def main():
    parser = argparse.ArgumentParser(description="Heuristic: A modular recon pipeline.")
    parser.add_argument("-d", "--domain", required=True, help="The target domain for recon.")
    args = parser.parse_args()

    # 1. Subdomain Enumeration
    subs = get_subdomains(args.domain)
    if not subs:
        print(f"[!] No subdomains found for {args.domain}. Exiting.")
        return  # Exit the main function if no subdomains are found

    # 2. Port Scanning
    scan_results = run_scanner(subs)

    # Filter out subdomains with no open ports before probing
    active_subs = {sub: ports for sub, ports in scan_results.items() if ports}

    if not active_subs:
        print("[!] No active subdomains with open ports found. Exiting.")
        return  # Exit if there are no active subdomains to probe
    
    # 3. Probing HTTP Services
    final_data = run_prober(active_subs)

    # 4. Output Results
    print("\n" + "="*60)
    print(f"Recon results for {args.domain}:")
    print("="*60)
    for sub, results in final_data.items():
        print(f"\nSubdomain: {sub}")
        for res in results:
            print(f"  Port: {res['port']} | Status: {res['status']} | Server: {res['server']} | URL: {res['url']}")

if __name__ == "__main__":
    main()