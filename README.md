# MoonDict 🎤

Voice dictation for Linux powered by [Moonshine AI](https://github.com/moonshine-ai/moonshine) — fast, offline, lightweight.

## Features

- 🚀 **26x faster** than Whisper Small on CPU
- 🧠 **4.33% WER** in Spanish (Moonshine Base ES)
- 💾 **~80 MB RAM** total usage
- 🔒 **100% offline** — no data leaves your machine
- ⌨️ **Push-to-talk** or toggle mode
- 📝 **Text injection** in any application (X11)

## Requirements

- Python 3.11+
- Linux with PipeWire or PulseAudio
- X11 display server (Wayland: limited text injection)
- Microphone (built-in, USB, or Android via ADB)

## Quick Start

```bash
# Clone
git clone https://github.com/XaviCode1000/moondict.git
cd moondict

# Setup with uv (fast!)
uv venv && source .venv/bin/activate
uv pip install -e .

# Run
moondict
```

## Usage

```
moondict                  # Start with defaults
moondict --push-to-talk   # Push-to-talk mode (hold Ctrl)
moondict --toggle         # Toggle mode (Ctrl+Ctrl)
moondict --device 3       # Use specific audio device
moondict --model base     # Use Moonshine Base Spanish
```

## Keyboard Shortcuts

| Mode | Action |
|------|--------|
| **Push-to-talk** | Hold `Ctrl` → speak → release `Ctrl` |
| **Toggle** | `Ctrl+Ctrl` → speak → `Ctrl+Ctrl` to stop |

## Configuration

Config file: `~/.config/moondict/config.json`

```json
{
    "engine": "moonshine",
    "model": "base_es",
    "language": "es",
    "shortcut_mode": "push_to_talk",
    "shortcut_key": "ctrl",
    "audio_device": null,
    "text_injection": "xdotool",
    "copy_to_clipboard": false,
    "audio_feedback": true
}
```

## Architecture

```
┌─────────────────────────────────────────┐
│              MoonDict                    │
├─────────────────────────────────────────┤
│  ┌──────────┐  ┌───────────┐           │
│  │ Audio    │→ │ Moonshine │           │
│  │ Capture  │  │ Engine    │           │
│  └──────────┘  └─────┬─────┘           │
│                      │ text             │
│              ┌───────▼───────┐          │
│              │ Text Injector │          │
│              │   (xdotool)   │          │
│              └───────────────┘          │
│                                         │
│  Keyboard shortcuts (pynput)            │
│  System tray (pystray)                  │
│  Config (pydantic-settings)             │
└─────────────────────────────────────────┘
```

## Development

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Lint + format
ruff check .
ruff format .

# Type check
mypy src/
```

## License

- Code: MIT
- Moonshine models: [Community License](https://github.com/moonshine-ai/moonshine/blob/main/LICENSE) (free for personal use and small businesses <$1M/year)

## Acknowledgments

- [Moonshine AI](https://github.com/moonshine-ai/moonshine) — Speech recognition engine
- [AudioSource](https://github.com/gdzx/audiosource) — Android mic forwarding
- [xdotool](https://github.com/jordansissel/xdotool) — Text injection
