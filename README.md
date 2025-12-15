# Stable-TS GUI Transcriber

A user-friendly desktop application for transcribing video and audio files using [stable-ts](https://github.com/jianfch/stable-ts) (Stable Whisper).

![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)
![License MIT](https://img.shields.io/badge/License-MIT-green)

## Features

- **Drag & Drop Interface**: Easily add video/audio files to the transcription queue
- **Queue Management**: View pending files, remove individual items, or clear the entire queue
- **Configurable Settings**:
  - **Model**: tiny, base, small, medium, large, large-v2, large-v3
  - **Language**: Auto-detect or select from 99+ supported languages
  - **Output Format**: VTT, SRT, TXT, or JSON
- **Settings Persistence**: Your preferences are saved automatically
- **Real-time Progress**: View transcription progress and logs in the built-in terminal
- **Stop Functionality**: Safely stop transcription at any time (immediately frees GPU memory)
- **GPU Acceleration**: Automatically uses CUDA if available for faster transcription

---

## Quick Start

### 1. Prerequisites

- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
- **FFmpeg** - Required for audio/video processing

### 2. Install FFmpeg

FFmpeg must be installed and added to your system PATH.

<details>
<summary><b>Windows</b></summary>

**Option A: Using winget (recommended)**
```powershell
winget install ffmpeg
```

**Option B: Manual installation**
1. Download from [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/)
2. Extract the archive (e.g., to `C:\ffmpeg`)
3. Add the `bin` folder to your system PATH:
   - Search "Environment Variables" in Windows
   - Edit "Path" under System Variables
   - Add `C:\ffmpeg\bin` (or wherever you extracted it)
4. Restart your terminal and verify: `ffmpeg -version`

</details>

<details>
<summary><b>macOS</b></summary>

```bash
brew install ffmpeg
```

</details>

<details>
<summary><b>Linux (Ubuntu/Debian)</b></summary>

```bash
sudo apt update
sudo apt install ffmpeg
```

</details>

### 3. Install Dependencies

Run the included installer script which will check and install all required packages:

```bash
python install.py
```

This will:
- Check your Python version
- Verify FFmpeg is installed
- Install/verify PyTorch (with CUDA support detection)
- Install customtkinter, tkinterdnd2, and stable-ts

**Or install manually:**

```bash
# For CPU only:
pip install torch torchvision torchaudio
pip install customtkinter tkinterdnd2 stable-ts

# For NVIDIA GPU (CUDA 12.1):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install customtkinter tkinterdnd2 stable-ts
```

### 4. Launch the Application

```bash
python main.py
```

---

## Usage Guide

### Basic Workflow

1. **Add Files**: Drag and drop video/audio files into the drop zone, or click to browse
2. **Configure Settings**: Select your preferred model, language, and output format
3. **Start Transcription**: Click "Start Transcription" to begin processing
4. **Monitor Progress**: Watch the terminal output for real-time progress
5. **Find Output**: Transcription files are saved next to the source files

### Settings Explained

| Setting | Options | Description |
|---------|---------|-------------|
| **Model** | tiny, base, small, medium, large, large-v2, large-v3 | Larger models are more accurate but slower and require more VRAM |
| **Language** | Auto, en, es, fr, de, ja, zh, ... | Use "Auto" for automatic detection, or specify for better accuracy |
| **Format** | vtt, srt, txt, json | Output subtitle/transcript format |

### Model Selection Guide

| Model | VRAM Required | Speed | Accuracy |
|-------|--------------|-------|----------|
| tiny | ~1 GB | Fastest | Basic |
| base | ~1 GB | Very Fast | Good |
| small | ~2 GB | Fast | Better |
| medium | ~5 GB | Moderate | Great |
| large | ~10 GB | Slow | Best |
| large-v2 | ~10 GB | Slow | Best |
| large-v3 | ~10 GB | Slow | Best (latest) |

**Recommendation**: Start with `small` for a good balance of speed and accuracy. Use `medium` or `large` for important transcriptions where accuracy is critical.

---

## Troubleshooting

### "No module named 'customtkinter'"

Run the installer script to install missing dependencies:
```bash
python install.py
```

### "ffmpeg not found"

FFmpeg is not installed or not in your PATH. See the installation instructions above.

### Transcription is slow

- Ensure you have a CUDA-capable NVIDIA GPU
- Verify CUDA is available: `python -c "import torch; print(torch.cuda.is_available())"`
- If False, reinstall PyTorch with CUDA support
- Use a smaller model (e.g., `small` instead of `large`)

### Out of memory errors

- Use a smaller model
- Close other GPU-intensive applications
- The `tiny` or `base` models work on most systems

### Stop button not working

The stop button forcefully terminates the transcription process and immediately frees GPU memory. If it's not responding, the main window may be frozen - wait a few seconds or restart the application.

---

## File Structure

```
stable_ts_gui/
├── main.py           # Application entry point
├── gui.py            # GUI implementation (customtkinter)
├── transcriber.py    # Transcription logic (multiprocessing)
├── install.py        # Dependency installer script
├── settings.json     # User settings (auto-generated)
└── README.md         # This file
```

---

## Technical Details

- **GUI Framework**: CustomTkinter (modern-looking Tkinter wrapper)
- **Drag & Drop**: tkinterdnd2
- **Transcription Engine**: stable-ts (Stable Whisper)
- **Process Management**: Uses multiprocessing for true cancellation support

The application uses multiprocessing instead of threading for transcription. This allows the Stop button to immediately terminate a running transcription and free GPU memory, rather than waiting for the current file to complete.

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Credits

- [stable-ts](https://github.com/jianfch/stable-ts) - Stable Whisper implementation
- [OpenAI Whisper](https://github.com/openai/whisper) - Original speech recognition model
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Modern Tkinter widgets
- [tkinterdnd2](https://github.com/pmgagne/tkinterdnd2) - Drag and drop support
