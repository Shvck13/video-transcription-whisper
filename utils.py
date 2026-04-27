# =============================================
#  utils.py — Helper functions
# =============================================

import os
import sys
import shutil
import re
import logging
from datetime import timedelta

from config import AUDIO_DIR, OUTPUT_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)


def ensure_dirs() -> None:
    """Creates required directories if they don't exist."""
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def cleanup_audio(filepath: str) -> None:
    """Deletes a temporary audio file."""
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Temp audio deleted: {filepath}")
    except OSError as e:
        # Not critical, just warn and move on
        logger.warning(f"Could not delete {filepath}: {e}")


def validate_url(url: str) -> bool:
    """Checks whether the string looks like a valid URL."""
    pattern = re.compile(
        r"^(https?://)?([\w\-]+\.)+[\w\-]+(:\d+)?(/[\w\-./?%&=+#]*)?$",
        re.IGNORECASE,
    )
    return bool(pattern.match(url.strip()))


def seconds_to_timestamp(seconds: float) -> str:
    """Converts seconds to HH:MM:SS format."""
    total = int(seconds)
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def save_transcription(text: str, video_title: str, with_timestamps: bool = True) -> str:
    """Saves the transcription as a .txt file in OUTPUT_DIR. Returns the file path."""
    ensure_dirs()

    # Strip characters that would break the filename on any OS
    safe_title = re.sub(r'[\\/*?:"<>|]', "_", video_title)[:80]
    filepath = os.path.join(OUTPUT_DIR, f"{safe_title}.txt")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"Title: {video_title}\n")
        f.write("=" * 60 + "\n\n")
        f.write(text)

    logger.info(f"Transcription saved: {filepath}")
    return filepath


def check_ffmpeg() -> bool:
    """Checks whether ffmpeg is installed."""
    if shutil.which("ffmpeg") is None:
        logger.error(
            "❌  ffmpeg not found. Install it with:\n"
            "    • Linux/macOS:  sudo apt install ffmpeg  /  brew install ffmpeg\n"
            "    • Windows:      https://ffmpeg.org/download.html"
        )
        return False
    return True


def check_dependencies() -> bool:
    """Verifies all required dependencies are available before doing anything."""
    ok = check_ffmpeg()
    for module, package in {"yt_dlp": "yt-dlp", "whisper": "openai-whisper"}.items():
        try:
            __import__(module)
        except ImportError:
            logger.error(f"❌  Module '{module}' not found. Install with:  pip install {package}")
            ok = False
    return ok
