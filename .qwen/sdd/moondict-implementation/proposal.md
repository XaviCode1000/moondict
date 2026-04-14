# MoonDict — Implementation Proposal

**Change**: `moondict-implementation`
**Date**: 2026-04-14
**Status**: Pending Review
**Artifact Store**: engram

---

## 1. Executive Summary

MoonDict es una aplicación de dictado por voz **100% offline** para Linux, diseñada para hardware limitado (Haswell 4-core, 8GB RAM, HDD). Usa Moonshine Base Spanish (58M params, WER 4.33%) como motor ASR.

**Problema**: El predecesor Vocalinux usa whisper.cpp que es lento (~16s inferencia por 9s audio) y consume ~400MB RAM. MoonDict resuelve esto con Moonshine: ~80MB RAM, inferencia < 3x realtime.

**Estado actual**: Solo `config.py` implementado. Todos los demás módulos son archivos vacíos. No hay infraestructura de testing.

**Objetivo**: Implementar la app completa en 4 fases siguiendo el PRD, con TDD estricto, siguiendo arquitectura limpia/hexagonal.

---

## 2. Architecture Decisions

### 2.1 Pipeline de Audio

```
sounddevice callback → queue.Queue → Transcriber.create_stream() → TranscriptEventListener → xdotool
```

**Decisión clave**: Usar `Transcriber + create_stream()` en lugar de `MicTranscriber`.

**Por qué NO MicTranscriber**:
- `MicTranscriber` mantiene el micrófono siempre abierto → consume CPU continuamente en idle
- En hardware target (Haswell, HDD), CPU idle < 1% es requisito
- `create_stream()` permite abrir/cerrar el stream bajo demanda (solo cuando el usuario activa dictado)
- Más control sobre el ciclo de vida del audio

### 2.2 Thread Safety

- `sounddevice` callback corre en **native PortAudio thread** (no Python GIL thread)
- Bridge: `queue.Queue` para pasar audio del callback al thread de transcripción
- `threading.Event` para señalizar inicio/fin de grabación
- El stream de Moonshine corre en un thread dedicado (separado del callback)

### 2.3 Composition Root

- `main.py` como orquestador principal
- `__main__.py` como entry point mínimo (solo llama a `main()`)
- Inyección de dependencias explícita en `main()`
- No hidden side effects, todo configurable

### 2.4 Text Injection con Unicode

**Problema**: `xdotool type` NO soporta Unicode correctamente (tildes, ñ se rompen).

**Solución**: Dos estrategias:
1. **Primaria**: `xdotool type` con ASCII-safe + caracteres especiales via clipboard fallback
2. **Fallback**: `xclip` o `wl-copy` para clipboard + Ctrl+V simulado
3. Implementar como `TextInjector` interface con backends intercambiables

### 2.5 Model Download en HDD

- Primera ejecución descarga ~58MB → debe mostrar estado de loading
- Usar indicador de progreso (barra o spinner en consola)
- Modelos se guardan en `~/.local/share/moondict/models/`
- HDD lento → no bloquear UI durante descarga

---

## 3. Implementation Phases

### Phase 1: Test Infra + Core (M1) — 1-2 días

**Objetivo**: Infraestructura de testing + pipeline funcional (capture → transcribe → print)

| # | Tarea | Archivos | Tests |
|---|-------|----------|-------|
| 1.1 | `conftest.py` con mocks para sounddevice, moonshine, xdotool | `tests/conftest.py` | — |
| 1.2 | `engine/moonshine.py` — wrapper Transcriber + create_stream | `src/moondict/engine/moonshine.py` | `tests/test_engine.py` |
| 1.3 | `audio/capture.py` — SoundDevice callback + queue.Queue bridge | `src/moondict/audio/capture.py` | `tests/test_audio_capture.py` |
| 1.4 | `audio/feedback.py` — sons de inicio/fin | `src/moondict/audio/feedback.py` | `tests/test_audio_feedback.py` |
| 1.5 | Tests unitarios para config | `tests/test_config.py` | — |

**Criterio de aceptación**:
- `pytest` corre con > 80% coverage
- Pipeline end-to-end: grabar 5s audio → transcribir → print resultado
- RAM < 100MB durante inferencia

### Phase 2: Dictation Completo (M2) — 2-3 días

**Objetivo**: Push-to-talk + text injection + config + logging

| # | Tarea | Archivos | Tests |
|---|-------|----------|-------|
| 2.1 | `shortcuts/keyboard.py` — pynput global listener | `src/moondict/shortcuts/keyboard.py` | `tests/test_shortcuts.py` |
| 2.2 | `injection/xdotool.py` — text injection con Unicode fallback | `src/moondict/injection/xdotool.py` | `tests/test_injection.py` |
| 2.3 | `main.py` — orquestador completa | `src/moondict/main.py` | `tests/test_main.py` |
| 2.4 | `__main__.py` — entry point | `src/moondict/__main__.py` | — |
| 2.5 | Integración: push-to-talk → transcribe → inyect | — | `tests/test_integration.py` |

**Criterio de aceptación**:
- Mantener Ctrl → grabar → soltar → transcribir → inyectar texto
- Unicode funciona: "María tomó café aquí" → correcto
- Config hot-reload sin reiniciar
- Logging con loguru en todos los módulos

### Phase 3: UX Completa (M3) — 1-2 días

**Objetivo**: System tray + audio feedback + polish

| # | Tarea | Archivos | Tests |
|---|-------|----------|-------|
| 3.1 | `tray/indicator.py` — pystray icon + menu | `src/moondict/tray/indicator.py` | `tests/test_tray.py` |
| 3.2 | Audio feedback integration | `src/moondict/audio/feedback.py` | — |
| 3.3 | Loading state para descarga de modelo | `src/moondict/main.py` | — |
| 3.4 | Integration tests end-to-end | `tests/test_e2e.py` | — |

**Criterio de aceptación**:
- Icono en tray con estados: idle, listening, processing
- Menú contextual: settings, toggle mode, quit
- Sonido al iniciar/parar dictado
- README actualizado con instrucciones

### Phase 4: Optimización (M4) — 1 día

**Objetivo**: Perfil de memoria/CPU + acceptance tests

| # | Tarea | Archivos |
|---|-------|----------|
| 4.1 | Memory profiling (tracemalloc) | — |
| 4.2 | CPU profiling (cProfile) | — |
| 4.3 | Ajustes para Haswell (AVX2, threads) | — |
| 4.4 | Acceptance tests (WER con 20 frases) | `tests/test_acceptance.py` |
| 4.5 | Documentación final | `README.md`, `docs/` |

**Criterio de aceptación** (del PRD):
- RAM pico < 150 MB
- CPU idle < 1%
- Inferencia 10s audio < 15s
- WER español < 5%
- Startup < 2s

---

## 4. Risks and Mitigations

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| `moonshine-voice` API cambia | Media | Alto | Pin versión en pyproject.toml, tests con mock |
| `sounddevice` + PipeWire incompatibilidad | Baja | Medio | Fallback a dispositivo por defecto, documentar |
| `xdotool` Unicode roto | Alta | Medio | Clipboard fallback implementado desde Fase 2 |
| pynput no funciona en Wayland | Media | Bajo | Documentar limitación X11-only, futuro wlroots |
| Modelo Spanish mala calidad | Baja | Alto | Test WER en Fase 4, fallback a modelo EN si necesario |
| HDD lento en carga de modelo | Media | Bajo | Cachear modelo en RAM después de primera carga |

---

## 5. Success Criteria

| Criterio | Target | Medición |
|----------|--------|----------|
| Inferencia 10s audio | < 15s | `time` en dictado real |
| RAM pico | < 150 MB | `ps aux` durante uso |
| CPU idle | < 1% | `htop` sin dictar |
| Startup | < 2s | `time moondict` |
| WER español | < 5% | 20 frases conocidas |
| Unicode injection | ✅ | "María tomó café aquí" → correcto |
| Tests passing | 100% | `pytest -v` |
| Coverage | > 80% | `pytest --cov` |
| mypy strict | 0 errors | `mypy src/` |
| ruff | 0 errors | `ruff check .` |

---

## 6. Dependencies Order

```
Phase 1 (conftest + core)
    ↓
Phase 2 (shortcuts + injection + orchestrator)
    ↓
Phase 3 (tray + UX)
    ↓
Phase 4 (optimization + acceptance)
```

Cada fase es **independiente y deployable**. Se puede hacer release después de cada fase.

---

## 7. Testing Strategy

- **TDD Estricto**: test primero → implementación → refactor
- **Mocks**: sounddevice, moonshine-voice, xdotool, pynput, pystray
- **Unit tests**: cada módulo aislado
- **Integration tests**: pipeline completo (mock engine)
- **Acceptance tests**: WER con frases conocidas (requiere modelo real)
- **Workers**: `pytest -n 2` (CPU 4C/4T constraint)
