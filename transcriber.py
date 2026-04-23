# =============================================
#  transcriber.py — Transcripción con Whisper
# =============================================
#
#  OpenAI Whisper (open source):
#  https://github.com/openai/whisper
#
#  Modelos disponibles:
#   tiny   (~39 M params)  — muy rápido, menos preciso
#   base   (~74 M params)  — rápido
#   small  (~244 M params) — bueno
#   medium (~769 M params) — muy bueno  ← recomendado
#   large  (~1550 M params)— máxima precisión (necesita GPU o paciencia)
#   large-v2 / large-v3    — mejoras incrementales del large
# =============================================

import os
import logging
import time
from dataclasses import dataclass, field

import whisper
import torch

from config import WHISPER_MODEL, WHISPER_DEVICE, WHISPER_LANGUAGE, SHOW_TIMESTAMPS
from utils import seconds_to_timestamp

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Estructuras de datos
# ------------------------------------------------------------------

@dataclass
class Segment:
    start: float
    end: float
    text: str

@dataclass
class TranscriptionResult:
    full_text: str
    language: str
    segments: list[Segment] = field(default_factory=list)
    duration_seconds: float = 0.0

    def formatted_text(self, with_timestamps: bool = True) -> str:
        """Devuelve el texto formateado, con o sin marcas de tiempo."""
        if not with_timestamps or not self.segments:
            return self.full_text

        lines = []
        for seg in self.segments:
            ts = seconds_to_timestamp(seg.start)
            lines.append(f"[{ts}]  {seg.text.strip()}")
        return "\n".join(lines)


# ------------------------------------------------------------------
# Clase principal de transcripción
# ------------------------------------------------------------------

class Transcriber:
    """
    Carga el modelo Whisper una sola vez y permite transcribir
    múltiples archivos de audio.
    """

    def __init__(self, model_name: str = WHISPER_MODEL, device: str = WHISPER_DEVICE):
        self._device = self._resolve_device(device)
        logger.info(f"Cargando modelo Whisper '{model_name}' en {self._device}…")
        t0 = time.time()
        self._model = whisper.load_model(model_name, device=self._device)
        elapsed = time.time() - t0
        logger.info(f"Modelo cargado en {elapsed:.1f}s")

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def transcribe(self, audio_path: str, language: str | None = WHISPER_LANGUAGE) -> TranscriptionResult:
        """
        Transcribe *audio_path* y devuelve un TranscriptionResult.

        Args:
            audio_path: Ruta al archivo de audio (.mp3, .wav, .m4a, …)
            language:   Código ISO 639-1 ("es", "en", …) o None para auto-detección.

        Raises:
            FileNotFoundError si el archivo no existe.
            RuntimeError      si la transcripción falla.
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Archivo de audio no encontrado: {audio_path}")

        logger.info(f"Transcribiendo: {os.path.basename(audio_path)}")
        logger.info(f"  Idioma: {'automático' if language is None else language}")
        logger.info("  (Esto puede tardar varios minutos dependiendo del modelo y la duración…)")

        options: dict = {
            "task": "transcribe",
            "verbose": False,          # Whisper no imprimirá líneas por segmento
            "condition_on_previous_text": True,   # Mejor coherencia entre segmentos
            "compression_ratio_threshold": 2.4,
            "no_speech_threshold": 0.6,
            "fp16": self._device == "cuda",       # FP16 solo en GPU
        }
        if language:
            options["language"] = language

        t0 = time.time()
        try:
            result = self._model.transcribe(audio_path, **options)
        except Exception as e:
            raise RuntimeError(f"Error durante la transcripción: {e}") from e

        elapsed = time.time() - t0
        logger.info(f"Transcripción completada en {elapsed:.1f}s")

        segments = [
            Segment(start=s["start"], end=s["end"], text=s["text"])
            for s in result.get("segments", [])
        ]

        return TranscriptionResult(
            full_text=result["text"].strip(),
            language=result.get("language", "desconocido"),
            segments=segments,
            duration_seconds=segments[-1].end if segments else 0.0,
        )

    # ------------------------------------------------------------------
    # Métodos internos
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_device(device: str) -> str:
        if device == "auto":
            chosen = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Dispositivo detectado automáticamente: {chosen.upper()}")
            return chosen
        return device


# ------------------------------------------------------------------
# Función de conveniencia
# ------------------------------------------------------------------

_global_transcriber: Transcriber | None = None

def get_transcriber() -> Transcriber:
    """
    Devuelve una instancia global de Transcriber (singleton).
    El modelo solo se carga una vez aunque se llame varias veces.
    """
    global _global_transcriber
    if _global_transcriber is None:
        _global_transcriber = Transcriber()
    return _global_transcriber


def transcribe_audio(audio_path: str, language: str | None = None) -> TranscriptionResult:
    """Atajo rápido para transcribir sin gestionar la instancia."""
    return get_transcriber().transcribe(audio_path, language=language)
