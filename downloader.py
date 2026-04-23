# =============================================
#  downloader.py — Descarga de audio con yt-dlp
# =============================================
#
#  Soporta: YouTube, Vimeo, Twitter/X, TikTok,
#           Instagram, Facebook, Twitch, SoundCloud
#           y +1 000 sitios más (lista completa en
#           https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)
# =============================================

import os
import re
import logging

import yt_dlp

from config import AUDIO_DIR, AUDIO_FORMAT, AUDIO_CODEC, AUDIO_QUALITY
from utils import ensure_dirs

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Clase principal de descarga
# ------------------------------------------------------------------

class AudioDownloader:
    """Descarga el audio de un vídeo usando yt-dlp."""

    def __init__(self):
        ensure_dirs()
        self._title: str = "video"

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def download(self, url: str) -> tuple[str, str]:
        """
        Descarga el audio de *url* y lo guarda en AUDIO_DIR.

        Returns:
            (filepath, title)  — ruta del archivo de audio y título del vídeo.

        Raises:
            RuntimeError si la descarga falla.
        """
        url = url.strip()
        logger.info(f"Iniciando descarga de: {url}")

        output_template = os.path.join(AUDIO_DIR, "%(title)s.%(ext)s")

        ydl_opts = {
            "format": AUDIO_FORMAT,
            "outtmpl": output_template,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": AUDIO_CODEC,
                    "preferredquality": AUDIO_QUALITY,
                }
            ],
            # Identificarse como cliente Android para evitar bloqueos de YouTube
            "extractor_args": {
                "youtube": {
                    "player_client": ["android", "web"],
                }
            },
            # Callbacks
            "progress_hooks": [self._progress_hook],
            # Opciones de red y robustez
            "retries": 10,
            "fragment_retries": 10,
            "ignoreerrors": False,
            "nooverwrites": False,
            # Silenciar la salida interna de yt-dlp (usamos nuestro logger)
            "quiet": True,
            "no_warnings": False,
            # Extraer información antes de descargar para obtener el título
            "writethumbnail": False,
            "writeinfojson": False,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                self._title = info.get("title", "video")
        except yt_dlp.utils.DownloadError as e:
            raise RuntimeError(f"Error al descargar el vídeo: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Error inesperado durante la descarga: {e}") from e

        filepath = self._find_audio_file(self._title)
        logger.info(f"Audio descargado: {filepath}")
        return filepath, self._title

    # ------------------------------------------------------------------
    # Métodos internos
    # ------------------------------------------------------------------

    def _progress_hook(self, d: dict) -> None:
        """Muestra el progreso de la descarga."""
        status = d.get("status")
        if status == "downloading":
            percent = d.get("_percent_str", "?").strip()
            speed   = d.get("_speed_str", "?").strip()
            eta     = d.get("_eta_str", "?").strip()
            print(f"\r  ⬇  Descargando: {percent}  |  Velocidad: {speed}  |  ETA: {eta}   ", end="", flush=True)
        elif status == "finished":
            print()  # salto de línea tras la barra de progreso
            logger.info("Descarga completada. Procesando audio…")
        elif status == "error":
            print()
            logger.error("Error durante la descarga.")

    def _find_audio_file(self, title: str) -> str:
        """
        Busca el archivo de audio generado en AUDIO_DIR.
        yt-dlp puede añadir caracteres especiales al nombre, así que
        buscamos por extensión y tomamos el más reciente.
        """
        candidates = [
            f for f in os.listdir(AUDIO_DIR)
            if f.endswith(f".{AUDIO_CODEC}")
        ]
        if not candidates:
            raise RuntimeError(
                f"No se encontró ningún archivo .{AUDIO_CODEC} en {AUDIO_DIR}"
            )
        # El más recientemente modificado
        candidates.sort(
            key=lambda f: os.path.getmtime(os.path.join(AUDIO_DIR, f)),
            reverse=True,
        )
        return os.path.join(AUDIO_DIR, candidates[0])


# ------------------------------------------------------------------
# Función de conveniencia
# ------------------------------------------------------------------

def download_audio(url: str) -> tuple[str, str]:
    """Atajo para descargar audio sin instanciar la clase manualmente."""
    return AudioDownloader().download(url)
