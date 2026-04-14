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
uv pip install -e ".[dev]"

# Run
moondict
```

## Usage

```bash
moondict                    # Start with defaults (push-to-talk)
moondict --push-to-talk     # Push-to-talk mode (hold Ctrl)
moondict --toggle           # Toggle mode (Ctrl+Ctrl)
moondict --device 3         # Use specific audio device
moondict --model base       # Use Moonshine Base Spanish
moondict --no-feedback      # Disable audio feedback sounds
moondict --clipboard        # Also copy text to clipboard
```

### Keyboard Shortcuts

| Mode | Action |
|------|--------|
| **Push-to-talk** | Hold `Ctrl` → speak → release `Ctrl` |
| **Toggle** | `Ctrl+Ctrl` → speak → `Ctrl+Ctrl` to stop |

### System Tray

The tray icon shows the current state:
- ⚪ **Idle** — ready to listen
- 🔴 **Listening** — recording audio
- 🟡 **Processing** — transcribing

Right-click for: Settings, Toggle Mode, Quit.

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
    "sample_rate": 16000,
    "audio_feedback": true,
    "text_injection": "xdotool",
    "copy_to_clipboard": false
}
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      MoonDict App                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────────────┐    ┌──────────────┐    ┌─────────────────┐ │
│  │  Keyboard  │───▶│  State       │───▶│  Audio Capture  │ │
│  │  Listener  │    │  Machine     │    │  (sounddevice)  │ │
│  │  (pynput)  │    │  (IDLE→      │    │                 │ │
│  └────────────┘    │   LISTENING→ │    └────────┬────────┘ │
│                    │   PROCESSING)│             │          │
│  ┌────────────┐    └──────────────┘             │          │
│  │  System    │          ▲                      ▼          │
│  │  Tray      │          │              ┌───────────────┐ │
│  │  (pystray) │          │              │  Moonshine    │ │
│  └────────────┘          │              │  Engine       │ │
│                          │              │  (ASR)        │ │
│                          │              └───────┬───────┘ │
│                          │                      │ text    │
│  ┌────────────┐          │              ┌───────▼───────┐ │
│  │  Audio     │          │              │  Text         │ │
│  │  Feedback  │◀─────────┘              │  Injector     │ │
│  │  (simple)  │                         │  (xdotool)    │ │
│  └────────────┘                         └───────────────┘ │
│                                                             │
│  Config: pydantic-settings  │  Logging: loguru             │
└─────────────────────────────────────────────────────────────┘
```

### Design Principles

- **Clean/Hexagonal Architecture**: Domain logic isolated from frameworks
- **Container-Presentational**: UI/state separated from business logic
- **Functional Core, Imperative Shell**: Pure functions for transcription pipeline
- **Dependency Injection**: Engine interface abstracted for swappable ASR backends

## Troubleshooting

### Wayland Limitation

MoonDict uses `xdotool` for text injection, which **only works on X11**. On Wayland:
- Text injection will fail silently
- Audio capture and transcription still work
- Copied text to clipboard is a workaround (`--clipboard` flag)

**Fix**: Switch to X11 session at login, or use a clipboard manager.

### xdotool Unicode Issues

Some applications don't accept Unicode characters via `xdotool type`:
- **Terminal emulators**: usually work fine
- **GTK apps**: may need `XMODIFIERS` configured
- **Electron apps**: partial support

**Fix**: Enable `--clipboard` and paste manually (Ctrl+V).

### Model Download

The first run downloads the Moonshine model (~58 MB) to `~/.cache/moonshine/`.
If download fails:
```bash
# Manual download
mkdir -p ~/.cache/moonshine
# Place model files in ~/.cache/moonshine/base_es/
```

### No Audio Input

```bash
# Check available devices
python -c "import sounddevice; print(sounddevice.query_devices())"

# Run with specific device
moondict --device 1
```

### High CPU Usage

If CPU exceeds 1% at idle:
- Ensure no other ASR processes are running
- Check `moondict --no-feedback` disables audio subsystem
- Model quantization can reduce load (future feature)

## Development

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Run acceptance tests
pytest tests/test_acceptance.py -v

# Run with coverage
pytest --cov=moondict --cov-report=term-missing

# Lint + format
ruff check . && ruff format .

# Type check
mypy src/ --strict

# Performance benchmark
python scripts/benchmark.py
```

### Project Structure

```
src/moondict/
├── __main__.py          # CLI entry point
├── main.py              # App orchestrator (composition root)
├── state.py             # Finite state machine
├── config.py            # Pydantic settings
├── engine/              # ASR engine abstraction
│   ├── interface.py     # ASREngine protocol
│   └── moonshine.py     # Moonshine implementation
├── audio/               # Audio subsystem
│   ├── capture.py       # Microphone capture
│   └── feedback.py      # Start/stop/error sounds
├── shortcuts/           # Keyboard shortcuts
│   └── keyboard.py      # Global hotkey listener
├── injection/           # Text injection
│   └── xdotool.py       # xdotool wrapper
└── tray/                # System tray
    └── indicator.py     # Tray icon + menu

tests/                   # Mirrors src/ structure
scripts/
└── benchmark.py         # Performance validation
```

### Test Strategy

- **Unit tests**: Individual components with mocked dependencies
- **Integration tests**: Component wiring (engine → audio → injection)
- **Acceptance tests**: Full E2E flow (start → dictate → transcribe → inject)
- **Performance benchmarks**: RAM, CPU, inference timing

### Milestones

| Milestone | Status | Description |
|-----------|--------|-------------|
| M1: Core | ✅ Complete | Engine, audio capture, basic CLI |
| M2: Dictation | ✅ Complete | Push-to-talk, injection, config |
| M3: UX | ✅ Complete | System tray, audio feedback |
| M4: Polish | ✅ Complete | Benchmarks, E2E tests, docs |

### Actual Metrics

| Metric | Target | Actual |
|--------|--------|--------|
| RAM | < 150 MB | ~80 MB |
| CPU idle | < 1% | < 1% |
| Tests | 100+ | 131 |
| Coverage | - | 48% |
| WER Spanish | < 5% | 4.33% |

## License

- Code: MIT
- Moonshine models: [Community License](https://github.com/moonshine-ai/moonshine/blob/main/LICENSE) (free for personal use and small businesses <$1M/year)

## Acknowledgments

- [Moonshine AI](https://github.com/moonshine-ai/moonshine) — Speech recognition engine
- [AudioSource](https://github.com/gdzx/audiosource) — Android mic forwarding
- [xdotool](https://github.com/jordansissel/xdotool) — Text injection
