# Manual de Operaciones Técnicas: Estrategia de Ejecución y Configuración de Prompts (Stark Ecosystem)

Este manual establece los protocolos operativos de alto nivel para la integración de Qwen Code y GitNexus. Como Arquitectos de Inteligencia, nuestro objetivo es erradicar la "ceguera arquitectónica" y transformar la asistencia probabilística en la ejecución de sistemas determinista y de alta precisión.


--------------------------------------------------------------------------------


## 1. Fundamentos del Ecosistema Stark: Comprensión Estructural y Delegación Inteligente

El ecosistema Stark no opera sobre fragmentos aislados, sino sobre un Sustrato Relacional. Resolvemos las limitaciones de los LLMs tradicionales mediante dos pilares:

- **Structural Understanding (Comprensión Estructural)**: Combatimos la "ceguera arquitectónica" y los "blind edits" (ediciones ciegas) mediante un grafo de conocimiento pre-calculado. Utilizamos el algoritmo de detección de comunidades de Leiden para resolver la inteligencia relacional antes de que el modelo realice la primera consulta, eliminando el problema de "lost in the middle" característico de los RAGs basados en vectores.
- **Intelligent AI Delegation (Delegación Inteligente)**: El sistema actúa como una Máquina de Estados Basada en Artefactos. Reconocemos que el chat no es un medio de almacenamiento confiable; por lo tanto, la memoria del sistema reside en el sistema de archivos, delegando tareas a agents especializados que operan bajo contextos limpios y específicos.

### RAG Tradicional vs. Sustrato Relacional (GitNexus)

| Característica | RAG Basado en Snippets (Tradicional) | Grafo de Conocimiento (GitNexus) |
|---------------|--------------------------------------|----------------------------------|
| Naturaleza | Búsqueda probabilística por similitud. | Mapa relacional determinista (AST). |
| Contexto | Fragmentos de texto plano (pérdida de jerarquía). | Conexiones de llamadas, herencia e importaciones. |
| Resolución | Basada en palabras clave/vectores. | Sustrato relacional resuelto via Leiden. |
| Riesgo | Ediciones ciegas y alucinaciones estructurales. | Análisis de impacto y precisión arquitectónica. |


--------------------------------------------------------------------------------


## 2. El Motor de Inteligencia: GitNexus y LadybugDB

La eficiencia del ecosistema radica en LadybugDB, un motor de base de datos de grafos embebido que utiliza KuzuDB para la ejecución en CLI y implementaciones WASM para la interfaz web. El motor de parsing subyacente es Tree-sitter, lo que garantiza una extracción de símbolos precisa en 14+ lenguajes.

La transición de búsquedas basadas en grep a consultas directas al grafo genera una reducción de tokens de 120x:

- **Búsqueda tradicional (file-by-file)**: ~412,000 tokens para 5 consultas estructurales.
- **Consulta GitNexus (Knowledge Graph)**: ~3,400 tokens para el mismo alcance.
- **Latencia**: <1ms en consultas locales.
- **Arquitectura**: Local-first con propiedad de proceso único (single-process ownership).


--------------------------------------------------------------------------------


## 3. Ciclo de Vida SDD: Estrategia de Ejecución en Qwen Code

El flujo de Spec-Driven Development (SDD) es un proceso estrictamente secuencial diseñado para evitar la degradación del contexto.

| Fase | Acción Principal | Tools Qwen Code | Resultado Esperado |
|------|-----------------|-----------------|-------------------|
| sdd-explore | Investigación profunda de la arquitectura. | `query`, `context`, `@{file}` | Comprensión del flujo de ejecución y dependencias. |
| sdd-propose | Definición de intención y alcance técnico. | `impact` (d=2) | Propuesta validada estructuralmente (Blast Radius). |
| sdd-apply | Implementación de cambios en el código. | `rename` (dry_run), `edit` | Modificaciones precisas en el árbol de archivos. |
| sdd-verify | Validación de la implementación vs spec. | `detect_changes`, `run_shell_command` | Confirmación de integridad post-cambio. |

**Nota de Arquitecto**: El orden de actualización es innegociable para mantener la validez del código: Interfaces/Types → Implementaciones → Callers → Tests.


--------------------------------------------------------------------------------


## 4. Configuración de Agents Especializados en Qwen Code

Qwen Code permite agents especializados mediante archivos Markdown con frontmatter YAML. Es crítico entender que cada agent tiene su propio contexto aislado y su propia lista de tools disponibles.

### 4.1. Estructura de un Agent

```markdown
---
name: python-expert
description: Expert in Python development, clean architecture, SOLID, TDD. Use PROACTIVELY for Python tasks.
model: inherit
tools:
  - read_file
  - write_file
  - read_many_files
  - run_shell_command
---

You are a Senior Python Architect specializing in clean, maintainable code...
```

### 4.2. Ubicaciones de Agents (precedencia)

| Nivel | Ruta | Alcance |
|-------|------|---------|
| Proyecto | `.qwen/agents/` | Solo este proyecto (mayor precedencia) |
| Usuario | `~/.qwen/agents/` | Todos los proyectos del usuario |
| Extensión | `<extensión>/agents/` | Proporcionados por extensiones |

### 4.3. Selección de Modelo por Agent

Cada agent puede usar un modelo diferente:

```yaml
model: inherit        # Usa el modelo de la conversación principal
model: qwen3.6-plus   # Usa modelo específico
model: openai:gpt-4o  # Usa proveedor diferente
```

### 4.4. Delegación Proactiva

Para que Qwen Code delegue automáticamente, incluí en el `description`:
- `"Use PROACTIVELY for..."` — delegación automática cuando detecta el contexto
- `"MUST BE USED when..."` — delegación obligatoria para ese tipo de tarea


--------------------------------------------------------------------------------


## 5. Arquitectura de Prompts Compartidos (Shared Prompt Architecture)

Para evitar la polución de archivos de configuración, externalizamos las instrucciones en archivos Markdown dentro de `.qwen/`.

### 5.1. Commands (`.qwen/commands/`)

Los commands SDD se definen como archivos Markdown con frontmatter YAML:

```markdown
---
description: Initialize SDD context — detects project stack
agent: sdd-orchestrator
subtask: true
---

You are an SDD sub-agent. Read the skill file and follow its instructions...
```

Se invocan como `/sdd-init`, `/sdd-explore`, `/sdd-apply`, etc.

### 5.2. Skills (`.qwen/skills/`)

Cada skill es un directorio con `SKILL.md` que contiene:

```yaml
---
name: sdd-apply
description: Implement tasks from the change, writing actual code following the specs and design.
license: MIT
metadata:
  author: gentleman-programming
  version: "3.0"
---

## Purpose
...
```

Se invocan automáticamente cuando el modelo detecta el contexto, o explícitamente con `/skills <nombre>`.

### 5.3. Inyección de Contenido en Commands

Qwen Code soporta tres tipos de inyección dinámica:

| Tipo | Sintaxis | Procesamiento | Ejemplo |
|------|----------|---------------|---------|
| Parámetros | `{{args}}` | Inyección de usuario | `Analyze {{args}}` |
| Archivos | `@{file}` | Inyección de contenido | `Standards: @{docs/code-standards.md}` |
| Shell | `!{command}` | Ejecución de comando | `Changes: !{git diff --staged}` |

### 5.4. Beneficios

1. **Mantenibilidad**: Edición centralizada de lógica de agents y commands.
2. **Modularidad**: Agents reutilizables entre proyectos vía `~/.qwen/agents/`.
3. **Versionabilidad**: Todo es Markdown + YAML, commiteable en git.
4. **Legibilidad**: No hay JSONs complejos; archivos legibles por humanos.


--------------------------------------------------------------------------------


## 6. Protocolo de Refactorización Segura (Safe Refactoring)

Todo refactor estructural debe seguir este protocolo para mitigar riesgos de regresión silenciosa:

1. **Impact Analysis (Upstream)**: Ejecutar `impact` con profundidad d=2 para evaluar el radio de explosión.
2. **Planificación de Orden**: Seguir estrictamente: Interfaces → Implementaciones → Callers → Tests.
3. **Ejecución con rename**: Utilizar la herramienta rename con `dry_run: true`.
4. **Auditoría de Ediciones**: Revisar manualmente las ediciones de `ast_search` (basadas en texto), ya que tienen menor confianza que las `graph edits` (basadas en el grafo).
5. **Validación**: Correr `detect_changes` para asegurar que el alcance de la modificación coincide con el plan original.


--------------------------------------------------------------------------------


## 7. Análisis de Impacto y Precisión Arquitectónica

Categorizamos el riesgo de cambio según la profundidad de la dependencia en el grafo:

- **Depth 1 (d=1) — CRITICAL**: Dependencias directas. El cambio ROMPERÁ el sistema inmediatamente si no se actualizan los llamadores.
- **Depth 2 (d=2) — HIGH**: Dependencias indirectas. Áreas LIKELY AFFECTED (probablemente afectadas). Es el estándar mínimo de revisión para cualquier refactorización segura.
- **Depth 3 (d=3) — LOW**: Dependencias transitivas. Áreas que MAY NEED TESTING (podrían requerir pruebas) si se encuentran en rutas críticas de negocio.


--------------------------------------------------------------------------------


## 8. Directrices de Mantenimiento y Actualización de la Inteligencia

El grafo de conocimiento debe estar sincronizado con el HEAD de Git para evitar "Stale Indexes".

### 8.1. Sincronización GitNexus

- **Análisis**: `npx gitnexus analyze`
- **Preservación de Vectores**: Si el proyecto requiere búsqueda semántica, es obligatorio el uso de `--embeddings`. Un analyze plano eliminará los vectores existentes.
- **Propiedad del Proceso**: LadybugDB requiere single-process ownership. No ejecutá analyze mientras el servidor MCP está realizando escrituras activas.

### 8.2. Troubleshooting: Señales de Alerta

| Trigger (Señal) | Instruction | Razón |
|----------------|-------------|-------|
| Advertencia de "Stale Index" | Ejecutar `npx gitnexus analyze` | Los cambios en Git son invisibles para LadybugDB hasta el re-indexado. |
| La calidad de búsqueda semántica cae | `npx gitnexus analyze --embeddings` | La generación de embeddings es optativa; un análisis estándar borra los vectores previos. |
| Error "Database busy" | Detener procesos concurrentes | La DB embebida espera propiedad de un solo proceso sobre el almacenamiento. |
| El MCP no lista repositorios | Ejecutar `analyze` para poblar `registry.json` | El servidor descubre repositorios a través del registro global. |

### 8.3. Commands de Mantenimiento Qwen Code

| Comando | Propósito |
|---------|-----------|
| `/agents manage` | Ver agents configurados |
| `/skills` | Listar y gestionar skills |
| `/context` | Ver uso de tokens |
| `/compress` | Comprimir historial de chat |
| `/tools` | Ver herramientas disponibles |


--------------------------------------------------------------------------------


## 9. Conclusión: El Futuro del Desarrollo Agéntico con Stark

La integración de SDD, GitNexus y Qwen Code trasciende la mera "escritura de código". Al operar sobre un Sustrato Relacional, el desarrollador evoluciona de un ejecutor de tareas a un Orquestador de Sistemas.

Este enfoque garantiza la soberanía de los datos (local-first) y reemplaza las conjeturas probabilísticas por una Ejecución Determinista. El futuro del desarrollo no es más código, es mejor arquitectura.

