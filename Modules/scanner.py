import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

# Ports that matter on real external attack surfaces.
# Covers standard web, alternate web, common dev/proxy ports.
DEFAULT_PORTS = [80, 443, 8080, 8443, 8888, 3000, 3001, 5000, 5001, 9090, 9443]

TIMEOUT = 2       # seconds per connect attempt
MAX_WORKERS = 50  # tune down if you're hitting rate limits or dropping packets


def _resolve(subdomain: str) -> str | None:
    """Resolve subdomain to IP. Returns None if DNS fails."""
    try:
        return socket.gethostbyname(subdomain)
    except socket.gaierror:
        return None


def _tcp_connect(subdomain: str, ip: str, port: int) -> tuple[str, int] | None:
    """
    Attempt a TCP connect to ip:port.
    Returns (subdomain, port) if open, None otherwise.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(TIMEOUT)
    try:
        result = sock.connect_ex((ip, port))
        if result == 0:
            return (subdomain, port)
        return None
    except (socket.timeout, socket.error):
        return None
    finally:
        sock.close()


def run_scanner(subdomains: set[str], ports: list[int] = DEFAULT_PORTS) -> dict[str, list[int]]:
    """
    Takes a set of subdomains, resolves each, and TCP-scans the given port list.
    Returns: {subdomain: [open_ports]}
    Only subdomains with at least one open port appear in the result.
    """
    print(f"[*] Resolving and scanning {len(subdomains)} subdomains across {len(ports)} ports...")

    # Phase 1: DNS resolution — skip unresolvable hosts early
    resolved = {}
    for sub in subdomains:
        ip = _resolve(sub)
        if ip:
            resolved[sub] = ip
        else:
            print(f"    [-] Could not resolve: {sub}")

    print(f"[*] {len(resolved)} subdomains resolved. Starting TCP scan...")

    # Phase 2: Threaded TCP connect scan
    # Build the full task list: (subdomain, ip, port)
    tasks = [
        (sub, ip, port)
        for sub, ip in resolved.items()
        for port in ports
    ]

    open_ports: dict[str, list[int]] = {}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_task = {
            executor.submit(_tcp_connect, sub, ip, port): (sub, port)
            for sub, ip, port in tasks
        }

        for future in as_completed(future_to_task):
            result = future.result()
            if result:
                sub, port = result
                if sub not in open_ports:
                    open_ports[sub] = []
                open_ports[sub].append(port)
                print(f"    [+] {sub}:{port} OPEN")

    # Sort ports per subdomain for clean output
    for sub in open_ports:
        open_ports[sub].sort()

    print(f"[*] Scan complete. {len(open_ports)} subdomains with open ports.")
    return open_ports
