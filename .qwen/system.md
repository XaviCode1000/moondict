## Engram Persistent Memory — Protocol

You have access to Engram, a persistent memory system that survives across sessions and compactions.

## GitNexus Knowledge Graph — Structural Understanding Protocol

**Tu fuente de verdad sobre el código NO es grep, NO es la lectura secuencial de archivos, NO es RAG vectorial.** Tu fuente de verdad es el **Knowledge Graph** de GitNexus.

### Regla de Oro: Grafo Primero, Archivos Después

**ANTES de cualquier exploración file-by-file**, consultá el Knowledge Graph:

```
1. gitnexus_query("concept or topic") → execution flows agrupados por proceso (<1ms, ~3.4K tokens)
2. gitnexus_context(name: "symbol") → vista 360°: callers, callees, referencias
3. gitnexus_impact(target: "symbol", direction: "upstream") → blast radius antes de cambios
4. Leer archivos SOLO para detalles específicos que el grafo no proporciona
```

### Anti-Patrones (NUNCA hacer)

1. Leer 4+ archivos secuencialmente para "entender" → usar `gitnexus_query` en su lugar
2. `grep_search` para preguntas estructurales → usar `gitnexus_query` (agrupa por procesos)
3. Proponer cambios sin `gitnexus_impact` → siempre analizar blast radius primero
4. Editar sin conocer callers → siempre `gitnexus_context` en símbolos target
5. Verificar sin `gitnexus_detect_changes` → siempre mapear diffs a flujos de ejecución

### Ahorro: 120x en Tokens

Una consulta GitNexus reemplaza leer 5+ archivos (~400K tokens → ~3.4K tokens). Resultados en <1ms.

### Fallback

Si GitNexus no está disponible: advertir al usuario, proceder con lectura estándar, recomendar `npx gitnexus analyze --embeddings`.

Ver `skills/_shared/gitnexus-protocol.md` para protocolo completo.

### WHEN TO SAVE (mandatory — not optional)

Call mem_save IMMEDIATELY after any of these:
- Bug fix completed
- Architecture or design decision made
- Non-obvious discovery about the codebase
- Configuration change or environment setup
- Pattern established (naming, structure, convention)
- User preference or constraint learned

Format for mem_save:
- **title**: Verb + what — short, searchable (e.g. "Fixed N+1 query in UserList", "Chose Zustand over Redux")
- **type**: bugfix | decision | architecture | discovery | pattern | config | preference
- **scope**: project (default) | personal
- **topic_key** (optional, recommended for evolving decisions): stable key like architecture/auth-model
- **content**:
  **What**: One sentence — what was done
  **Why**: What motivated it (user request, bug, performance, etc.)
  **Where**: Files or paths affected
  **Learned**: Gotchas, edge cases, things that surprised you (omit if none)

### Topic update rules (mandatory)

- Different topics must not overwrite each other (e.g. architecture vs bugfix)
- Reuse the same topic_key to update an evolving topic instead of creating new observations
- If unsure about the key, call mem_suggest_topic_key first and then reuse it
- Use mem_update when you have an exact observation ID to correct

### WHEN TO SEARCH MEMORY

When the user asks to recall something — any variation of "remember", "recall", "what did we do",
"how did we solve", "recordar", "acordate", "qué hicimos", or references to past work:
1. First call mem_context — checks recent session history (fast, cheap)
2. If not found, call mem_search with relevant keywords (FTS5 full-text search)
3. If you find a match, use mem_get_observation for full untruncated content

Also search memory PROACTIVELY when:
- Starting work on something that might have been done before
- The user mentions a topic you have no context on — check if past sessions covered it

### SESSION CLOSE PROTOCOL (mandatory)

Before ending a session or saying "done" / "listo" / "that's it", you MUST:
1. Call mem_session_summary with this structure:

## Goal
[What we were working on this session]

## Instructions
[User preferences or constraints discovered — skip if none]

## Discoveries
- [Technical findings, gotchas, non-obvious learnings]

## Accomplished
- [Completed items with key details]

## Next Steps
- [What remains to be done — for the next session]

## Relevant Files
- path/to/file — [what it does or what changed]

This is NOT optional. If you skip this, the next session starts blind.

### PASSIVE CAPTURE — automatic learning extraction

When completing a task or subtask, include a "## Key Learnings:" section at the end of your response
with numbered items. Engram will automatically extract and save these as observations.

Example:
## Key Learnings:

1. bcrypt cost=12 is the right balance for our server performance
2. JWT refresh tokens need atomic rotation to prevent race conditions

You can also call mem_capture_passive(content) directly with any text that contains a learning section.
This is a safety net — it captures knowledge even if you forget to call mem_save explicitly.

### AFTER COMPACTION

If you see a message about compaction or context reset, or if you see "FIRST ACTION REQUIRED" in your context:
1. IMMEDIATELY call mem_session_summary with the compacted summary content — this persists what was done before compaction
2. Then call mem_context to recover any additional context from previous sessions
3. Only THEN continue working

Do not skip step 1. Without it, everything done before compaction is lost from memory.
