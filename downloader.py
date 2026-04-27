# =============================================
#  downloader.py — Audio download via yt-dlp
# =============================================
#  Supports YouTube, Vimeo, Twitter/X, TikTok,
#  Instagram, Facebook, Twitch, SoundCloud and
#  1,000+ more sites.
# =============================================

import os
import logging

import yt_dlp

from config import AUDIO_DIR, AUDIO_FORMAT, AUDIO_CODEC, AUDIO_QUALITY
from utils import ensure_dirs

logger = logging.getLogger(__name__)


class AudioDownloader:
    """Downloads audio from a video URL using yt-dlp."""

    def __init__(self):
        ensure_dirs()
        self._title: str = "video"

    def download(self, url: str) -> tuple[str, str]:
        """
        Downloads audio from *url* and saves it to AUDIO_DIR.

        Returns:
            (filepath, title)

        Raises:
            RuntimeError if the download fails.
        """
        url = url.strip()
        logger.info(f"Starting download: {url}")

        ydl_opts = {
            "format": AUDIO_FORMAT,
            "outtmpl": os.path.join(AUDIO_DIR, "%(title)s.%(ext)s"),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": AUDIO_CODEC,
                "preferredquality": AUDIO_QUALITY,
            }],
            # Pretend to be an Android client — YouTube blocks requests otherwise
            "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
            "progress_hooks": [self._progress_hook],
            "retries": 10,
            "fragment_retries": 10,
            "ignoreerrors": False,
            "nooverwrites": False,
            "quiet": True,
            "no_warnings": False,
            "writethumbnail": False,
            "writeinfojson": False,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                self._title = info.get("title", "video")
        except yt_dlp.utils.DownloadError as e:
            raise RuntimeError(f"Download error: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected error during download: {e}") from e

        filepath = self._find_audio_file(self._title)
        logger.info(f"Audio saved: {filepath}")
        return filepath, self._title

    def _progress_hook(self, d: dict) -> None:
        # Print progress in-place so it doesn't spam the terminal
        status = d.get("status")
        if status == "downloading":
            percent = d.get("_percent_str", "?").strip()
            speed   = d.get("_speed_str", "?").strip()
            eta     = d.get("_eta_str", "?").strip()
            print(f"\r  ⬇  Downloading: {percent}  |  Speed: {speed}  |  ETA: {eta}   ", end="", flush=True)
        elif status == "finished":
            print()
            logger.info("Download complete. Processing audio…")
        elif status == "error":
            print()
            logger.error("Error during download.")

    def _find_audio_file(self, title: str) -> str:
        # yt-dlp can mangle filenames, so instead of guessing we just grab
        # the most recently modified file with the right extension
        candidates = [f for f in os.listdir(AUDIO_DIR) if f.endswith(f".{AUDIO_CODEC}")]
        if not candidates:
            raise RuntimeError(f"No .{AUDIO_CODEC} file found in {AUDIO_DIR}")
        candidates.sort(key=lambda f: os.path.getmtime(os.path.join(AUDIO_DIR, f)), reverse=True)
        return os.path.join(AUDIO_DIR, candidates[0])


def download_audio(url: str) -> tuple[str, str]:
    """Shortcut to download audio without managing the class instance."""
    return AudioDownloader().download(url)
