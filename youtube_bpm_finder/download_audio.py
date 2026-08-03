"""
Download audio from a YouTube playlist as MP3.

Usage:
    python download_audio.py <youtube_playlist_url>

Output lands in data/audio/ — point your DJ software at that folder.
"""

import logging
import sys
from pathlib import Path

import yt_dlp

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

AUDIO_DIR = Path(__file__).parent / "data" / "audio"


def download_playlist_audio(playlist_url: str):
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "outtmpl": str(AUDIO_DIR / "%(title)s.%(ext)s"),
        "nooverwrites": True,  # skip already-downloaded files
    }

    logger.info(f"Downloading: {playlist_url}")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([playlist_url])

    files = list(AUDIO_DIR.glob("*.mp3"))
    logger.info(f"{len(files)} MP3s in {AUDIO_DIR}")
    print(f"\nDone. Load this folder into your DJ software:\n  {AUDIO_DIR.resolve()}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    download_playlist_audio(sys.argv[1])
