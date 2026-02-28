# Heuristic 🧠
> **Ties your subdomain discovery and service mapping into one script.**

Heuristic is a modular Python reconnaissance pipeline designed for efficient attack surface discovery. By combining passive enumeration with active port scanning and HTTP probing, it provides a structured snapshot of a domain's external footprint.

## ✨ Key Features
* **Passive Enumeration**: Queries `crt.sh` certificate logs to find subdomains without direct interaction.
* **Multi-threaded Scanning**: Uses `ThreadPoolExecutor` for high-speed TCP port validation. ⚡
* **Service Intelligence**: Probes open ports for HTTP status codes and Server headers (Nginx, Apache, etc.).
* **Modular Architecture**: Easily swap or extend modules for discovery, scanning, or probing.

## ⚙️ Installation

1. **Clone the repository**:
   ```bash
   git clone [https://github.com/yourusername/heuristic.git](https://github.com/yourusername/heuristic.git)
   cd heuristic

2. **Install dependencies**
    ```Bash
    pip install -r requirements.txt

🚀 Usage
Run the pipeline using the -d flag for the target domain:
    ```Bash
    python main.py -d example.com

python main.py -d example.com