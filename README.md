# Heuristic 🧠

> *In the psychology of influence, a heuristic is a mental shortcut used to quickly form a judgment or solve a problem. In security, the same principle applies: cut through noise, surface what matters.*

Heuristic is a modular Python reconnaissance pipeline that ties subdomain discovery, TCP port scanning, and HTTP service probing into a single, fast, opinionated workflow. It is built for security professionals who need a structured snapshot of an external attack surface without stitching together five separate tools.

---

## How It Works

Heuristic runs three sequential stages:

```
Target Domain
     │
     ▼
[1] Subdomain Enumeration   ← Passive. Queries crt.sh certificate logs.
     │
     ▼
[2] TCP Port Scanner        ← Active. Threaded connect scan across common ports.
     │
     ▼
[3] HTTP Service Prober     ← Active. Fingerprints status codes and server headers.
     │
     ▼
Structured Output
```

Each stage is a self-contained module. You can extend, replace, or chain them independently.

---

## Features

- **Passive Enumeration** — Harvests subdomains from crt.sh certificate transparency logs with wildcard filtering.
- **Threaded TCP Scanning** — Concurrent connect scans with configurable port targets. No Nmap dependency.
- **HTTP Fingerprinting** — Probes open ports for HTTP status codes and Server headers, following redirects.
- **Fail-Fast Design** — Unresolvable hosts are skipped early. Dead-end stages exit cleanly with actionable messages.
- **Modular Architecture** — Each pipeline stage lives in its own module. Swap or extend without touching the core.

---

## Installation

**Requirements:** Python 3.10+

```bash
git clone https://github.com/choolwe0x/Heuristic.git
cd Heuristic
pip3 install -r requirements.txt
```

---

## Usage

```bash
python3 main.py -d example.com
```

### Example Output

```
[*] Found 42 subdomains.
[*] Resolving and scanning 42 subdomains across 11 ports...
    [-] Could not resolve: legacy.example.com
    [+] mail.example.com:443 OPEN
    [+] api.example.com:8443 OPEN
    [+] dev.example.com:8080 OPEN
[*] Scan complete. 3 subdomains with open ports.
[*] Probing HTTP services for 3 targets...

============================================================
Recon results for example.com:
============================================================

Subdomain: mail.example.com
  Port: 443 | Status: 200 | Server: nginx | URL: https://mail.example.com

Subdomain: api.example.com
  Port: 8443 | Status: 401 | Server: Apache | URL: https://api.example.com

Subdomain: dev.example.com
  Port: 8080 | Status: 200 | Server: Unknown | URL: http://dev.example.com
```

---

## Module Reference

| Module | Function | Description |
|---|---|---|
| `modules/subdomains.py` | `get_subdomains(domain)` | Queries crt.sh and returns a deduplicated set of subdomains |
| `modules/scanner.py` | `run_scanner(subdomains, ports)` | Resolves hosts and runs threaded TCP connect scans |
| `modules/prober.py` | `run_prober(scan_results)` | Probes open ports for HTTP responses and server headers |

### Default Port List

```
80, 443, 8080, 8443, 8888, 3000, 3001, 5000, 5001, 9090, 9443
```

---

## Project Structure

```
Heuristic/
├── main.py                  # Pipeline entrypoint
├── requirements.txt
├── modules/
│   ├── __init__.py
│   ├── subdomains.py        # Passive enumeration
│   ├── scanner.py           # TCP port scanner
│   └── prober.py            # HTTP service prober
└── README.md
```

---

## Roadmap

- [ ] Add DNS bruteforce as a secondary enumeration source alongside crt.sh
- [ ] Shodan/Censys API integration for IP-to-host correlation
- [ ] JSON output mode for downstream tooling and report pipelines
- [ ] Scoring layer to rank discovered assets by exposure signal
- [ ] Custom port list via CLI flag (`--ports`)
- [ ] Rate limiting and stealth timing options

---

## Legal

Heuristic is built for authorised security testing. Only run it against domains you own or have explicit written permission to test. Unauthorised scanning is illegal in most jurisdictions.

---

## Author

**Choolwe Chiti Chilinda**
Head of Technical Services, DigitalSafe Limited
[github.com/choolwe0x](https://github.com/choolwe0x)