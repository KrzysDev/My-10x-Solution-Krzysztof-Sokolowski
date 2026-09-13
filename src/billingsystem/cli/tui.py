import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Necessary for Windows console to handle UTF-8 symbols and emojis without cp1250 encoding errors
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8", errors="replace")

from rich import box
from rich.align import Align
from rich.console import Console as RichConsole
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.table import Table
from rich.text import Text

console = RichConsole(legacy_windows=False)


def get_recordings_dir() -> Path:
    p_current = Path("./recordings").resolve()
    p_parent = Path("../recordings").resolve()
    if p_current.exists():
        return p_current
    if p_parent.exists():
        return p_parent
    return p_current


def get_header_panel() -> Panel:
    header_text = Text()
    header_text.append("⚡ arve", style="bold cyan")
    header_text.append("  •  ", style="dim")
    header_text.append("freelance activity & billing tracker", style="italic bright_white")
    return Panel(
        Align.center(header_text),
        box=box.ROUNDED,
        border_style="cyan",
        padding=(0, 1),
    )


def print_banner() -> None:
    console.print(get_header_panel())


def print_session_start_panel(session_name: str, interval: float, session_path: str) -> None:
    table = Table(box=None, show_header=False, pad_edge=False)
    table.add_column("Key", style="bold cyan", width=22)
    table.add_column("Value", style="bold white")

    table.add_row("🟢 Session Status:", "[bold green]ACTIVE (RECORDING)[/]")
    table.add_row("🏷️  Session Name:", f"[bold yellow]{session_name}[/]")
    table.add_row("⏱️  Screenshot Interval:", f"[bold magenta]{interval} s[/]")
    table.add_row("📁 Save Directory:", f"[underline blue]{session_path}[/]")
    table.add_row("🕒 Start Time:", f"[white]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/]")

    instructions = (
        "\n[bold bright_white]Tips:[/]\n"
        " • Enter commands as in a normal shell.\n"
        " • Commands and periodic screenshots are automatically recorded in the background.\n"
        " • To finish recording, enter: [bold yellow]stop recording[/] or press [bold red]Ctrl+C[/]."
    )

    content = Table(box=None, show_header=False, pad_edge=False)
    content.add_row(table)
    content.add_row(Text.from_markup(instructions))

    panel = Panel(
        content,
        title="[bold green]● Session Started[/bold green]",
        subtitle="[dim]arve[/dim]",
        box=box.ROUNDED,
        border_style="green",
        padding=(1, 2),
    )
    console.print(panel)


def format_duration(seconds: float) -> str:
    seconds = max(0, int(seconds))
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}h {minutes:02d}m {secs:02d}s"
    return f"{minutes:02d}m {secs:02d}s"


def print_session_summary_panel(
    session_name: str,
    duration_seconds: float,
    screenshots_count: int,
    commands: List[Dict[str, Any]],
    session_path: str,
) -> None:
    summary_table = Table(box=None, show_header=False, pad_edge=False)
    summary_table.add_column("Property", style="bold cyan", width=24)
    summary_table.add_column("Value", style="bold white")

    summary_table.add_row("🏁 Status:", "[bold red]COMPLETED[/]")
    summary_table.add_row("🏷️  Session:", f"[bold yellow]{session_name}[/]")
    summary_table.add_row("⏱️  Duration:", f"[bold bright_green]{format_duration(duration_seconds)}[/]")
    summary_table.add_row("📸 Screenshots:", f"[bold magenta]{screenshots_count}[/] saved files")
    summary_table.add_row("⌨️  Logged Commands:", f"[bold cyan]{len(commands)}[/]")
    summary_table.add_row("📁 Archive Path:", f"[underline blue]{session_path}[/]")

    renderables = [summary_table]

    if commands:
        cmd_table = Table(
            title="[bold yellow]Recently Logged Commands[/bold yellow]",
            box=box.SIMPLE_HEAD,
            header_style="bold cyan",
            show_edge=False,
        )
        cmd_table.add_column("#", style="dim", width=4)
        cmd_table.add_column("Time", style="green", width=12)
        cmd_table.add_column("Command", style="bold white")

        displayed_cmds = commands[-10:]
        offset = len(commands) - len(displayed_cmds)
        for i, cmd_info in enumerate(displayed_cmds, start=offset + 1):
            ts = cmd_info.get("timestamp", "")
            time_part = ts.split("T")[1][:8] if "T" in ts else ts[:8]
            cmd_table.add_row(str(i), time_part, cmd_info.get("command", ""))

        renderables.append(Text("\n"))
        renderables.append(cmd_table)

    summary_content = Table(box=None, show_header=False, pad_edge=False)
    for r in renderables:
        summary_content.add_row(r)

    panel = Panel(
        summary_content,
        title="[bold green]✓ Session Summary[/bold green]",
        subtitle="[bold dim]All session data was saved successfully[/bold dim]",
        box=box.ROUNDED,
        border_style="green",
        padding=(1, 2),
    )
    console.print(panel)


def prompt_main_menu() -> str:
    menu_table = Table(box=box.ROUNDED, border_style="cyan", show_header=False, expand=True)
    menu_table.add_column("Option", style="bold yellow", width=6, justify="center")
    menu_table.add_column("Description", style="bold white")

    menu_table.add_row("[1]", "🚀 Start new recording session")
    menu_table.add_row("[2]", "📂 Open recordings folder in file explorer")
    menu_table.add_row("[3]", "❌ Exit")

    panel = Panel(
        menu_table,
        title="[bold bright_white]MAIN MENU[/bold bright_white]",
        border_style="bright_blue",
        box=box.ROUNDED,
        padding=(0, 1),
    )
    console.print(panel)

    choice = Prompt.ask(
        "[bold cyan]Select option[/bold cyan]",
        choices=["1", "2", "3"],
        default="1",
    )
    return choice


def prompt_session_config() -> tuple[str, float]:
    default_name = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    session_name = Prompt.ask(
        "[bold cyan]Session name[/bold cyan]",
        default=default_name,
    ).strip()

    if not session_name:
        session_name = default_name

    interval = IntPrompt.ask(
        "[bold cyan]Screenshot interval in seconds[/bold cyan]",
        default=10,
    )

    return session_name, float(interval)
