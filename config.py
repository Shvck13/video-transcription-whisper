# =============================================
#  config.py — Configuración global
# =============================================

import os

# ------------------------------------------------------------------
# Directorios
# ------------------------------------------------------------------
BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR       = os.path.join(BASE_DIR, "temp_audio")
OUTPUT_DIR      = os.path.join(BASE_DIR, "transcriptions")

# ------------------------------------------------------------------
# Whisper
# ------------------------------------------------------------------
# Modelos disponibles (de menos a más preciso / lento):
#   tiny | base | small | medium | large | large-v2 | large-v3
WHISPER_MODEL   = "medium"          # Buen equilibrio calidad/velocidad
WHISPER_DEVICE  = "auto"            # "auto" detecta CUDA si está disponible
WHISPER_LANGUAGE = None             # None = detección automática | "es" = español forzado

# ------------------------------------------------------------------
# yt-dlp
# ------------------------------------------------------------------
AUDIO_FORMAT    = "bestaudio/best"  # Mejor calidad de audio disponible
AUDIO_CODEC     = "mp3"             # Formato final tras conversión
AUDIO_QUALITY   = "192"             # kbps

# ------------------------------------------------------------------
# Salida
# ------------------------------------------------------------------
SAVE_TXT        = True              # Guardar transcripción en .txt
SHOW_TIMESTAMPS = True              # Incluir marcas de tiempo en la salida
