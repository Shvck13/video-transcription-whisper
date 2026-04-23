# =============================================
#  utils.py — Funciones auxiliares
# =============================================

import os
import sys
import shutil
import re
import logging
from datetime import timedelta

from config import AUDIO_DIR, OUTPUT_DIR


# ------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Gestión de directorios
# ------------------------------------------------------------------

def ensure_dirs() -> None:
    """Crea los directorios necesarios si no existen."""
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def cleanup_audio(filepath: str) -> None:
    """Elimina el archivo de audio temporal."""
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Audio temporal eliminado: {filepath}")
    except OSError as e:
        logger.warning(f"No se pudo eliminar {filepath}: {e}")


# ------------------------------------------------------------------
# Validación de URL
# ------------------------------------------------------------------

def validate_url(url: str) -> bool:
    """Comprueba que la cadena tiene pinta de URL válida."""
    pattern = re.compile(
        r"^(https?://)?"           # http o https
        r"([\w\-]+\.)+[\w\-]+"    # dominio
        r"(:\d+)?"                 # puerto opcional
        r"(/[\w\-./?%&=+#]*)?$",  # ruta/query
        re.IGNORECASE,
    )
    return bool(pattern.match(url.strip()))


# ------------------------------------------------------------------
# Formato de timestamps
# ------------------------------------------------------------------

def seconds_to_timestamp(seconds: float) -> str:
    """Convierte segundos a formato HH:MM:SS."""
    td = timedelta(seconds=int(seconds))
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


# ------------------------------------------------------------------
# Guardar transcripción
# ------------------------------------------------------------------

def save_transcription(text: str, video_title: str, with_timestamps: bool = True) -> str:
    """
    Guarda la transcripción en un archivo .txt dentro de OUTPUT_DIR.
    Devuelve la ruta del archivo guardado.
    """
    ensure_dirs()

    # Limpiar caracteres no válidos para nombre de archivo
    safe_title = re.sub(r'[\\/*?:"<>|]', "_", video_title)[:80]
    filename = f"{safe_title}.txt"
    filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"Título: {video_title}\n")
        f.write("=" * 60 + "\n\n")
        f.write(text)

    logger.info(f"Transcripción guardada en: {filepath}")
    return filepath


# ------------------------------------------------------------------
# Verificar dependencias externas
# ------------------------------------------------------------------

def check_ffmpeg() -> bool:
    """Comprueba que ffmpeg está instalado en el sistema."""
    if shutil.which("ffmpeg") is None:
        logger.error(
            "❌  ffmpeg no encontrado. Instálalo con:\n"
            "    • Linux/macOS:  sudo apt install ffmpeg  /  brew install ffmpeg\n"
            "    • Windows:      https://ffmpeg.org/download.html"
        )
        return False
    return True


def check_dependencies() -> bool:
    """Verifica todas las dependencias necesarias."""
    ok = True

    # ffmpeg
    if not check_ffmpeg():
        ok = False

    # Librerías Python
    required = {"yt_dlp": "yt-dlp", "whisper": "openai-whisper"}
    for module, package in required.items():
        try:
            __import__(module)
        except ImportError:
            logger.error(f"❌  Módulo '{module}' no encontrado. Instala con:  pip install {package}")
            ok = False

    return ok
