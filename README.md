# Video → Transcription

Converts the audio from **any online video** into text using
[yt-dlp](https://github.com/yt-dlp/yt-dlp) for downloading and
[OpenAI Whisper](https://github.com/openai/whisper) for transcription.

## Supported Sites

YouTube · Vimeo · Twitter/X · TikTok · Instagram · Facebook · Twitch · SoundCloud · and [1,000+ more](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md).

---

## Requirements

| Requirement | Notes |
|-------------|-------|
| Python 3.10+ | `python --version` to check |
| ffmpeg | See install commands below |
| Python dependencies | `pip install -r requirements.txt` |

**Install ffmpeg:**
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows — download from https://ffmpeg.org/download.html and add to PATH
```

> **GPU support:** If you have a CUDA-compatible NVIDIA GPU, the program will detect it automatically for faster transcription.

---

## Quick Start

```bash
git clone <repo-url>
cd video_transcriber
pip install -r requirements.txt
python main.py
```

---

## Usage

```bash
# Interactive mode (prompts for URL)
python main.py

# Pass URL directly
python main.py "https://www.youtube.com/watch?v=..."

# Force a language
python main.py "URL" --lang es

# Use a larger model
python main.py "URL" --model large-v3

# Other flags
--no-timestamps   # Omit timestamps from output
--no-save         # Don't save the .txt file
--keep-audio      # Keep the downloaded audio file
```

---

## Project Structure

```
video_transcriber/
├── main.py          ← Entry point
├── downloader.py    ← Audio download via yt-dlp
├── transcriber.py   ← Transcription via Whisper
├── utils.py         ← Helper functions
├── config.py        ← Global settings
├── requirements.txt
├── temp_audio/      ← Temporary audio (auto-cleaned)
└── transcriptions/  ← Saved transcriptions (.txt)
```

---

## Configuration

Edit `config.py` to change default behavior:

```python
WHISPER_MODEL    = "medium"   # tiny | base | small | medium | large | large-v2 | large-v3
WHISPER_LANGUAGE = None       # None = auto-detect | "es" = always Spanish
SHOW_TIMESTAMPS  = True
SAVE_TXT         = True
```

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `ffmpeg not found` | Install ffmpeg and add it to PATH |
| `No module named 'whisper'` | `pip install openai-whisper` |
| `No module named 'yt_dlp'` | `pip install yt-dlp` |
| Download blocked | Update yt-dlp: `pip install -U yt-dlp` |
| Private/paid video | Not supported (requires session cookies) |
| GPU out of memory | Use a smaller model or run on CPU |

---

## Licenses

- **yt-dlp** — Unlicense
- **OpenAI Whisper** — MIT License
- **This project** — Free for personal and educational use
