"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                              AETHER DOWNLOADER                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import sys
import os
import time
import subprocess
from datetime import datetime
from yt_dlp import YoutubeDL
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    Progress, 
    SpinnerColumn, 
    TextColumn, 
    BarColumn, 
    DownloadColumn, 
    TransferSpeedColumn, 
    TimeRemainingColumn
)
from rich.text import Text
from rich.align import Align
from rich.table import Table
from rich.columns import Columns
from rich import box
import questionary
from questionary import Style

# ═══════════════════════════════════════════════════════════════════════════════
#  CONFIGURATION — Edit these values
# ═══════════════════════════════════════════════════════════════════════════════

SOCIAL_LINKS = {
    "github": "https://github.com/xkintaro",
    "repo": "https://github.com/xkintaro/aether-downloader",
    "discord": "https://discord.gg/NSQk27Zdkv",
}

APP_VERSION = "1.0.0"

# ═══════════════════════════════════════════════════════════════════════════════
#  CONSOLE & STYLING
# ═══════════════════════════════════════════════════════════════════════════════

console = Console()

AETHER_STYLE = Style([
    ('qmark', 'fg:#ff79c6 bold'),
    ('question', 'fg:#f8f8f2 bold'),
    ('answer', 'fg:#50fa7b bold'),
    ('pointer', 'fg:#ff79c6 bold'),
    ('highlighted', 'fg:#191a21 bg:#ff79c6 bold'),
    ('selected', 'fg:#50fa7b'),
    ('separator', 'fg:#6272a4'),
    ('instruction', 'fg:#6272a4'),
    ('text', 'fg:#f8f8f2'),
])

# ═══════════════════════════════════════════════════════════════════════════════
#  UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def update_ytdlp() -> None:
    console.print(Text("Updating yt-dlp, please wait...", style="dim italic"))
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-U", "yt-dlp"], 
            check=True, 
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        console.print(Text("yt-dlp updated successfully or is already up to date.", style="green dim"))
    except Exception as e:
        console.print(Text(f"An error occurred while updating yt-dlp: {e}", style="red dim"))
    time.sleep(1.5)

def resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def get_download_path() -> str:
    path = os.path.join(os.path.expanduser("~"), "Downloads", "aether-downloader")
    os.makedirs(path, exist_ok=True)
    return path


def clear() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')


def generate_filename() -> str:
    return f"{datetime.now().strftime('%d%m%Y%H%M%S%f')[:-3]}"

# ═══════════════════════════════════════════════════════════════════════════════
#  UI COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

LOGO_ART = """[bold bright_magenta]
     █████╗ ███████╗████████╗██╗  ██╗███████╗██████╗ 
    ██╔══██╗██╔════╝╚══██╔══╝██║  ██║██╔════╝██╔══██╗
    ███████║█████╗     ██║   ███████║█████╗  ██████╔╝
    ██╔══██║██╔══╝     ██║   ██╔══██║██╔══╝  ██╔══██╗
    ██║  ██║███████╗   ██║   ██║  ██║███████╗██║  ██║
    ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝[/bold bright_magenta]"""


def render_header() -> None:
    console.print(LOGO_ART)
    console.print()
    
    console.print(
        Text("━━━━━━━━━━━━━━━━ terminal media downloader ━━━━━━━━━━━━━━━━━", style="dim")
    )
    console.print()
    
    links_table = Table.grid(padding=(0, 3))
    links_table.add_column(justify="center")
    links_table.add_column(justify="center")
    links_table.add_column(justify="center")
    links_table.add_column(justify="center")
    
    links_table.add_row(
        f"[dim]github[/dim] [bright_magenta]→[/bright_magenta] [link={SOCIAL_LINKS['github']}]{SOCIAL_LINKS['github'].split('/')[-1]}[/link]",
        f"[dim]repo[/dim] [bright_magenta]→[/bright_magenta] [link={SOCIAL_LINKS['repo']}]source[/link]",
        f"[dim]discord[/dim] [bright_magenta]→[/bright_magenta] [link={SOCIAL_LINKS['discord']}]join[/link]",
        f"[dim]v{APP_VERSION}[/dim]",
    )
    
    console.print(links_table)
    console.print()
    console.print(Text("━" * 60, style="dim"))
    console.print()


def render_success(title: str, details: str, location: str) -> None:
    console.print()
    
    inner_content = Table.grid(padding=(0, 0))
    inner_content.add_column(justify="center")
    inner_content.add_row("")
    inner_content.add_row("[bold bright_green]┌────────────────────────────────────────┐[/bold bright_green]")
    inner_content.add_row("[bold bright_green]│[/bold bright_green]         [bold white]✓ DOWNLOAD COMPLETE[/bold white]         [bold bright_green]│[/bold bright_green]")
    inner_content.add_row("[bold bright_green]└────────────────────────────────────────┘[/bold bright_green]")
    inner_content.add_row("")
    inner_content.add_row(f"[white]{title[:50]}{'...' if len(title) > 50 else ''}[/white]")
    inner_content.add_row(f"[dim]{details}[/dim]")
    inner_content.add_row("")
    inner_content.add_row(f"[dim bright_black]saved to {location}[/dim bright_black]")
    inner_content.add_row("")
    
    console.print(inner_content)


def render_error(message: str) -> None:
    console.print()
    
    error_content = Table.grid(padding=(0, 0))
    error_content.add_column(justify="center")
    error_content.add_row("")
    error_content.add_row("[bold red]┌────────────────────────────────────────┐[/bold red]")
    error_content.add_row("[bold red]│[/bold red]             [bold white]✗ ERROR[/bold white]                  [bold red]│[/bold red]")
    error_content.add_row("[bold red]└────────────────────────────────────────┘[/bold red]")
    error_content.add_row("")
    error_content.add_row(f"[white]{message[:60]}[/white]")
    error_content.add_row("")
    
    console.print(error_content)


def render_analyzing(url: str) -> None:
    console.print()
    console.print(Text("analyzing", style="dim italic"))
    console.print(Text(url[:60] + ('...' if len(url) > 60 else ''), style="bright_white"))
    console.print()

# ═══════════════════════════════════════════════════════════════════════════════
#  DOWNLOADER CORE
# ═══════════════════════════════════════════════════════════════════════════════

class Aether:    
    def __init__(self):
        self.download_path = get_download_path()
        self._progress: Progress | None = None
        self._task_id: int | None = None

    def _progress_hook(self, data: dict) -> None:
        status = data.get('status')
        
        if status == 'downloading':
            if self._progress is None:
                self._progress = Progress(
                    SpinnerColumn(style="bright_magenta"),
                    TextColumn("[white]{task.description}[/white]"),
                    BarColumn(bar_width=30, complete_style="bright_magenta", finished_style="bright_green"),
                    TextColumn("[bright_magenta]{task.percentage:>3.0f}%[/bright_magenta]"),
                    DownloadColumn(),
                    TransferSpeedColumn(),
                    TimeRemainingColumn(),
                    console=console
                )
                self._progress.start()
                self._task_id = self._progress.add_task("connecting", total=100)

            downloaded = data.get('downloaded_bytes', 0)
            total = data.get('total_bytes') or data.get('total_bytes_estimate', 0)
            
            if total > 0:
                pct = (downloaded / total) * 100
                self._progress.update(self._task_id, description="downloading", completed=pct)

        elif status == 'finished':
            if self._progress:
                self._progress.update(self._task_id, description="processing", completed=100)
                self._progress.stop()
                self._progress = None

    def _cleanup_progress(self) -> None:
        if self._progress:
            self._progress.stop()
            self._progress = None

    def download_video(self, url: str) -> bool:
        filename = generate_filename()
        
        opts = {
            'format': 'best',
            'outtmpl': f'{self.download_path}/{filename}.%(ext)s',
            'progress_hooks': [self._progress_hook],
            'quiet': True,
            'no_warnings': True,
            'restrictfilenames': True,
            'merge_output_format': 'mp4',
            'nocheckcertificate': True,
            'http_headers': {
                'referer': 'google.com',
                'Accept-Language': 'en-US,en;q=0.9',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            },
        }

        try:
            render_analyzing(url)
            
            with YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Unknown')
                render_success(title, "Video • Best Quality", self.download_path)
                return True
                
        except Exception as e:
            self._cleanup_progress()
            render_error(str(e))
            return False

# ═══════════════════════════════════════════════════════════════════════════════
#  INTERACTIVE MENUS
# ═══════════════════════════════════════════════════════════════════════════════

def prompt_url() -> str | None:
    console.print()
    return questionary.text(
        "paste url",
        style=AETHER_STYLE,
        qmark="  →"
    ).ask()


def prompt_continue() -> None:
    console.print()
    questionary.press_any_key_to_continue(
        message="press any key to continue...",
        style=AETHER_STYLE
    ).ask()

# ═══════════════════════════════════════════════════════════════════════════════
#  APPLICATION FLOW
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    clear()
    render_header()
    update_ytdlp()
    
    app = Aether()
    
    while True:
        clear()
        render_header()
        
        url = prompt_url()
        
        if url is None or url.strip().lower() in ['exit', 'q', 'quit']:
            console.print()
            console.print(Text("goodbye.", style="dim italic"))
            console.print()
            time.sleep(0.4)
            break
            
        if not url.strip():
            continue
            
        console.print()
        app.download_video(url.strip())
        prompt_continue()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n") 
        console.print(Text("interrupted", style="dim"))
        console.print()
        sys.exit(0)