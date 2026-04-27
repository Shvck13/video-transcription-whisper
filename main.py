#!/usr/bin/env python3
# =============================================
#  main.py — Entry point
# =============================================
#  Usage:
#    python main.py                      ← interactive mode
#    python main.py <URL>                ← direct URL
#    python main.py <URL> --lang es      ← force language
#    python main.py <URL> --model large  ← use large model
#    python main.py <URL> --no-save      ← skip .txt output
# =============================================

import sys
import argparse
import logging

from utils import validate_url, ensure_dirs, cleanup_audio, save_transcription, check_dependencies
from downloader import download_audio
from transcriber import transcribe_audio
from config import WHISPER_MODEL, SHOW_TIMESTAMPS, SAVE_TXT, WHISPER_LANGUAGE

logger = logging.getLogger(__name__)

BANNER = r"""
╔═════════════════════════════════════════════════════╗
║             VIDEO  →  TRANSCRIPTION                 ║
║  By: Sergio Vidal    ///   Work in Progress         ║
╚═════════════════════════════════════════════════════╝
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transcribe audio from any online video to text.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("url", nargs="?", default=None, help="Video URL (YouTube, Vimeo, TikTok, Twitter/X, etc.)")
    parser.add_argument("--lang", default=None, metavar="CODE", help="Audio language (e.g. es, en, fr). Default: auto-detect.")
    parser.add_argument("--model", default=WHISPER_MODEL, choices=["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"], help=f"Whisper model to use (default: {WHISPER_MODEL}).")
    parser.add_argument("--no-timestamps", action="store_true", help="Omit timestamps from output.")
    parser.add_argument("--no-save", action="store_true", help="Don't save the transcription as a .txt file.")
    parser.add_argument("--keep-audio", action="store_true", help="Keep the temporary audio file after transcription.")
    return parser.parse_args()


def main() -> None:
    print(BANNER)

    if not check_dependencies():
        sys.exit(1)

    args = parse_args()

    # If no URL was passed as an argument, ask for it interactively
    url = args.url or input("Enter video URL: ").strip()
    if not validate_url(url):
        logger.error(f"Invalid URL: '{url}'")
        sys.exit(1)

    ensure_dirs()
    audio_path = None

    try:
        print("\n Downloading audio…")
        audio_path, title = download_audio(url)
        print(f"  Ready: {title}\n")

        # This is the slow part — model size and video length both matter
        print(" Transcribing (this may take a while depending on video length)…\n")
        result = transcribe_audio(audio_path, language=args.lang or WHISPER_LANGUAGE)

        with_ts = not args.no_timestamps and SHOW_TIMESTAMPS
        formatted = result.formatted_text(with_timestamps=with_ts)

        print("\n" + "═" * 60)
        print(f"  Language : {result.language.upper()}")
        print(f"  Duration : {int(result.duration_seconds // 60)}m {int(result.duration_seconds % 60)}s")
        print(f"  Segments : {len(result.segments)}")
        print("═" * 60 + "\n")
        print(formatted)
        print("\n" + "═" * 60)

        if not args.no_save and SAVE_TXT:
            saved_path = save_transcription(formatted, title, with_timestamps=with_ts)
            print(f"\n Transcription saved to: {saved_path}")

    except KeyboardInterrupt:
        print("\n\n Operation cancelled.")
        sys.exit(0)
    except (FileNotFoundError, RuntimeError) as e:
        logger.error(str(e))
        sys.exit(1)
    finally:
        # Always clean up the temp audio unless the user explicitly asked to keep it
        if audio_path and not (args.keep_audio if args else False):
            cleanup_audio(audio_path)

    print("\n  Done!\n")


if __name__ == "__main__":
    main()
