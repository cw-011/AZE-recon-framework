import os
import subprocess
import sys
import shutil
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.align import Align

console = Console()

REQUIRED_TOOLS = {
    "nmap": "nmap",
    "gobuster": "gobuster",
    "whatweb": "whatweb",
    "sqlmap": "sqlmap"
}

LANG = {
    "az": {
        "checking": "[*] Sistem tələbləri yoxlanılır...",
        "menu_title": "PENTEST ALƏTLƏRİ",
        "choice": "Seçiminiz: ",
        "enter_target": "Hədəf (məsələn: example.com): ",
        "nmap_choice": "\n[cyan]Nmap Skan Növü:[/cyan]\n[1] Bütün Portlar & Versiya (-p- -sV -T4) [Tövsiyə]\n[2] Script & Versiya (-sV -sC -T4)\n[3] Sürətli Top-1000 (-sV -T4)\n[4] Aqressiv Skan (-A -T4)",
        "proto_choice": "Protokol:\n[1] https:// (Tövsiyə)\n[2] http://",
        "wordlist_choice": "\n[yellow]Wordlist Seçimi:[/yellow]\n[1] Common (/usr/share/wordlists/dirb/common.txt)\n[2] Rockyou (/usr/share/wordlists/rockyou.txt)\n[3] Xüsusi yol daxil et",
        "wordlist_prompt": "Seçim (1, 2, 3): ",
        "enter_custom_wordlist": "Wordlist tam yolu: ",
        "running": "[+] İcra olunur, gözləyin...",
        "done": "[✔] Proses tamamlandı.",
        "tools": {
            "nmap": "Port skaneri və servis versiya təyini",
            "gobuster": "Qovluq və fayl fassing (Wordlist ilə)",
            "whatweb": "Veb texnologiyalarının təyini",
            "sqlmap": "Avtomatlaşdırılmış SQL injection testi",
            "subfinder": "Sürətli alt-domen (subdomain) axtarışı",
            "exit": "Proqramdan çıxış"
        }
    },
    "en": {
        "checking": "[*] Checking system dependencies...",
        "menu_title": "PENTEST TOOLS",
        "choice": "Choice: ",
        "enter_target": "Target (e.g., example.com): ",
        "nmap_choice": "\n[cyan]Nmap Scan Type:[/cyan]\n[1] All Ports & Version (-p- -sV -T4) [Recommended]\n[2] Script & Version (-sV -sC -T4)\n[3] Fast Top-1000 (-sV -T4)\n[4] Aggressive Scan (-A -T4)",
        "proto_choice": "Protocol:\n[1] https:// (Recommended)\n[2] http://",
        "wordlist_choice": "\n[yellow]Wordlist Option:[/yellow]\n[1] Common (/usr/share/wordlists/dirb/common.txt)\n[2] Rockyou (/usr/share/wordlists/rockyou.txt)\n[3] Custom path",
        "wordlist_prompt": "Choice (1, 2, 3): ",
        "enter_custom_wordlist": "Full path to wordlist: ",
        "running": "[+] Running tool, please wait...",
        "done": "[✔] Process completed.",
        "tools": {
            "nmap": "Port scanner & Service version detection",
            "gobuster": "Directory & File fuzzing (Wordlist)",
            "whatweb": "Web technology fingerprinting",
            "sqlmap": "Automated SQL injection testing",
            "subfinder": "Fast Subdomain enumeration",
            "exit": "Quit the framework"
        }
    }
}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def clean_target(target):
    target = target.strip()
    if target.startswith("http://"):
        target = target[7:]
    elif target.startswith("https://"):
        target = target[8:]
    return target.rstrip('/')

def check_dependencies(t):
    console.print(f"[bold yellow]{t['checking']}[/bold yellow]\n")
    
    for cmd, pkg in REQUIRED_TOOLS.items():
        if not shutil.which(cmd):
            console.print(f"[red][!] '{cmd}' tapılmadı. Quraşdırılır...[/red]")
            try:
                subprocess.run(f"sudo apt install -y {pkg}", shell=True, check=True)
                console.print(f"[green][✔] '{cmd}' quraşdırıldı.[/green]\n")
            except Exception as e:
                console.print(f"[red][X] '{cmd}' xətası: {e}[/red]\n")
        else:
            console.print(f"[green][✔] '{cmd}' hazırdır.[/green]")

    if not shutil.which("subfinder"):
        console.print(f"[red][!] 'subfinder' tapılmadı. Quraşdırılır...[/red]")
        try:
            if not shutil.which("go"):
                subprocess.run("sudo apt install -y golang", shell=True, check=True)
            subprocess.run("go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest", shell=True, check=True)
            console.print(f"[green][✔] 'subfinder' quraşdırıldı.[/green]\n")
        except Exception as e:
            console.print(f"[red][X] 'subfinder' xətası: {e}[/red]\n")
    else:
        console.print(f"[green][✔] 'subfinder' hazırdır.[/green]")

    print()
    input("Davam etmək üçün 'Enter' basın...")

def main():
    clear_screen()
    
    banner = Panel(
        Align.center("[bold cyan]AZERBAIJANI PENTEST FRAMEWORK[/bold cyan]\n[dim]Automated Reconnaissance & Scanning Suite[/dim]\n[italic bright_black]Created by Yusif Mammadzada[/italic bright_black]"),
        border_style="cyan",
        box=__import__('rich.box', fromlist=['ROUNDED']).ROUNDED,
        padding=(1, 4)
    )
    console.print(banner)

    console.print(Panel("[yellow]1.[/yellow] Azərbaycan\n[yellow]2.[/yellow] English", title="[bold]Language / Dil[/bold]", border_style="yellow", box=__import__('rich.box', fromlist=['ROUNDED']).ROUNDED))
    lang_choice = Prompt.ask("👉", choices=["1", "2"], default="1")
    l_key = "az" if lang_choice == "1" else "en"
    t = LANG[l_key]

    clear_screen()
    check_dependencies(t)
    clear_screen()

    while True:
        table = Table(title=f"[bold green]═══ {t['menu_title']} ═══[/bold green]", box=__import__('rich.box', fromlist=['SIMPLE']).SIMPLE, style="dim")
        table.add_column("ID", justify="center", style="bold cyan", width=4)
        table.add_column("Tool", style="bold yellow", width=12)
        table.add_column("Description", style="white")

        table.add_row("1", "Nmap", t["tools"]["nmap"])
        table.add_row("2", "Gobuster", t["tools"]["gobuster"])
        table.add_row("3", "WhatWeb", t["tools"]["whatweb"])
        table.add_row("4", "Sqlmap", t["tools"]["sqlmap"])
        table.add_row("5", "Subfinder", t["tools"]["subfinder"])
        table.add_row("6", "Exit", t["tools"]["exit"])

        console.print(Panel(table, subtitle="[italic dim]Created by Yusif Mammadzada[/italic dim]", subtitle_align="right", border_style="green", box=__import__('rich.box', fromlist=['ROUNDED']).ROUNDED, padding=(1, 2)))

        choice = Prompt.ask(f"[bold cyan]{t['choice']}[/bold cyan]", choices=["1", "2", "3", "4", "5", "6"])

        if choice == "6":
            console.print("[bold red]\n[x] Çıxış edildi. Uğurlar![/bold red]")
            sys.exit(0)

        raw_target = Prompt.ask(f"[bold yellow]🎯 {t['enter_target']}[/bold yellow]")
        target = clean_target(raw_target)

        if choice in ["2", "3", "4"]:
            console.print(t["proto_choice"])
            p_choice = Prompt.ask("👉", choices=["1", "2"], default="1")
            proto = "https://" if p_choice == "1" else "http://"
        else:
            proto = ""

        if choice == "1":
            console.print(t["nmap_choice"])
            n_choice = Prompt.ask("👉", choices=["1", "2", "3", "4"], default="1")
            if n_choice == "1":
                cmd = f"nmap -p- -sV -T4 {target}"
            elif n_choice == "2":
                cmd = f"nmap -sV -sC -T4 {target}"
            elif n_choice == "3":
                cmd = f"nmap -sV -T4 {target}"
            else:
                cmd = f"nmap -A -T4 {target}"
                
        elif choice == "2":
            console.print(t["wordlist_choice"])
            wl_choice = Prompt.ask(f"[bold cyan]{t['wordlist_prompt']}[/bold cyan]", choices=["1", "2", "3"], default="1")
            
            if wl_choice == "1":
                wordlist = "/usr/share/wordlists/dirb/common.txt"
            elif wl_choice == "2":
                wordlist = "/usr/share/wordlists/rockyou.txt"
            else:
                wordlist = Prompt.ask(f"[bold yellow]📁 {t['enter_custom_wordlist']}[/bold yellow]")
            
            cmd = f"gobuster dir -u {proto}{target} -w {wordlist}"
            
        elif choice == "3":
            cmd = f"whatweb {proto}{target}"
        elif choice == "4":
            cmd = f"sqlmap -u {proto}{target} --batch --dbs"
        elif choice == "5":
            cmd = f"subfinder -d {target}"
        else:
            continue

        console.print(f"\n[bold magenta]{t['running']}[/bold magenta]")
        console.print(f"[dim]Command: {cmd}[/dim]\n")

        try:
            subprocess.run(cmd, shell=True)
        except Exception as e:
            console.print(f"[bold red][!] Xəta: {e}[/bold red]")

        console.print(f"\n[bold green]{t['done']}[/bold green]\n")
        input("Davam etmək üçün 'Enter' basın...")
        clear_screen()

if __name__ == "__main__":
    main()
