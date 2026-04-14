# Manual de Arquitectura y Configuración: Ecosistema de Desarrollo Orquestado

Escuchame bien: si alguna vez sentiste que tu agente de IA está "tirando fruta" o rompiendo dependencias que no vio venir, es porque estás operando bajo ceguera arquitectónica (architectural blindness). Un agente sin contexto relacional es como un cirujano operando a oscuras; va a hacer blind edits que compilan, sí, pero que destruyen la integridad del sistema a largo plazo.

Este manual no es una simple guía de instalación. Es la base técnica del ecosistema de Gentleman Programming, donde orquestamos Qwen Code (el ejecutor), Gentle-AI (el configurador de estado) y GitNexus (el grafo de conocimiento) para que tu flujo de trabajo sea quirúrgico.

--------------------------------------------------------------------------------

## 1. Visión General del Ecosistema Orquestado

La sinergia entre nuestras herramientas no es casualidad. Mientras que la mayoría se conforma con búsquedas basadas en grep o RAG vectorial básico, nosotros usamos inteligencia relacional.

- **GitNexus** precomputa un mapa arquitectónico usando el algoritmo de detección de comunidades de Leiden. No ve archivos; ve clústeres funcionales.
- **Qwen Code** consume este grafo para razonar antes de tocar una sola línea.
- **Gentle-AI** inyecta la lógica de Spec-Driven Development (SDD) para que el agente planee antes de ejecutar.

El impacto en tu laburo es real:

- **Reducción de tokens**: Pasamos de leer archivos secuencialmente a consultar el grafo. Hablamos de una reducción de 120x en el consumo de tokens.
- **Latencia**: Las consultas estructurales tardan <1ms, comparado con los segundos de una búsqueda tradicional.

--------------------------------------------------------------------------------

## 2. Gentle-AI: El Orquestador de Instalación y Estado

Fijate que Gentle-AI no es un instalador de paquetes común. Es un configurador de estado que garantiza la idempotencia del ecosistema. Si algo falla, podés re-ejecutarlo y solo va a corregir lo que esté desviado.

### 2.1. Perfiles de Instalación

Podés elegir qué tan profundo querés que sea el "tunning" de tu entorno:

| Perfil | Descripción |
|--------|-------------|
| `full-gentleman` | El pack completo: Engram, SDD, habilidades MCP, y el overlay de personalidad "Gentleman" (el mentor que te empuja a ser mejor). |
| `ecosystem-only` | Solo los componentes técnicos. Ideal si ya tenés tu propia personalidad configurada pero querés el cerebro del SDD. |

### 2.2. Verificación de Requisitos (Idempotencia)

Antes de mover un dedo, el configurador verifica tus dependencias. Tené en cuenta las versiones mínimas:

| Dependencia | Versión Mín. | Motivo Arquitectónico |
|-------------|-------------|----------------------|
| Node.js | 20+ | Requisito para Qwen Code |
| Git | 2.x | Necesario para el mapeo de diffs y hooks de sincronización |
| Go | 1.24+ | Crítico para buildear Engram y manejar la concurrencia de LadybugDB |
| Package Managers | N/A | Homebrew (macOS/Linux), Apt, Pacman, Dnf o Winget en Windows |

--------------------------------------------------------------------------------

## 3. Arquitectura de Prompts Compartidos (Shared Prompt Architecture)

Para que no tengas un archivo de configuración de cinco mil líneas que sea un dolor de cabeza mantener, usamos una arquitectura desacoplada basada en archivos Markdown dentro de `.qwen/`.

### 3.1. La Regla de Oro del Orquestador

Mirá bien esta distinción porque es donde muchos le pifian:

1. **Prompts de Sub-agents**: Se definen en `.qwen/agents/` como archivos Markdown con frontmatter YAML. Cada agent tiene su propio system prompt.
2. **Commands**: Se definen en `.qwen/commands/` como archivos Markdown con frontmatter YAML. Se invocan con `/nombre` o `/namespace:accion`.
3. **Skills**: Se definen en `.qwen/skills/` como directorios con `SKILL.md`. El modelo los invoca automáticamente cuando detecta el contexto.

### 3.2. Estructura de Directorios

```
.qwen/
├── QWEN.md              # Reglas del proyecto (persona, convenciones)
├── system.md            # Protocolos de memoria (Engram)
├── settings.json        # Configuración de modelos y providers
├── agents/              # Agents especializados (sub-agentes)
│   ├── python-expert.md
│   ├── rust-expert.md
│   └── rust-tester.md
├── commands/            # Commands invocables con /
│   ├── sdd-init.md
│   ├── sdd-explore.md
│   ├── sdd-apply.md
│   ├── sdd-verify.md
│   └── ...
└── skills/              # Skills auto-invocables por el modelo
    ├── sdd-init/
    │   └── SKILL.md
    ├── sdd-apply/
    │   └── SKILL.md
    └── ...
```

### 3.3. Formato de Agents

```markdown
---
name: agent-name
description: Cuándo usar este agente. Incluir "Use PROACTIVELY" para delegación automática.
model: inherit
tools:
  - read_file
  - write_file
  - run_shell_command
---

System prompt content goes here...
```

### 3.4. Formato de Commands

```markdown
---
description: Descripción del command (se muestra en /help)
agent: nombre-del-agent
subtask: true
---

Prompt content with {{args}}, @{file}, and !{command} injections...
```

--------------------------------------------------------------------------------

## 4. Configuración de Agents en Qwen Code

En Qwen Code, los agents se configuran mediante archivos Markdown — no JSON. Esto permite versionado, diffs legibles y colaboración.

### 4.1. Ubicaciones y Precedencia

| Nivel | Ruta | Precedencia |
|-------|------|-------------|
| Proyecto | `.qwen/agents/` | Mayor (override todo) |
| Usuario | `~/.qwen/agents/` | Media (fallback personal) |
| Extensión | `<ext>/agents/` | Baja (proporcionado por extensiones) |

### 4.2. Ejemplo: Agent de Desarrollo Python

```markdown
---
name: python-expert
description: Expert in Python development, clean architecture, SOLID, TDD. Use PROACTIVELY for Python tasks, refactoring, and architecture design.
model: inherit
tools:
  - read_file
  - write_file
  - read_many_files
  - run_shell_command
---

You are a Senior Python Architect specializing in clean, maintainable, and type-safe Python code following 2025/2026 best practices.

## Your Expertise
- Clean Architecture: Layered design with Dependency Rule
- SOLID Principles: Single Responsibility, Open/Closed, Liskov, Interface Segregation, Dependency Inversion
- Testing: TDD (Red-Green-Refactor), pytest, mocking
- Type Safety: Type hints, mypy strict mode, pydantic for runtime validation
```

### 4.3. Ejemplo: Agent de Testing Rust

```markdown
---
name: rust-tester
description: Expert in Rust testing following 2025-26 best practices. PROACTIVELY use for any Rust testing task including unit tests, async tests, property-based testing, and mocking.
model: inherit
tools:
  - read_file
  - write_file
  - read_many_files
  - run_shell_command
---

You are a Senior Rust Testing Engineer specializing in modern testing patterns...
```

### 4.4. Delegación: Automática vs Explícita

| Modo | Cómo funciona | Ejemplo |
|------|--------------|---------|
| **Automática** | Qwen Code detecta coincidencia entre `description` del agent y la tarea | Usuario: "Escribí tests para el módulo de auth" → delega a testing agent |
| **Explícita** | Usuario menciona el agent por nombre | "Dejá que python-expert refactorice este módulo" |

Para habilitar delegación proactiva, incluir en el `description`:
- `"Use PROACTIVELY for..."`
- `"MUST BE USED when..."`

--------------------------------------------------------------------------------

## 5. GitNexus: El Substrato de Inteligencia Estructural

GitNexus es el que realmente conoce tu código. Su binario soporta 35 lenguajes y utiliza un servidor MCP para exponer herramientas críticas a los agents.

### 5.1. Herramientas Críticas de Contexto

Instruí a tus agents para que nunca editen sin consultar:

1. **query**: Búsqueda híbrida (BM25 + Semántica) que usa RRF (Reciprocal Rank Fusion) para ordenar resultados. Lo más importante: los resultados vienen agrupados por procesos de ejecución, no por archivos sueltos.
2. **impact**: Análisis de blast radius.

   - Niveles: d=1 (ruptura inmediata), d=2 (indirectos), d=3 (transitivos).
   - Puntaje de Confianza (0.0 a 1.0): Si una relación tiene confianza < 0.5, el agent debe ignorarla o pedir validación manual.

3. **detect_changes**: Antes de commitear, mapea los diffs de Git a los símbolos afectados. Si el agent cambió algo que no debía, acá salta la ficha.

### 5.2. Integración con Qwen Code

GitNexus se expone como servidor MCP. Qwen Code accede a las herramientas de GitNexus a través del protocolo MCP:

```bash
/mcp          # Ver servers MCP conectados
/tools        # Ver herramientas disponibles (incluye GitNexus tools)
```

Los agents con `run_shell_command` también pueden invocar GitNexus directamente:

```bash
npx gitnexus query "auth validation flow"
npx gitnexus impact --target "validateUser" --direction upstream
```

--------------------------------------------------------------------------------

## 6. Protocolo de Safe Refactoring y Sincronización de Memoria

### 6.1. Refactorización Quirúrgica

Si vas a renombrar un símbolo, prohibí el "find-and-replace" tradicional. El protocolo exige:

1. Usar `gitnexus_rename` con `dry_run: true`.
2. Revisión Crítica: Diferenciá entre `graph edits` (alta confianza, basados en el grafo) y `ast_search edits` (baja confianza, simples coincidencias de texto). Estas últimas se revisan con lupa.

### 6.2. Engram: El Cerebro Compartido

Engram asegura que si tomaste una decisión arquitectónica en una sesión, el agente la recuerde en la siguiente.

- **Persistence**: Se guarda en `~/.engram/engram.db`.
- **Health Check**: Verificá siempre el puerto 7437.
- **Operaciones**: Usá `mem_save` para registrar convenciones y `mem_search` para recuperarlas.

### 6.3. Comandos Engram

```bash
engram projects list          # Ver proyectos con contadores de memoria
engram projects consolidate   # Fix name drift
engram search "auth bug"      # Buscar decisiones pasadas
engram tui                    # Navegador visual
```

--------------------------------------------------------------------------------

## 7. Mantenimiento y Troubleshooting de la Arquitectura

Para mantener los prompts y habilidades alineados con las actualizaciones de Gentleman Programming, ejecutá periódicamente `gentle-ai sync`.

### 7.1. Signos de Falla (Patterns de Error)

Si el ecosistema se comporta raro, buscá estos patrones:

| Sign | Trigger | Instruction | Reason |
|------|---------|-------------|--------|
| Grafo desactualizado | Los resultados de búsqueda no reflejan los últimos cambios | Ejecutá `npx gitnexus analyze` | Las herramientas consultan LadybugDB, que es estática hasta la re-indexación |
| Desvanecimiento de Embeddings | La búsqueda semántica se vuelve inútil | `npx gitnexus analyze --embeddings` | La generación de vectores es optativa y se pierde sin el flag |
| Bloqueo de LadybugDB | Error "database busy" | Cerrá procesos de indexación o MCP concurrentes | Solo un proceso puede escribir a la vez |

### 7.2. Commands de Mantenimiento Qwen Code

| Command | Propósito |
|---------|-----------|
| `/agents manage` | Ver y gestionar agents |
| `/skills` | Listar y gestionar skills |
| `/context` | Ver uso de ventana de contexto |
| `/compress` | Comprimir historial de conversación |
| `/model` | Cambiar modelo en sesión |
| `/mcp` | Ver servidores MCP |
| `/tools` | Ver herramientas disponibles |

--------------------------------------------------------------------------------

## 8. Gobernanza y Guardrails del Desarrollador

Este ecosistema se rige por la licencia PolyForm Noncommercial 1.0.0. Como arquitecto, tenés que hacer cumplir estas reglas no negociables:

1. **Commit de Secretos**: Prohibido terminantemente. Usá `.env.example`.
2. **Análisis de Impacto**: Obligatorio antes de tocar cualquier símbolo compartido por otros módulos.
3. **Preservación de Grafo**: Verificá siempre el `meta.json`. Si los embeddings son 0, el agente está alucinando semánticamente.

### 8.1. Protocolo de Escalación (Cuándo parar)

Detené la automatización y pedí intervención humana si:

- El análisis de impacto muestra riesgos HIGH o CRITICAL fuera del scope de la tarea actual.
- Hay un conflicto insoluble entre la velocidad de análisis y la integridad de los datos en repositorios gigantes.
- Se requiere modificar configuraciones de seguridad sensible o infraestructura de CI.

Mirá, la herramienta es potente, pero el criterio es tuyo. No dejes que la IA maneje sin cinturón de seguridad. ¡A laburar!
