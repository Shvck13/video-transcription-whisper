# Video → Transcripción

Convierte el audio de **cualquier vídeo online** en texto usando
[yt-dlp](https://github.com/yt-dlp/yt-dlp) para la descarga y
[OpenAI Whisper](https://github.com/openai/whisper) para la transcripción.

## Sitios soportados

YouTube · Vimeo · Twitter/X · TikTok · Instagram · Facebook · Twitch ·
SoundCloud · Dailymotion · y más de 1 000 sitios adicionales.

---

## /// Requisitos previos ///

### 1. Python 3.10 o superior
```bash
python --version
```

### 2. ffmpeg (imprescindible para el audio)
| Sistema | Comando |
|---------|---------|
| Ubuntu/Debian | `sudo apt install ffmpeg` |
| macOS (Homebrew) | `brew install ffmpeg` |
| Windows | Descargar en https://ffmpeg.org/download.html y añadir al PATH |

### 3. Dependencias Python
```bash
pip install -r requirements.txt
```

> **Nota GPU:** Si tienes una tarjeta NVIDIA compatible con CUDA, el programa
> la detectará automáticamente y la transcripción será mucho más rápida.
> Asegúrate de tener instalado el driver CUDA correspondiente.

---

## Instalación rápida (todo en uno)

```bash
# Clona o descarga el proyecto
cd video_transcriber

# Instala dependencias
pip install -r requirements.txt

# ¡Listo!
python main.py
```

---

## Uso

### Modo interactivo (el programa pide la URL)
```bash
python main.py
```

### Pasar la URL directamente
```bash
python main.py "https://www.youtube.com/watch?v=..."
```

### Opciones adicionales
```bash
# Forzar idioma español (evita la detección automática)
python main.py "URL" --lang es

# Usar el modelo más preciso (más lento, necesita más RAM/VRAM)
python main.py "URL" --model large-v3

# Sin marcas de tiempo en la salida
python main.py "URL" --no-timestamps

# No guardar el archivo .txt
python main.py "URL" --no-save

# Conservar el audio descargado
python main.py "URL" --keep-audio
```

---


## Estructura del proyecto

```
video_transcriber/
├── main.py          ← Punto de entrada (ejecutar este)
├── downloader.py    ← Descarga audio con yt-dlp
├── transcriber.py   ← Transcribe con Whisper
├── utils.py         ← Funciones auxiliares
├── config.py        ← Configuración global
├── requirements.txt ← Dependencias Python
├── temp_audio/      ← Audios temporales (se limpian automáticamente)
└── transcriptions/  ← Transcripciones guardadas (.txt)
```

---

## Configuración

Edita `config.py` para cambiar el comportamiento por defecto:

```python
WHISPER_MODEL    = "medium"   # Modelo a usar
WHISPER_LANGUAGE = None       # None = auto | "es" = español siempre
SHOW_TIMESTAMPS  = True       # Incluir [HH:MM:SS] en la salida
SAVE_TXT         = True       # Guardar transcripción en archivo
```

---

## Solución de problemas

| Error | Solución |
|-------|----------|
| `ffmpeg not found` | Instala ffmpeg y añádelo al PATH |
| `No module named 'whisper'` | `pip install openai-whisper` |
| `No module named 'yt_dlp'` | `pip install yt-dlp` |
| Descarga bloqueada | Actualiza yt-dlp: `pip install -U yt-dlp` |
| Vídeo privado/de pago | No soportado (necesita cookies de sesión) |
| OOM en GPU | Usa un modelo más pequeño o añade `--device cpu` |

---

## Licencias

- **yt-dlp**: Unlicense
- **OpenAI Whisper**: MIT License
- **Este proyecto**: libre para uso personal y educativo
