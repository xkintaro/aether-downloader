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
import deno
import imageio_ffmpeg
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
from rich.console import Group
from rich.constrain import Constrain
from rich.rule import Rule
from rich.table import Table
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

APP_WIDTH = 60

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
            [sys.executable, "-m", "pip", "install", "-U", "yt-dlp[default]"],
            check=True, 
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        console.print(Text("yt-dlp updated successfully or is already up to date.", style="green dim"))
    except Exception as e:
        console.print(Text(f"An error occurred while updating yt-dlp: {e}", style="red dim"))
    time.sleep(1.5)

def get_download_path() -> str:
    path = os.path.join(os.path.expanduser("~"), "Downloads", "aether-downloads")
    os.makedirs(path, exist_ok=True)
    return path


def clear() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')


def generate_filename() -> str:
    return f"{datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]}"

# ═══════════════════════════════════════════════════════════════════════════════
#  UI COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

LOGO_LINES = [
    " █████╗ ███████╗████████╗██╗  ██╗███████╗██████╗ ",
    "██╔══██╗██╔════╝╚══██╔══╝██║  ██║██╔════╝██╔══██╗",
    "███████║█████╗     ██║   ███████║█████╗  ██████╔╝",
    "██╔══██║██╔══╝     ██║   ██╔══██║██╔══╝  ██╔══██╗",
    "██║  ██║███████╗   ██║   ██║  ██║███████╗██║  ██║",
    "╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝",
]


def centered(renderable) -> Constrain:
    return Constrain(Align.center(renderable), width=APP_WIDTH)


def divider(title: str = "") -> Constrain:
    return Constrain(Rule(title, characters="━", style="dim"), width=APP_WIDTH)


def render_header() -> None:
    console.print()
    logo_width = max(len(line) for line in LOGO_LINES)
    logo = "\n".join(line.ljust(logo_width) for line in LOGO_LINES)
    console.print(centered(Text(logo, style="bold bright_magenta")))
    console.print()
    console.print(divider("[dim]terminal media downloader[/dim]"))
    console.print()

    links_table = Table.grid(padding=(0, 3))
    for _ in range(4):
        links_table.add_column(justify="center")

    links_table.add_row(
        f"[dim]github[/dim] [bright_magenta]→[/bright_magenta] [link={SOCIAL_LINKS['github']}]{SOCIAL_LINKS['github'].split('/')[-1]}[/link]",
        f"[dim]repo[/dim] [bright_magenta]→[/bright_magenta] [link={SOCIAL_LINKS['repo']}]source[/link]",
        f"[dim]discord[/dim] [bright_magenta]→[/bright_magenta] [link={SOCIAL_LINKS['discord']}]join[/link]",
        f"[dim]v{APP_VERSION}[/dim]",
    )

    console.print(centered(links_table))
    console.print()
    console.print(divider())
    console.print()


def render_result(heading: Text, lines: list[Text], border_style: str) -> None:
    console.print()
    body = Group(
        Text(""),
        heading,
        Text(""),
        *lines,
        Text(""),
    )
    console.print(Panel(body, box=box.SQUARE, border_style=border_style, width=APP_WIDTH))


def render_success(title: str, details: str, location: str) -> None:
    render_result(
        Text("✓ DOWNLOAD COMPLETE", style="bold white", justify="center"),
        [
            Text(title, style="white", justify="center", no_wrap=True, overflow="ellipsis"),
            Text(details, style="dim", justify="center"),
            Text(""),
            Text(f"saved to {location}", style="dim bright_black", justify="center", overflow="fold"),
        ],
        "bold bright_green",
    )


def render_error(message: str) -> None:
    render_result(
        Text("✗ ERROR", style="bold white", justify="center"),
        [Text(message, style="white", justify="center", overflow="fold")],
        "bold red",
    )


def render_analyzing(url: str) -> None:
    console.print()
    console.print(Text("analyzing", style="dim italic"))
    console.print(Constrain(Text(url, style="bright_white", no_wrap=True, overflow="ellipsis"), width=APP_WIDTH))
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
                self._task_id = self._progress.add_task("connecting", total=None)

            downloaded = data.get('downloaded_bytes', 0)
            total = data.get('total_bytes') or data.get('total_bytes_estimate', 0)

            if total > 0:
                info = data.get('info_dict') or {}
                description = "downloading audio" if info.get('vcodec') == 'none' else "downloading video"
                self._progress.update(self._task_id, description=description, total=total, completed=downloaded)

        elif status == 'finished':
            if self._progress:
                task = self._progress.tasks[0]
                self._progress.update(self._task_id, completed=task.total or task.completed)
                self._progress.stop()
                self._progress = None

    def _postprocessor_hook(self, data: dict) -> None:
        if data.get('status') == 'started' and data.get('postprocessor') == 'Merger':
            console.print(Text("merging video and audio...", style="dim italic"))

    def _cleanup_progress(self) -> None:
        if self._progress:
            self._progress.stop()
            self._progress = None

    def download_video(self, url: str) -> bool:
        filename = generate_filename()
        
        opts = {
            'format': 'bv*+ba/b',
            'format_sort': ['res', 'vcodec:h264', 'acodec:m4a'],
            'js_runtimes': {'deno': {'path': deno.find_deno_bin()}},
            'ffmpeg_location': imageio_ffmpeg.get_ffmpeg_exe(),
            'outtmpl': f'{self.download_path}/{filename}.%(ext)s',
            'progress_hooks': [self._progress_hook],
            'postprocessor_hooks': [self._postprocessor_hook],
            'quiet': True,
            'noprogress': True,
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