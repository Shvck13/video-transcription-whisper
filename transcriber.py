# =============================================
#  transcriber.py — Transcription via Whisper
# =============================================
#  Available models:
#   tiny   (~39M)  — fastest, less accurate
#   base   (~74M)  — fast
#   small  (~244M) — good
#   medium (~769M) — very good  ← recommended
#   large  (~1550M)— best accuracy (needs GPU)
#   large-v2 / large-v3 — incremental improvements
# =============================================

import os
import logging
import time
from dataclasses import dataclass, field

import whisper
import torch

from config import WHISPER_MODEL, WHISPER_DEVICE, WHISPER_LANGUAGE
from utils import seconds_to_timestamp

logger = logging.getLogger(__name__)


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
        """Returns formatted text with or without timestamps."""
        if not with_timestamps or not self.segments:
            return self.full_text
        return "\n".join(f"[{seconds_to_timestamp(s.start)}]  {s.text.strip()}" for s in self.segments)


class Transcriber:
    """Loads the Whisper model once and transcribes audio files."""

    def __init__(self, model_name: str = WHISPER_MODEL, device: str = WHISPER_DEVICE):
        self._device = self._resolve_device(device)
        logger.info(f"Loading Whisper model '{model_name}' on {self._device}…")
        t0 = time.time()
        self._model = whisper.load_model(model_name, device=self._device)
        logger.info(f"Model loaded in {time.time() - t0:.1f}s")

    def transcribe(self, audio_path: str, language: str | None = WHISPER_LANGUAGE) -> TranscriptionResult:
        """
        Transcribes *audio_path* and returns a TranscriptionResult.

        Raises:
            FileNotFoundError if the audio file doesn't exist.
            RuntimeError if transcription fails.
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        logger.info(f"Transcribing: {os.path.basename(audio_path)}")

        options: dict = {
            "task": "transcribe",
            "verbose": False,
            # Helps keep context between segments — makes a noticeable difference
            "condition_on_previous_text": True,
            "compression_ratio_threshold": 2.4,
            "no_speech_threshold": 0.6,
            # FP16 only works on GPU; on CPU it actually slows things down
            "fp16": self._device == "cuda",
        }
        if language:
            options["language"] = language

        t0 = time.time()
        try:
            result = self._model.transcribe(audio_path, **options)
        except Exception as e:
            raise RuntimeError(f"Transcription error: {e}") from e

        logger.info(f"Transcription completed in {time.time() - t0:.1f}s")

        segments = [Segment(start=s["start"], end=s["end"], text=s["text"]) for s in result.get("segments", [])]

        return TranscriptionResult(
            full_text=result["text"].strip(),
            language=result.get("language", "unknown"),
            segments=segments,
            duration_seconds=segments[-1].end if segments else 0.0,
        )

    @staticmethod
    def _resolve_device(device: str) -> str:
        if device == "auto":
            chosen = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Device auto-detected: {chosen.upper()}")
            return chosen
        return device


# Keep a single instance around so we don't reload the model on every call
_global_transcriber: Transcriber | None = None

def get_transcriber() -> Transcriber:
    """Returns a global Transcriber instance (singleton)."""
    global _global_transcriber
    if _global_transcriber is None:
        _global_transcriber = Transcriber()
    return _global_transcriber

def transcribe_audio(audio_path: str, language: str | None = None) -> TranscriptionResult:
    """Shortcut to transcribe without managing the instance."""
    return get_transcriber().transcribe(audio_path, language=language)
