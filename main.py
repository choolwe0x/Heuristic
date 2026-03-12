import argparse
from modules.subdomains import get_subdomains
from modules.scanner import run_scanner
from modules.prober import run_prober
from modules.output import print_results, save_json
from modules.banner import print_banner

def main():
    print_banner()
    parser = argparse.ArgumentParser(description="Heuristic: Modular Recon Pipeline")
    parser.add_argument("-d", "--domain", required=True, help="Target domain for recon")

    # --ouput is optional, if not provided results will only be printed to stdout
    parser.add_argument("-o", "--output", required=False, metavar="FILE", help="Save results to a JSON file. E.g. -o results.json")

    args = parser.parse_args()

    # Step 1: Get subdomains
    subdomains = get_subdomains(args.domain)
    if not subdomains:
        print("[!] No subdomains found. Exiting.")
        return
    
    # Step 2: Run port scanner on found subdomains
    scan_results = run_scanner(subdomains)
    active_subs = {sub: ports for sub, ports in scan_results.items() if ports}
    if not active_subs:
        print("[!] No active services found on discovered subdomains. Exiting.")
        return
    
    # Step 3: Probe active services for HTTP responses
    final_data = run_prober(active_subs)
    
    # Step 4: Print results
    print_results(args.domain,final_data)
    
    # Step 5: Save results to JSON file if specified
    if args.output:
        save_json(args.domain, final_data, args.output)

if __name__ == "__main__":
    main()