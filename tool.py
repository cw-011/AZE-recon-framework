import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.align import Align
from rich.box import ROUNDED, SIMPLE

console = Console()

# ============================================================
# CONFIG
# ============================================================

REQUIRED_TOOLS = {
    "nmap": "nmap",
    "gobuster": "gobuster",
    "whatweb": "whatweb",
    "sqlmap": "sqlmap",
    "subfinder": "subfinder",
}


# ============================================================
# LANGUAGE
# ============================================================

LANG = {
    "az": {
        "checking": "Sistem tələbləri yoxlanılır...",
        "menu_title": "PENTEST ALƏTLƏRİ",
        "choice": "Seçiminiz",
        "enter_target": "Hədəf (hostname/IP)",
        "invalid_target": "Yanlış hədəf formatıdır.",
        "running": "İcra olunur, gözləyin...",
        "done": "Proses tamamlandı.",
        "exit": "Proqramdan çıxış",

        "tools": {
            "nmap": "Port skaneri və servis versiya təyini",
            "gobuster": "Qovluq və fayl discovery",
            "whatweb": "Veb texnologiyalarının təyini",
            "sqlmap": "İcazəli SQL injection testi",
            "subfinder": "Alt-domen discovery",
        }
    },

    "en": {
        "checking": "Checking system dependencies...",
        "menu_title": "PENTEST TOOLS",
        "choice": "Choice",
        "enter_target": "Target (hostname/IP)",
        "invalid_target": "Invalid target format.",
        "running": "Running, please wait...",
        "done": "Process completed.",
        "exit": "Quit",

        "tools": {
            "nmap": "Port scanner & service detection",
            "gobuster": "Directory & file discovery",
            "whatweb": "Web technology fingerprinting",
            "sqlmap": "Authorized SQL injection testing",
            "subfinder": "Subdomain discovery",
        }
    }
}


# ============================================================
# GENERAL FUNCTIONS
# ============================================================

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    input("\nDavam etmək üçün Enter basın...")


# ============================================================
# TARGET VALIDATION
# ============================================================

def clean_target(target: str) -> str:
    target = target.strip()

    if target.startswith("https://"):
        target = target[8:]

    elif target.startswith("http://"):
        target = target[7:]

    target = target.rstrip("/")

    # Path/query qəbul etmirik
    if "/" in target:
        return ""

    if "?" in target or "#" in target:
        return ""

    return target


def valid_target(target: str) -> bool:
    if not target:
        return False

    if len(target) > 253:
        return False

    # IPv4
    ipv4_pattern = r"^(?:\d{1,3}\.){3}\d{1,3}$"

    if re.fullmatch(ipv4_pattern, target):
        try:
            parts = target.split(".")
            return all(0 <= int(part) <= 255 for part in parts)
        except ValueError:
            return False

    # Hostname
    hostname_pattern = (
        r"^(?=.{1,253}$)"
        r"(?:[A-Za-z0-9]"
        r"(?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)*"
        r"[A-Za-z0-9]"
        r"(?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$"
    )

    return bool(re.fullmatch(hostname_pattern, target))


def get_target(t):
    while True:
        raw = Prompt.ask(
            f"[bold yellow]🎯 {t['enter_target']}[/bold yellow]"
        )

        target = clean_target(raw)

        if valid_target(target):
            return target

        console.print(
            f"[red][!] {t['invalid_target']}[/red]"
        )


# ============================================================
# DEPENDENCIES
# ============================================================

def check_dependencies():
    console.print(
        "[bold yellow][*] Sistem tələbləri yoxlanılır...[/bold yellow]\n"
    )

    missing = []

    for command in REQUIRED_TOOLS:

        if shutil.which(command):

            console.print(
                f"[green][✔] {command} hazırdır.[/green]"
            )

        else:

            console.print(
                f"[red][!] {command} tapılmadı.[/red]"
            )

            missing.append(command)

    if missing:

        console.print(
            "\n[yellow]Çatışmayan alətlər:[/yellow]"
        )

        for tool in missing:
            console.print(f"  • {tool}")

        console.print(
            "\n[dim]Alətləri sisteminizin paket meneceri ilə "
            "ayrıca quraşdırın.[/dim]"
        )

    else:

        console.print(
            "\n[green][✔] Bütün dependency-lər hazırdır.[/green]"
        )

    pause()


# ============================================================
# HTTP / HTTPS
# ============================================================

def choose_protocol():
    console.print(
        "\n[cyan]Protokol seçin:[/cyan]\n"
        "[1] HTTPS\n"
        "[2] HTTP"
    )

    choice = Prompt.ask(
        "👉",
        choices=["1", "2"],
        default="1"
    )

    if choice == "1":
        return "https://"

    return "http://"


# ============================================================
# WORDLIST
# ============================================================

def find_existing_file(paths):

    for path in paths:

        if os.path.isfile(path):
            return path

    return None


def choose_wordlist():

    console.print(
        "\n[yellow]Wordlist seçimi:[/yellow]\n"
        "[1] Common\n"
        "[2] Rockyou\n"
        "[3] Öz wordlist-im"
    )

    choice = Prompt.ask(
        "👉",
        choices=["1", "2", "3"],
        default="1"
    )

    # --------------------------------------------------------
    # COMMON
    # --------------------------------------------------------

    if choice == "1":

        paths = [
            "/usr/share/wordlists/dirb/common.txt",
            "/usr/share/wordlists/dirb/big.txt",
        ]

        wordlist = find_existing_file(paths)

        if wordlist:
            console.print(
                f"[green][✔] Wordlist: {wordlist}[/green]"
            )
            return wordlist

        console.print(
            "[red][!] Common wordlist tapılmadı.[/red]"
        )

        return None

    # --------------------------------------------------------
    # ROCKYOU
    # --------------------------------------------------------

    if choice == "2":

        paths = [
            "/usr/share/wordlists/rockyou.txt",
            "/usr/share/wordlists/rockyou.txt.gz",
        ]

        wordlist = find_existing_file(paths)

        if wordlist:

            # Gobuster .gz faylını birbaşa istifadə edə bilməz.
            if wordlist.endswith(".gz"):

                console.print(
                    "[yellow][!] rockyou.txt.gz tapıldı. "
                    "Gobuster üçün açılmış .txt faylı lazımdır.[/yellow]"
                )

                console.print(
                    "[dim]Məsələn: "
                    "sudo gzip -dk /usr/share/wordlists/rockyou.txt.gz"
                    "[/dim]"
                )

                return None

            console.print(
                f"[green][✔] Wordlist: {wordlist}[/green]"
            )

            return wordlist

        console.print(
            "[red][!] Rockyou wordlist tapılmadı.[/red]"
        )

        return None

    # --------------------------------------------------------
    # CUSTOM WORDLIST
    # --------------------------------------------------------

    while True:

        path = Prompt.ask(
            "[bold yellow]📁 Wordlist-in tam yolunu daxil edin[/bold yellow]"
        ).strip()

        path = os.path.expanduser(path)

        path = str(Path(path).resolve())

        if not os.path.exists(path):

            console.print(
                "[red][!] Fayl mövcud deyil.[/red]"
            )

            retry = Prompt.ask(
                "Yenidən cəhd edilsin?",
                choices=["y", "n"],
                default="y"
            )

            if retry == "n":
                return None

            continue

        if not os.path.isfile(path):

            console.print(
                "[red][!] Göstərilən yol fayl deyil.[/red]"
            )

            return None

        if not os.access(path, os.R_OK):

            console.print(
                "[red][!] Faylı oxumaq mümkün deyil.[/red]"
            )

            return None

        console.print(
            f"[green][✔] Wordlist seçildi:[/green] {path}"
        )

        return path


# ============================================================
# COMMAND EXECUTION
# ============================================================

def run_command(command):

    console.print(
        "\n[dim]Command:[/dim] "
        + " ".join(repr(arg) for arg in command)
    )

    try:

        result = subprocess.run(
            command,
            check=False
        )

        return result.returncode

    except FileNotFoundError:

        console.print(
            "[red][!] Alət sistemdə tapılmadı.[/red]"
        )

        return 127

    except PermissionError:

        console.print(
            "[red][!] Permission denied.[/red]"
        )

        return 126

    except KeyboardInterrupt:

        console.print(
            "\n[yellow][!] Proses dayandırıldı.[/yellow]"
        )

        return 130

    except Exception as error:

        console.print(
            f"[red][!] Xəta: {error}[/red]"
        )

        return 1


# ============================================================
# MENU
# ============================================================

def show_menu(t):

    table = Table(
        title=f"[bold green]═══ {t['menu_title']} ═══[/bold green]",
        box=SIMPLE
    )

    table.add_column(
        "ID",
        justify="center",
        style="bold cyan",
        width=4
    )

    table.add_column(
        "Tool",
        style="bold yellow",
        width=12
    )

    table.add_column(
        "Description",
        style="white"
    )

    table.add_row(
        "1",
        "Nmap",
        t["tools"]["nmap"]
    )

    table.add_row(
        "2",
        "Gobuster",
        t["tools"]["gobuster"]
    )

    table.add_row(
        "3",
        "WhatWeb",
        t["tools"]["whatweb"]
    )

    table.add_row(
        "4",
        "Sqlmap",
        t["tools"]["sqlmap"]
    )

    table.add_row(
        "5",
        "Subfinder",
        t["tools"]["subfinder"]
    )

    table.add_row(
        "6",
        "Exit",
        t["exit"]
    )

    console.print(
        Panel(
            table,
            subtitle="[italic dim]Authorized testing only[/italic dim]",
            subtitle_align="right",
            border_style="green",
            box=ROUNDED,
            padding=(1, 2)
        )
    )


# ============================================================
# MAIN
# ============================================================

def main():

    clear_screen()

    # --------------------------------------------------------
    # BANNER
    # --------------------------------------------------------

    banner = Panel(
        Align.center(
            "[bold cyan]AZERBAIJANI PENTEST FRAMEWORK[/bold cyan]\n"
            "[dim]Authorized Reconnaissance & Scanning Suite[/dim]\n"
            "[italic bright_black]"
            "Created by Yusif Mammadzada"
            "[/italic bright_black]"
        ),
        border_style="cyan",
        box=ROUNDED,
        padding=(1, 4)
    )

    console.print(banner)

    # --------------------------------------------------------
    # LANGUAGE
    # --------------------------------------------------------

    console.print(
        Panel(
            "[yellow]1.[/yellow] Azərbaycan\n"
            "[yellow]2.[/yellow] English",
            title="[bold]Language / Dil[/bold]",
            border_style="yellow",
            box=ROUNDED
        )
    )

    lang_choice = Prompt.ask(
        "👉",
        choices=["1", "2"],
        default="1"
    )

    language = "az" if lang_choice == "1" else "en"

    t = LANG[language]

    # --------------------------------------------------------
    # DEPENDENCY CHECK
    # --------------------------------------------------------

    clear_screen()

    check_dependencies()

    clear_screen()

    # --------------------------------------------------------
    # MAIN LOOP
    # --------------------------------------------------------

    while True:

        show_menu(t)

        choice = Prompt.ask(
            f"[bold cyan]{t['choice']}[/bold cyan]",
            choices=["1", "2", "3", "4", "5", "6"]
        )

        # ----------------------------------------------------
        # EXIT
        # ----------------------------------------------------

        if choice == "6":

            console.print(
                "\n[bold red][x] Proqramdan çıxıldı.[/bold red]"
            )

            sys.exit(0)

        # ----------------------------------------------------
        # TARGET
        # ----------------------------------------------------

        target = get_target(t)

        command = None

        # ====================================================
        # NMAP
        # ====================================================

        if choice == "1":

            console.print(
                "\n[cyan]Nmap Skan Növü:[/cyan]\n"
                "[1] Bütün portlar + versiya\n"
                "[2] Script + versiya\n"
                "[3] Sürətli Top-1000\n"
                "[4] Aqressiv scan"
            )

            n_choice = Prompt.ask(
                "👉",
                choices=["1", "2", "3", "4"],
                default="1"
            )

            if n_choice == "1":

                command = [
                    "nmap",
                    "-p-",
                    "-sV",
                    "-T4",
                    target
                ]

            elif n_choice == "2":

                command = [
                    "nmap",
                    "-sV",
                    "-sC",
                    "-T4",
                    target
                ]

            elif n_choice == "3":

                command = [
                    "nmap",
                    "-sV",
                    "-T4",
                    target
                ]

            elif n_choice == "4":

                command = [
                    "nmap",
                    "-A",
                    "-T4",
                    target
                ]

        # ====================================================
        # GOBUSTER
        # ====================================================

        elif choice == "2":

            protocol = choose_protocol()

            wordlist = choose_wordlist()

            if not wordlist:

                pause()
                clear_screen()
                continue

            command = [
                "gobuster",
                "dir",
                "-u",
                f"{protocol}{target}",
                "-w",
                wordlist
            ]

        # ====================================================
        # WHATWEB
        # ====================================================

        elif choice == "3":

            protocol = choose_protocol()

            command = [
                "whatweb",
                f"{protocol}{target}"
            ]

        # ====================================================
        # SQLMAP
        # ====================================================

        elif choice == "4":

            console.print(
                "\n[yellow]⚠ SQLMap yalnız icazəniz olan "
                "sistemlərdə istifadə edilməlidir.[/yellow]"
            )

            console.print(
                "[dim]Test üçün parametrli URL daxil edin.[/dim]"
            )

            url = Prompt.ask(
                "URL"
            ).strip()

            if not (
                url.startswith("http://")
                or url.startswith("https://")
            ):

                console.print(
                    "[red][!] URL http:// və ya "
                    "https:// ilə başlamalıdır.[/red]"
                )

                pause()
                clear_screen()
                continue

            command = [
                "sqlmap",
                "-u",
                url,
                "--batch"
            ]

        # ====================================================
        # SUBFINDER
        # ====================================================

        elif choice == "5":

            command = [
                "subfinder",
                "-d",
                target
            ]

        # ====================================================
        # EXECUTE
        # ====================================================

        if command:

            console.print(
                f"\n[bold magenta]{t['running']}[/bold magenta]"
            )

            return_code = run_command(command)

            if return_code == 0:

                console.print(
                    f"\n[bold green]{t['done']}[/bold green]"
                )

            else:

                console.print(
                    f"\n[yellow][!] Proses "
                    f"exit code: {return_code}[/yellow]"
                )

        pause()

        clear_screen()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:
        main()

    except KeyboardInterrupt:

        console.print(
            "\n\n[yellow][!] Proqram dayandırıldı.[/yellow]"
        )

        sys.exit(0)
