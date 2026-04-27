# =============================================
#  config.py — Global settings
# =============================================

import os

# Directories
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR  = os.path.join(BASE_DIR, "temp_audio")
OUTPUT_DIR = os.path.join(BASE_DIR, "transcriptions")

# Whisper — available models: tiny | base | small | medium | large | large-v2 | large-v3
WHISPER_MODEL    = "medium"   # Best quality/speed balance
WHISPER_DEVICE   = "auto"     # "auto" detects CUDA if available
WHISPER_LANGUAGE = None       # None = auto-detect | "es" = force Spanish

# yt-dlp
AUDIO_FORMAT  = "bestaudio/best"
AUDIO_CODEC   = "mp3"
AUDIO_QUALITY = "192"         # kbps

# Output
SAVE_TXT        = True        # Save transcription as .txt
SHOW_TIMESTAMPS = True        # Include timestamps in output
