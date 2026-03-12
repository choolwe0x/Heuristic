import pyfiglet
from colorama import Fore, Style, init

# init() ensures color codes work correctly on all platforms including Windows
init(autoreset=True)

VERSION = "1.0.0"
AUTHOR  = "choolwe0x"

def print_banner():
    """Prints the Heuristic ASCII banner with metadata."""

    # pyfiglet renders the tool name as large ASCII art
    # 'slant' is a clean, professional font — alternatives: 'doom', 'big', 'block'
    ascii_art = pyfiglet.figlet_format("Heuristic", font="slant")

    print(Fore.CYAN + ascii_art)
    print(Fore.WHITE + f"  {'─' * 52}")
    print(Fore.YELLOW + f"  Modular Recon Pipeline  |  v{VERSION}  |  {AUTHOR}")
    print(Fore.WHITE + f"  {'─' * 52}")
    print(Fore.RED   + "  [!] For authorised security testing only.")
    print(Fore.WHITE + f"  {'─' * 52}\n")