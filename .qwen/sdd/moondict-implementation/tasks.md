# Tasks — moondict-implementation

## Estado actual
- `config.py` ✅ implementado (NO modificar)
- Resto de módulos: archivos vacíos (stubs)
- Tests: solo `tests/__init__.py`
- Pipeline: sounddevice → queue.Queue → Transcriber.create_stream() → xdotool
- State machine: START → LOADING → IDLE → LISTENING → PROCESSING → IDLE
- 4 threads: main, keyboard, PortAudio, Moonshine

---

## M1: Core (Test Infra + Engine + Audio)

### T001 — Test Infrastructure: conftest.py + mocks
**Description**: Crear `tests/conftest.py` con fixtures para mockear sounddevice, moonshine-voice, xdotool, pynput. Incluir fixtures reutilizables: `mock_sounddevice`, `mock_moonshine_model`, `mock_xdotool`, `mock_pynput`, `tmp_config`.
**Dependencies**: None
**Acceptance criteria**:
- `pytest` runs green with 0 tests (infrastructure only)
- All external deps (sounddevice, moonshine, pynput, xdotool) mockeable via fixtures
- `tmp_config` fixture crea config temporal con valores de test
**Complexity**: M

### T002 — Engine Interface: ABC Transcriber
**Description**: Definir `engine/base.py` con clase abstracta `Transcriber` (protocol/interface): método `create_stream(queue)` que retorna un generator de texto, `load_model()`, `unload()`. Definir `TranscriptionResult` dataclass (text: str, confidence: float, language: str).
**Dependencies**: T001
**Acceptance criteria**:
- `Transcriber` es ABC con métodos abstractos tipados
- `TranscriptionResult` dataclass con type hints
- MyPy strict green
**Complexity**: S

### T003 — Engine Implementation: MoonshineTranscriber
**Description**: Implementar `engine/moonshine.py` con `MoonshineTranscriber(Transcriber)`. Usa `moonshine_onnx` para cargar modelo Spanish base. `create_stream()` consume audio chunks del queue y yield texto transcrito. Maneja lifecycle load/unload.
**Dependencies**: T002
**Acceptance criteria**:
- `MoonshineTranscriber` hereda de `Transcriber`
- `create_stream()` acepta `queue.Queue[bytes]` y genera `str`
- Modelo se carga en `load_model()` con path configurable
- Tests unitarios con moonshine mockeado
- MyPy strict green
**Complexity**: L

### T004 — Engine Tests
**Description**: Tests para T002 + T003: test abstract interface, test MoonshineTranscriber lifecycle (load → stream → unload), test error handling (model not found, audio format error).
**Dependencies**: T003
**Acceptance criteria**:
- ≥5 tests pasando
- Mock de moonshine-voice verificado (llamadas correctas)
- Coverage engine/ ≥ 80%
**Complexity**: M

### T005 — Audio Capture: AudioRecorder
**Description**: Implementar `audio/capture.py` con `AudioRecorder`. Usa sounddevice.InputStream a 16000Hz, mono, float32. Callback escribe en `queue.Queue[np.ndarray]`. Métodos: `start()`, `stop()`, `is_recording`. Thread-safe.
**Dependencies**: T001
**Acceptance criteria**:
- `AudioRecorder` crea InputStream con sample_rate=16000, channels=1, dtype='float32'
- Callback thread-safe escribe en queue.Queue
- `start()`/`stop()` manejan lifecycle correctamente
- Tests con sounddevice mockeado
- MyPy strict green
**Complexity**: M

### T006 — Audio Feedback: FeedbackPlayer
**Description**: Implementar `audio/feedback.py` con `FeedbackPlayer`. Toca sonidos de inicio/fin de grabación usando `sounddevice.play()` con WAVs embebidos o generados por código (beep sinusoidal). Métodos: `play_start()`, `play_stop()`. No bloqueante.
**Dependencies**: T005
**Acceptance criteria**:
- Genera beep sinusoidal programáticamente (sin archivos externos)
- `play_start()` y `play_stop()` sonidos diferenciados
- No bloquea el thread principal
- Tests con sounddevice.play mockeado
- MyPy strict green
**Complexity**: S

### T007 — Audio Tests
**Description**: Tests para T005 + T006: test capture lifecycle, test queue population, test feedback sounds, test error handling (device unavailable).
**Dependencies**: T005, T006
**Acceptance criteria**:
- ≥6 tests pasando
- Coverage audio/ ≥ 80%
**Complexity**: M

---

## M2: Dictation (Shortcuts + Injection + Orchestrator)

### T008 — Keyboard Shortcut Listener
**Description**: Implementar `shortcuts/keyboard.py` con `ShortcutListener`. Usa pynput para detectar tecla configurada (ctrl/alt/shift). Soporta `push_to_talk` (hold) y `toggle` (press). Emite eventos via callback: `on_press`, `on_release`. Thread en background.
**Dependencies**: T001
**Acceptance criteria**:
- `ShortcutListener(key, mode, on_press, on_release)` funciona
- Modos push_to_talk y toggle correctamente diferenciados
- Listener corre en thread separado
- Tests con pynput mockeado
- MyPy strict green
**Complexity**: M

### T009 — Shortcut Tests
**Description**: Tests para T008: test push_to_talk mode, test toggle mode, test key mapping, test thread lifecycle.
**Dependencies**: T008
**Acceptance criteria**:
- ≥4 tests pasando
- Coverage shortcuts/ ≥ 80%
**Complexity**: S

### T010 — Text Injection: XdoToolInjector
**Description**: Implementar `injection/xdotool.py` con `TextInjector` (protocol) y `XdoToolInjector(TextInjector)`. Usa `subprocess.run(["xdotool", "type", "--clearmodifiers", text])` para inyectar texto. Métodos: `inject(text)`, `is_available()`. Graceful fallback si xdotool no existe.
**Dependencies**: T001
**Acceptance criteria**:
- `TextInjector` protocol con `inject(text: str) -> None`
- `XdoToolInjector` ejecuta xdotool correctamente
- `is_available()` chequea xdotool en PATH
- Manejo de error si subprocess falla
- Tests con subprocess mockeado
- MyPy strict green
**Complexity**: M

### T011 — Injection Tests
**Description**: Tests para T010: test inject happy path, test xdotool not found, test subprocess error, test is_available.
**Dependencies**: T010
**Acceptance criteria**:
- ≥4 tests pasando
- Coverage injection/ ≥ 80%
**Complexity**: S

### T012 — State Machine: DictationState
**Description**: Implementar `state.py` con `DictationState` enum (START, LOADING, IDLE, LISTENING, PROCESSING) y `StateManager` que maneja transiciones válidas con validación. Log de transiciones.
**Dependencies**: None (paralelizable con M1)
**Acceptance criteria**:
- Enum con todos los estados
- `StateManager` valida transiciones (ej: IDLE→LISTENING OK, LISTENING→START ERROR)
- Transiciones logueadas con loguru
- Tests de todas las transiciones válidas e inválidas
- MyPy strict green
**Complexity**: S

### T013 — Orchestrator: DictationApp
**Description**: Implementar `main.py` con `DictationApp`. Orquesta todos los componentes: crea Transcriber, AudioRecorder, ShortcutListener, TextInjector, FeedbackPlayer, StateManager. Loop principal: escucha shortcut → start capture → transcribe → inject → stop. Cola puente queue.Queue entre audio y transcriber.
**Dependencies**: T003, T005, T006, T008, T010, T012
**Acceptance criteria**:
- `DictationApp.__init__()` inyecta todas las dependencias
- `run()` arranca todos los componentes en threads correctos
- Pipeline completo: shortcut → capture → transcribe → inject
- State machine integrada en el flujo
- Graceful shutdown con SIGINT/SIGTERM
- MyPy strict green
**Complexity**: L

### T014 — Orchestrator Tests
**Description**: Tests para T013: test init con deps mockeadas, test happy path completo (start→listen→process→inject), test shutdown, test error recovery.
**Dependencies**: T013
**Acceptance criteria**:
- ≥5 tests pasando
- Coverage main.py ≥ 70%
- Tests aislados con mocks de todos los componentes
**Complexity**: M

### T015 — Entry Point: __main__.py
**Description**: Implementar `__main__.py` con `main()`: carga config, configura loguru, instancia `DictationApp` con dependencias reales, maneja excepciones top-level.
**Dependencies**: T013
**Acceptance criteria**:
- `python -m moondict` ejecuta la app
- `moondict` CLI funciona (pyproject script)
- Config se carga desde ~/.config/moondict/config.json
- Loguru configurado según config.log_level
- Manejo de excepciones con stack trace logueado
**Complexity**: S

---

## M3: UX (Tray + Feedback)

### T016 — System Tray Indicator
**Description**: Implementar `tray/indicator.py` con `TrayIndicator`. Usa pystray para crear ícono de sistema. Muestra estado actual (idle/listening/processing) con colores diferentes. Menú context con: Toggle Dictation, Settings, Quit.
**Dependencies**: T012
**Acceptance criteria**:
- `TrayIndicator` crea ícono pystray
- Ícono cambia color según estado del StateManager
- Menú context con acciones funcionales
- Corre en thread separado
- Tests con pystray mockeado
- MyPy strict green
**Complexity**: M

### T017 — Tray Tests
**Description**: Tests para T016: test tray creation, test state-based icon change, test menu actions, test shutdown.
**Dependencies**: T016
**Acceptance criteria**:
- ≥4 tests pasando
- Coverage tray/ ≥ 70%
**Complexity**: S

### T018 — Tray Integration with Orchestrator
**Description**: Integrar `TrayIndicator` en `DictationApp`. El orchestrator pasa el StateManager al tray para updates visuales. Acciones del menú (toggle, quit) conectadas al orchestrator.
**Dependencies**: T013, T016
**Acceptance criteria**:
- Tray muestra estado en tiempo real
- Menu toggle inicia/detiene dictado
- Menu quit hace shutdown graceful
- Tests de integración
**Complexity**: M

---

## M4: Polish

### T019 — Performance Validation
**Description**: Verificar constraints de rendimiento: RAM < 150MB, CPU idle < 1%, inference < 3x realtime. Crear script `tools/bench.py` que mide uso de recursos durante 60s de dictado simulado.
**Dependencies**: T014, T018
**Acceptance criteria**:
- Script de benchmark ejecutable
- RAM medida < 150MB en idle y activo
- CPU idle < 1%
- Documentar resultados en docs/PERFORMANCE.md
**Complexity**: M

### T020 — Acceptance Tests (Integration)
**Description**: Tests de integración end-to-end simulando flujo completo sin hardware real: mock sounddevice input → mock moonshine output → verify xdotool called con texto correcto.
**Dependencies**: T014
**Acceptance criteria**:
- ≥3 tests E2E pasando
- Simulación de ciclo completo de dictado
- Verificación de texto inyectado
**Complexity**: M

### T021 — Documentation Update
**Description**: Actualizar README.md con: instalación, configuración, uso, atajos de teclado, troubleshooting. Crear docs/ARCHITECTURE.md con diagrama de componentes y flujo de datos.
**Dependencies**: T015, T018
**Acceptance criteria**:
- README.md con sección de instalación, uso, configuración
- docs/ARCHITECTURE.md con diagrama de flujo
- docs/PERFORMANCE.md con resultados de T019
- Todos los comandos de AGENTS.md funcionan
**Complexity**: S

### T022 — CI/Local Validation
**Description**: Ejecutar batería completa: `ruff check . && ruff format . && mypy src/ && pytest -v`. Corregir cualquier fallo. Verificar `python -m moondict --help` funciona.
**Dependencies**: T019, T020, T021
**Acceptance criteria**:
- `ruff check` sin errores
- `ruff format` sin cambios pendientes
- `mypy src/` sin errores (strict mode)
- `pytest` todos los tests pasando (≥30 tests)
- Coverage total ≥ 75%
**Complexity**: S

---

## Dependency Graph

```
T001 ─┬─► T002 ─► T003 ─► T004 ──┐
      ├─► T005 ──┬─► T006 ─► T007│
      │          │               │
      ├─► T008 ─► T009          │
      │                          │
      ├─► T010 ─► T011          │
      │                          ▼
T012 ─┘                          │
                                 ▼
                            T013 ─► T014 ─┬─► T019 ─┐
                                 │         ├─► T020  │
                                 ▼         │         ▼
                            T015        T016 ─► T017 ─► T018 ─► T021 ─► T022
                                                    │
                                                    └─► T018 (integration)
```

## Parallelizable Groups
- **Group A**: T001 (base para todo M1)
- **Group B**: T002, T005, T008, T010, T012 (paralelizables tras T001)
- **Group C**: T003, T006, T009, T011 (dependen de Group B)
- **Group D**: T004, T007, T013, T016 (dependen de Group C)
- **Group E**: T014, T015, T017, T018, T019, T020, T021, T022 (secuencia final)
