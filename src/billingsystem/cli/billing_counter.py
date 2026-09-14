import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

# Necessary for Windows console to handle UTF-8 symbols and emojis without cp1250 encoding errors
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8", errors="replace")

from billingsystem.cli.services.command_service import Console as ShellConsole
from billingsystem.cli.services.screenshot_service import ScreenshotService
from billingsystem.cli.tui import (
    console,
    get_recordings_dir,
    print_banner,
    print_session_start_panel,
    print_session_summary_panel,
    prompt_main_menu,
    prompt_session_config,
)
from rich.prompt import Prompt


def open_recordings_folder(path: Optional[str] = None) -> None:
    if path is None:
        folder = get_recordings_dir()
    else:
        folder = Path(path).resolve()

    if not folder.exists():
        folder.mkdir(parents=True, exist_ok=True)

    console.print(f"[bold green]Opening folder:[/] [underline blue]{folder}[/]")

    if os.name == "nt":
        os.startfile(folder)
    elif sys.platform == "darwin":
        subprocess.run(["open", str(folder)], check=False)
    else:
        subprocess.run(["xdg-open", str(folder)], check=False)


def run_recording_session(session_name: str, interval: float = 10.0) -> None:
    session_dir = Path(f"./recordings/{session_name}").resolve()

    with console.status("[bold cyan]Initializing environment and screenshot service...[/bold cyan]", spinner="dots"):
        shell = ShellConsole(recording_name=session_name)
        ss_service = ScreenshotService(recording_name=session_name, interval=interval)
        ss_service.start_recording()
        time.sleep(0.4)

    print_session_start_panel(
        session_name=session_name,
        interval=interval,
        session_path=str(session_dir),
    )

    start_time = time.time()

    try:
        while shell.is_alive():
            shell.prompt()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Interrupt signal detected (Ctrl+C)... Stopping session.[/bold yellow]")
    finally:
        with console.status("[bold yellow]Saving logs and stopping screenshot service...[/bold yellow]", spinner="bouncingBar"):
            shell.stop()
            ss_service.stop_recording()
            duration_seconds = time.time() - start_time

    ss_path = Path(ss_service.screenshots_path)
    screenshots_count = len(list(ss_path.glob("*.png"))) if ss_path.exists() else 0

    console.print("\n")
    print_session_summary_panel(
        session_name=session_name,
        duration_seconds=duration_seconds,
        screenshots_count=screenshots_count,
        commands=shell.entered_commands,
        session_path=str(session_dir),
    )


def define_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="arve - Freelance Time & Activity Tracker",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--record",
        nargs="?",
        const="",
        help="Start recording session. Optionally provide session name, e.g. --record task_1",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=10.0,
        help="Screenshot interval in seconds (default: 10.0)",
    )
    parser.add_argument(
        "--recordings",
        action="store_true",
        help="Open recordings directory in file explorer",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open recordings directory in file explorer",
    )
    return parser


def main() -> None:
    parser = define_parser()
    args = parser.parse_args()

    if args.record is not None:
        print_banner()
        
        from billingsystem.backend.services.supabase_service import SupabaseService
        from billingsystem.backend.services.auth_service import AuthService
        
        try:
            supabase_service = SupabaseService()
            auth_service = AuthService(supabase_service)

            email = input("email: ")
            password = input("password: ")

            user_id = auth_service.login(email=email, password=password)

            #print(user_id)
            
        except Exception as e:
            console.print(f"[bold red]Błąd inicjalizacji Supabase:[/] {e}")
            return
            
        session_name = args.record.strip()
        if not session_name:
            session_name, interval = prompt_session_config()
        else:
            interval = args.interval
        run_recording_session(session_name=session_name, interval=interval)
        return

    if args.recordings or args.open:
        open_recordings_folder()
        return

    from billingsystem.backend.services.supabase_service import SupabaseService
    from billingsystem.backend.services.auth_service import AuthService
    
    try:
        supabase_service = SupabaseService()
        auth_service = AuthService(supabase_service)
        email = input("email: ")
        password = input("password: ")

        user_id = auth_service.login(email=email, password=password)

        #print(user_id)
    except Exception as e:
        console.print(f"[bold red]Błąd inicjalizacji Supabase:[/] {e}")
        return

    while True:
        try:
            console.clear()
        except Exception:
            pass

        print_banner()
        choice = prompt_main_menu()

        if choice == "1":
            session_name, interval = prompt_session_config()
            run_recording_session(session_name=session_name, interval=interval)
            try:
                Prompt.ask("\n[dim]Press Enter to return to the main menu...[/dim]")
            except (EOFError, KeyboardInterrupt):
                break
        elif choice == "2":
            open_recordings_folder()
            try:
                Prompt.ask("\n[dim]Press Enter to return to the main menu...[/dim]")
            except (EOFError, KeyboardInterrupt):
                break
        elif choice == "3":
            console.print("\n[bold cyan]Thank you for using arve. Goodbye![/bold cyan]\n")
            break


if __name__ == "__main__":
    main()