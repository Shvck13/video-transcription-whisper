#!/usr/bin/env python3
# =============================================
#  main.py — Punto de entrada principal
# =============================================
#
#  Uso:
#    python main.py                      ← modo interactivo (pide URL)
#    python main.py <URL>                ← URL directa como argumento
#    python main.py <URL> --lang es      ← forzar idioma español
#    python main.py <URL> --model large  ← usar modelo grande
#    python main.py <URL> --no-save      ← no guardar el .txt
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
║           ¡  VIDEO  →  TRANSCRIPCIÓN  !             ║
║  By: Sergio Vidal    ///   Proyecto en Desarrollo   ║
╚═════════════════════════════════════════════════════╝
"""


# ------------------------------------------------------------------
# Argumentos CLI
# ------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transcribe el audio de cualquier vídeo online a texto.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "url",
        nargs="?",
        default=None,
        help="URL del vídeo (YouTube, Vimeo, TikTok, Twitter/X, etc.)",
    )
    parser.add_argument(
        "--lang",
        default=None,
        metavar="CODIGO",
        help="Idioma del audio (ej: es, en, fr). Por defecto: detección automática.",
    )
    parser.add_argument(
        "--model",
        default=WHISPER_MODEL,
        choices=["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"],
        help=f"Modelo Whisper a usar (por defecto: {WHISPER_MODEL}).",
    )
    parser.add_argument(
        "--no-timestamps",
        action="store_true",
        help="Omitir marcas de tiempo en la salida.",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="No guardar la transcripción en archivo .txt.",
    )
    parser.add_argument(
        "--keep-audio",
        action="store_true",
        help="No eliminar el archivo de audio temporal tras la transcripción.",
    )
    return parser.parse_args()


# ------------------------------------------------------------------
# Flujo principal
# ------------------------------------------------------------------

def main() -> None:
    print(BANNER)

    # 1. Verificar dependencias
    if not check_dependencies():
        sys.exit(1)

    # 2. Parsear argumentos
    args = parse_args()

    # 3. Obtener URL
    url = args.url
    if not url:
        url = input("Introduce la URL del vídeo: ").strip()

    if not validate_url(url):
        logger.error(f"URL no válida: '{url}'")
        sys.exit(1)

    # 4. Crear directorios necesarios
    ensure_dirs()

    # 5. Descargar audio
    audio_path = None
    try:
        print("\n...Descargando audio...")
        audio_path, title = download_audio(url)
        print(f"  Audio listo: {title}\n")

        # 6. Transcribir
        print(" Transcribiendo (esto puede tardar según la duración del vídeo)…\n")
        result = transcribe_audio(
            audio_path,
            language=args.lang or WHISPER_LANGUAGE,
        )

        # 7. Mostrar resultado
        with_ts = not args.no_timestamps and SHOW_TIMESTAMPS
        formatted = result.formatted_text(with_timestamps=with_ts)

        print("\n" + "═" * 60)
        print(f"  Idioma detectado : {result.language.upper()}")
        print(f"  Duración         : {int(result.duration_seconds // 60)}m {int(result.duration_seconds % 60)}s")
        print(f"  Segmentos        : {len(result.segments)}")
        print("═" * 60 + "\n")
        print(formatted)
        print("\n" + "═" * 60)

        # 8. Guardar en archivo
        if not args.no_save and SAVE_TXT:
            saved_path = save_transcription(formatted, title, with_timestamps=with_ts)
            print(f"\n Transcripción guardada en: {saved_path}")

    except KeyboardInterrupt:
        print("\n\n Operación cancelada por el usuario.")
        sys.exit(0)
    except (FileNotFoundError, RuntimeError) as e:
        logger.error(str(e))
        sys.exit(1)
    finally:
        # 9. Limpiar audio temporal (a menos que el usuario lo pida)
        if audio_path and not (args.keep_audio if args else False):
            cleanup_audio(audio_path)

    print("\n  ¡Listo!\n")


# ------------------------------------------------------------------
# Entrada
# ------------------------------------------------------------------

if __name__ == "__main__":
    main()
