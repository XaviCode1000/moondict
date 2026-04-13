# MoonDict — Product Requirements Document

## Visión

Voice dictation offline para Linux usando Moonshine AI. Rápido, ligero y funcional en hardware antiguo (Haswell 4-core, 8GB RAM, HDD).

## Problema

Vocalinux con whisper.cpp es lento (~16s inferencia por 9s audio en 2 threads) y consume ~400 MB RAM. Los usuarios con hardware limitado no pueden dictar en tiempo real sin saturar el sistema.

## Solución

MoonDict usa Moonshine Base Spanish (58M params, WER 4.33%) que es ~26x más rápido que Whisper Small en CPU y consume ~80 MB RAM.

## Stack Tecnológico (Python 2026)

| Componente | Herramienta | Por qué |
|------------|-------------|---------|
| **Package manager** | `uv` | 10-50x más rápido que pip |
| **Motor ASR** | `moonshine-voice` | 26x más rápido que whisper.cpp en CPU |
| **Modelo** | Moonshine Base Spanish (58M) | WER 4.33% en español, ~58 MB |
| **Audio capture** | `sounddevice` | Más ligero que PyAudio, usa PortAudio directamente |
| **Text injection** | `subprocess` + `xdotool` | Simple, confiable en X11 |
| **Keyboard shortcuts** | `pynput` | Global hotkey listener |
| **System tray** | `pystray` | Más ligero que GTK AppIndicator |
| **Audio feedback** | `simpleaudio` | Sin dependencias de GStreamer |
| **Config** | `pydantic-settings` | Validación + JSON persistencia |
| **Logging** | `loguru` | Mejor DX que logging stdlib |

## Requisitos Funcionales

### RF-01: Captura de audio
- Capturar audio del micrófono del sistema (PipeWire/PulseAudio)
- Soporte para micrófono Android vía ADB (audiosource)
- Sample rate: 16000 Hz (nativo de Moonshine)
- Formato: mono, float32

### RF-02: Transcripción
- Motor Moonshine con modelo Base Spanish
- Streaming: transcripción parcial mientras se habla
- VAD integrado (no transcribe silencio)
- Idioma: español (configurable)

### RF-03: Activación
- **Push-to-talk**: Mantener Ctrl para grabar, soltar para transcribir
- **Toggle mode**: Ctrl+Ctrl para iniciar/parar (opcional)
- Shortcut configurable

### RF-04: Text Injection
- Inyectar texto transcrito donde esté el cursor
- Backend: xdotool (X11)
- Soporte para caracteres Unicode (tildes, ñ, etc.)
- Opción: copiar al clipboard además de inyectar

### RF-05: Configuración
- Archivo `~/.config/moondict/config.json`
- Campos: modelo, idioma, shortcut, modo activación, volumen
- Hot-reload sin reiniciar la app

### RF-06: System Tray
- Icono con estados: idle, listening, processing
- Menú contextual: settings, toggle mode, quit
- Notificaciones de sistema al iniciar/parar dictado

### RF-07: Audio Feedback
- Sonido sutil al iniciar grabación
- Sonido al finalizar y texto inyectado
- Desactivable en settings

## Requisitos No Funcionales

### RNF-01: Rendimiento
- RAM: < 150 MB total
- CPU idle: < 1%
- Inferencia: < 3x realtime (3s inferencia por 9s audio)
- Startup: < 2s

### RNF-02: Hardware Target
- CPU: Intel Haswell (4 cores, AVX2)
- RAM: 8 GB
- Disco: HDD mecánico (I/O lento)
- OS: CachyOS Linux (PipeWire)

### RNF-03: Offline
- 100% offline, sin llamadas a internet
- Modelo descargado localmente

### RNF-04: Licencia
- Moonshine Community License (uso personal/pequeños negocios)
- Código: MIT

## Arquitectura

```
moondict/
├── src/moondict/
│   ├── __main__.py          # Entry point CLI
│   ├── main.py              # App orchestrator
│   ├── audio/
│   │   ├── capture.py       # SoundDevice mic capture
│   │   └── feedback.py      # Audio feedback sounds
│   ├── engine/
│   │   └── moonshine.py     # Moonshine wrapper + VAD
│   ├── injection/
│   │   └── xdotool.py       # Text injection via xdotool
│   ├── shortcuts/
│   │   └── keyboard.py      # Global hotkey listener
│   ├── tray/
│   │   └── indicator.py     # System tray icon + menu
│   └── config.py            # Pydantic settings
├── models/                   # Moonshine models (gitignored)
├── resources/
│   └── sounds/              # Audio feedback WAV files
├── tests/
├── pyproject.toml
└── README.md
```

## Criterios de Aceptación

| Criterio | Target | Medición |
|----------|--------|----------|
| Inferencia 10s audio | < 15s | `time` en dictado real |
| RAM pico | < 150 MB | `ps aux` durante uso |
| CPU idle | < 1% | `htop` sin dictar |
| Startup | < 2s | `time moondict` |
| WER español | < 5% | Prueba con 20 frases conocidas |
| Text injection Unicode | ✅ | "María tomó café aquí" → correcto |

## Milestones

### M1: Core funcional (1-2 días)
- [ ] pyproject.toml con uv
- [ ] Moonshine integration
- [ ] Captura de audio básica
- [ ] CLI simple: transcribe y printea

### M2: Dictation completo (2-3 días)
- [ ] Push-to-talk con pynput
- [ ] Text injection con xdotool
- [ ] Config con pydantic-settings
- [ ] Logging con loguru

### M3: UX completa (1-2 días)
- [ ] System tray con pystray
- [ ] Audio feedback
- [ ] Settings dialog (opcional, GTK)
- [ ] README con instrucciones

### M4: Optimización (1 día)
- [ ] Perfil de memoria/CPU
- [ ] Ajustes para Haswell
- [ ] Tests básicos

## Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Moonshine Spanish no funciona bien | Media | Alto | Probar antes de invertir |
| sounddevice no funciona con PipeWire | Baja | Medio | Fallback a PyAudio |
| pynput no detecta global shortcuts en Wayland | Media | Medio | Documentar limitación X11 |
| Licencia Moonshine restringe uso comercial | Baja | Bajo | Uso personal ok |
