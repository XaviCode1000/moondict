# Manual de Operaciones Técnicas: Ecosistema Stark (Qwen Code + Gentle AI + GitNexus)

Este manual define los procedimientos, la arquitectura y los protocolos operativos del ecosistema Stark. Como Arquitecto Jefe, mi objetivo es que elimines la ceguera arquitectónica de tu flujo de trabajo mediante la implementación de una infraestructura de inteligencia de código relacional.


--------------------------------------------------------------------------------


## 1. Filosofía de Ingeniería: La Eliminación de la Ceguera Arquitectónica

### 1.1. El Problema del Desarrollo Ciego

Los asistentes de IA tradicionales y los sistemas RAG (Retrieval-Augmented Generation) basados en vectores simples sufren de una "ceguera arquitectónica" crónica. Al operar mediante la búsqueda de fragmentos de código por similitud de palabras clave —un "grep" glorificado—, pierden de vista la jerarquía, las llamadas y las dependencias cross-file. Esto resulta en blind edits: modificaciones que son sintácticamente correctas pero estructuralmente destructivas, ya que el modelo no puede "ver" el radio de impacto de sus cambios ni las dependencias invisibles.

### 1.2. La Propuesta Stark

Stark propone una transición hacia la exploración basada en grafos de conocimiento. En lugar de forzar a la IA a leer archivos uno por uno —lo que puede consumir hasta 412.000 tokens para cinco preguntas estructurales—, GitNexus utiliza un grafo que reduce ese consumo a solo 3.400 tokens. Esta reducción de 120x en el consumo de tokens elimina el fenómeno del "lost in the middle", bajando costos drásticamente y permitiendo latencias de respuesta menores a 1ms.

### 1.3. Visión JARVIS

Este ecosistema actúa como el sustrato relacional definitivo; no es una simple herramienta de búsqueda, sino una infraestructura de verdad técnica absoluta. Desprecio la ineficiencia de los sistemas probabilísticos que "adivinan" la estructura. Stark dota a humanos y agentes de una conciencia estructural total, permitiendo que operen sobre un mapa arquitectónico precomputado donde las alucinaciones sobre la estructura del código simplemente no tienen lugar.


--------------------------------------------------------------------------------


## 2. Arquitectura de Structural Understanding (GitNexus)

### 2.1. El Motor Zero-Server

GitNexus opera bajo una arquitectura local-first y zero-server. Utiliza parsers de Tree-sitter compilados en WebAssembly (WASM) para realizar análisis estático profundo directamente en tu máquina. Los datos se persisten en LadybugDB, una base de datos de grafos embebida de alto rendimiento con soporte vectorial, garantizando que tu código nunca abandone tu infraestructura por razones de privacidad y soberanía de datos.

### 2.2. El Pipeline de Indexación en 7 Fases

La construcción del grafo sigue una secuencia cronológica estricta para garantizar la integridad referencial:

1. **Mapeo de Estructura**: Identificación de archivos, carpetas y módulos.
2. **Extracción de Símbolos**: Análisis de funciones, clases, interfaces y variables.
3. **Resolución de Referencias**: Mapeo de importaciones y exportaciones cross-file.
4. **Análisis de Herencia**: Resolución de jerarquías y cumplimiento de interfaces.
5. **Identificación de Comunidades**: Agrupamiento de símbolos mediante el algoritmo Leiden para detectar áreas funcionales con alta cohesión.
6. **Detección de Procesos**: Trazado de flujos de ejecución (call chains) desde puntos de entrada detectados automáticamente (scoring de frameworks).
7. **Resolución de Tipos**: Inferencia de tipos para desambiguar llamadas a métodos.

### 2.3. Resolución de Tipos y Propagación Cross-File

El sistema utiliza un fixpoint loop que itera sobre asignaciones (copy, callResult, fieldAccess y methodCallResult) hasta alcanzar la estabilidad (máximo 10 iteraciones). En la Fase 14 (Cross-File Propagation), el conocimiento se propaga entre archivos. Para evitar ciclos infinitos y garantizar la eficiencia, GitNexus aplica un Ordenamiento Topológico basado en el algoritmo Kahn (BFS), permitiendo que las definiciones de tipos "siembren" correctamente los archivos dependientes siguiendo el orden natural de las importaciones.

### 2.4. Soporte Multilenguaje y Estrategia COBOL

Para lenguajes modernos usamos Tree-sitter (WASM). Para COBOL, implementamos una estrategia de extracción por Regex para evitar cuelgues del scanner externo y manejar patch markers no estándar (cols 1-6).

| Característica | Lenguajes Tree-Sitter | COBOL (Regex-Only) |
|----------------|----------------------|-------------------|
| Parser | AST completo (WASM) | Máquina de estados Regex |
| Velocidad | ~5ms por archivo | ~1ms por archivo (Ultra-fast) |
| Símbolos capturados | Todos los nodos del AST | Programas, Paragraphs, Sections, CALL, MOVE, Data items (01-77), FD, EXEC SQL/CICS |
| Lógica especial | Grammars formales | Quote-aware: Ignora caracteres de comentario |


--------------------------------------------------------------------------------


## 3. Configuración del Ecosistema mediante Gentle AI

### 3.1. Orquestación de Instalación

Gentle AI utiliza un enfoque dependency-first. Detectá y remediá los prerrequisitos antes de configurar agentes. Es compatible con macOS (Homebrew), Ubuntu/Debian (apt), Arch (pacman) y Windows (winget).

### 3.2. Matriz de Componentes y Prerrequisitos

| Componente | Dependencias Obligatorias | Rol en el Ecosistema |
|------------|--------------------------|---------------------|
| Engram | Go 1.24+ (solo para build) | Cerebro compartido (Puerto 7437) |
| SDD Skills | Git | Workflow de desarrollo planificado |
| Qwen Code | Node.js 20+ | Agente principal con agents, skills y commands |
| GGA | Bash / Git | Guardian Angel (Gatekeeper de calidad) |
| MCP Servers | Node.js 20+ | Protocolo de herramientas para la IA |

### 3.3. Sistemas de Memoria y Conocimiento (Engram)

Engram es el cerebro compartido del ecosistema. Operando en el puerto 7437, permite la persistencia de contexto entre sesiones de Qwen Code y otros agentes. Centraliza decisiones arquitectónicas y convenciones, evitando que cada nueva sesión de chat sea un "comenzar de cero".


--------------------------------------------------------------------------------


## 4. Agentes Especializados en Qwen Code

### 4.1. Arquitectura de Agents (Sub-Agentes)

Qwen Code utiliza **agents** — asistentes especializados configurados como archivos Markdown con frontmatter YAML. A diferencia de los perfiles de OpenCode que requerían edición de JSON, los agents de Qwen Code son legibles, versionables y reutilizables.

**Ubicación**: `.qwen/agents/` (proyecto) + `~/.qwen/agents/` (usuario)

```markdown
---
name: python-expert
description: Expert in Python development, clean architecture, SOLID principles, TDD. Use PROACTIVELY for Python tasks.
model: inherit
tools:
  - read_file
  - write_file
  - read_many_files
  - run_shell_command
---

You are a Senior Python Architect specializing in clean, maintainable code...
```

### 4.2. Delegación Automática vs Explícita

Qwen Code delega tareas a agents de forma **automática** basada en:
- El `description` del agent (cuándo usarlo)
- El contexto de la solicitud del usuario
- Las herramientas disponibles

También se puede invocar **explícitamente**:
```
"Dejá que python-expert cree los tests para el módulo de autenticación"
"Que el documentation-writer actualice el README"
```

### 4.3. Selección de Modelo por Agent

Cada agent puede usar un modelo diferente mediante el campo `model` en el frontmatter:

| Valor | Comportamiento |
|-------|---------------|
| `inherit` (default) | Usa el mismo modelo que la conversación principal |
| `qwen3.6-plus` | Usa ese modelo específico |
| `openai:gpt-4o` | Usa un proveedor diferente |

### 4.4. Convenciones de Nomenclatura

Los agents siguen patrones de especialización clara:

| Agent | Especialización | Tools típicas |
|-------|----------------|---------------|
| `python-expert` | Python, pytest, ruff, mypy | read, write, shell |
| `rust-expert` | Rust, ownership, async, performance | read, write, shell, search |
| `testing-expert` | Tests unitarios, integración, mocking | read, write, shell |
| `documentation-writer` | README, API docs, guías | read, write, web_search |


--------------------------------------------------------------------------------


## 5. Flujos de Trabajo: Spec-Driven Development (SDD)

### 5.1. El Ciclo de Vida de 9 Fases

El SDD obliga a la IA a ser un arquitecto antes que un codificador.

| Fase | Propósito | Tools Qwen Code |
|------|-----------|-----------------|
| Init / Explore | Inicializa e investiga el código | `@{file}`, `grep_search`, `agent` |
| Propose / Spec | Propuesta técnica y requisitos detallados | `read_file`, `write_file` |
| Design / Tasks | Diseño técnico y desglose atómico | `read_many_files`, `write_file` |
| Apply | Implementación del código siguiendo el plan | `edit`, `write_file`, `run_shell_command` |
| Verify / Archive | Validación vs Specs y archivado de deltas | `run_shell_command`, `grep_search` |

### 5.2. Delegación con Agent Tool

Qwen Code delega fases SDD a agents especializados con contextos aislados:

- **Orquestador**: Mantiene conversación principal, delega trabajo real
- **Sub-agents**: Reciben prompt específico, trabajan independientemente, retornan resultados
- **Context isolation**: Cada agent tiene su propia historia de conversación
- **Progress visibility**: Se puede monitorear el progreso en tiempo real

### 5.3. Commands SDD

Los commands SDD se definen como archivos Markdown en `.qwen/commands/`:

```markdown
---
description: Initialize SDD context — detects project stack
---

You are an SDD sub-agent. Read the skill file and follow its instructions...
```

Se invocan como `/sdd-init`, `/sdd-explore`, etc.


--------------------------------------------------------------------------------


## 6. Protocolos de Safe Refactoring y Análisis de Impacto

### 6.1. Detección de Blast Radius

Antes de editar, medí el radio de explosión (Blast Radius).

| Nivel de Riesgo | Profundidad (d) | Significado | Estrategia |
|----------------|----------------|-------------|------------|
| CRITICAL | d=1 | WILL BREAK | Actualización obligatoria de llamadores |
| HIGH | d=2 | LIKELY AFFECTED | Prioridad máxima en el plan de testing |
| MEDIUM | d=3 | MAY NEED TESTING | Verificación en rutas críticas |

### 6.2. Workflow de Rename Coordinado

No uses find-and-replace; es suicidio técnico.

1. Invocá la herramienta MCP rename (no es un comando CLI directo).
2. Configurá `dry_run: true`.
3. Revisá las ediciones de tipo graph (confianza total) y auditá manualmente las de tipo ast_search (búsqueda de texto).
4. Aplicá el cambio solo tras validar el impacto.

### 6.3. Guardias de Seguridad y GGA (Guardian Angel)

GGA es tu gatekeeper. Configurado como un hook de git, valida cada commit contra tus estándares en AGENTS.md. Si el código no cumple la "Ley del Proyecto", el commit se bloquea.


--------------------------------------------------------------------------------


## 7. Mantenimiento y Diagnóstico de Operaciones

### 7.1. Gestión de Índices Estándar y Embeddings

- **Incremental**: `gitnexus analyze` detecta cambios automáticamente.
- **Vectores**: Si el proyecto usa embeddings, pasá siempre el flag `--embeddings`, o se perderán.
- **Limpieza**: Ante corrupción, ejecutá `gitnexus clean` para purgar `.gitnexus/` y LadybugDB.

### 7.2. Resolución de Errores Comunes

- **OOM (Out of Memory)**: GitNexus asigna 8GB por defecto. Para monorepos, elevá el heap: `NODE_OPTIONS="--max-old-space-size=16384"`.
- **LadybugDB Busy**: Ocurre por un bloqueo de escritor único (single-writer lock). Asegurate de cerrar procesos de MCP u otras instancias de analyze antes de reintentar.
- **Stale Index**: Si el grafo no coincide con el HEAD de Git, ejecutá `gitnexus status` y re-indexá.

### 7.3. Comandos Qwen Code Relevantes

| Comando | Propósito |
|---------|-----------|
| `/agents manage` | Ver y gestionar agents especializados |
| `/skills` | Listar y ejecutar skills disponibles |
| `/tools` | Mostrar herramientas disponibles |
| `/mcp` | Listar servidores MCP configurados |
| `/context` | Mostrar uso de ventana de contexto |
| `/compress` | Comprimir historial para ahorrar tokens |

### 7.4. Sistema de Backup y Rollback

Gentle AI genera snapshots tar.gz automáticos. Cada backup incluye un `manifest.json` que registra si un archivo existía previamente (`existed=false`). Esto permite que el rollback no solo restaure versiones viejas, sino que limpie físicamente archivos creados por una instalación fallida.


--------------------------------------------------------------------------------

*Arquitecto Jefe de Sistemas de Inteligencia de Código — Ecosistema Stark 2026 — Conciencia estructural total.*
