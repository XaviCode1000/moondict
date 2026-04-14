# GitNexus Protocol — Protocolo de Inteligencia Relacional para Fases SDD

## Filosofía

Tu fuente de verdad sobre el código **NO es grep, NO es la lectura secuencial de archivos, NO es RAG vectorial**. Tu fuente de verdad es el **Knowledge Graph** de GitNexus — un sustrato relacional pre-computado que conoce cada función, cada llamada, cada proceso de ejecución.

Una consulta al grafo reemplaza leer 5+ archivos secuencialmente, ahorra ~400K tokens y devuelve resultados en <1ms.

## Regla de Oro

**PROHIBIDO hacer exploración file-by-file a ciegas.** Siempre consultá el Knowledge Graph primero. GitNexus proporciona inteligencia relacional (calls, imports, extends, implements, process flows) que grep y RAG no pueden igualar.

## Herramientas GitNexus MCP Disponibles

| Herramienta | Propósito | Cuándo Usar |
|-------------|-----------|-------------|
| `gitnexus_query` | Búsqueda híbrida (BM25 + semántica) agrupada por procesos de ejecución | Entender cómo funciona el código junto, encontrar flujos de ejecución |
| `gitnexus_context` | Vista 360° de un símbolo (callers, callees, referencias categorizadas) | Entender a fondo una función/clase/interfaz específica |
| `gitnexus_impact` | Análisis de blast radius (d=1 ROMPERÁ, d=2 PROBABLEMENTE AFECTADO, d=3 PODRÍA NECESITAR TESTING) | Antes de proponer o implementar cambios |
| `gitnexus_detect_changes` | Mapea diffs de git no commiteados a flujos de ejecución afectados | Después de implementar, antes de commit/verify |
| `gitnexus_cypher` | Query Cypher directo contra el knowledge graph | Consultas estructurales complejas que query/explore no resuelven |
| `gitnexus_rename` | Rename coordinado multi-archivo con tagging de confianza | Renombrar funciones, clases, variables en todo el codebase |
| `gitnexus_api_impact` | Reporte de impacto pre-cambio para API route handlers | Antes de modificar handlers de API |
| `gitnexus_route_map` | Mapeo de rutas API (consumidores, handlers, middleware) | Entender patrones de consumo de API |
| `gitnexus_tool_map` | Definiciones y handlers de herramientas MCP/RPC | Entender APIs de herramientas |
| `gitnexus_shape_check` | Verificar shapes de respuesta API vs accesos de consumidores | Detectar shape drift en respuestas API |
| `gitnexus_list_repos` | Listar repositorios indexados | Cuando hay múltiples repos, para targetear el correcto |

## Reglas de Confianza

| Score de Confianza | Acción |
|-------------------|--------|
| >= 0.8 | Alta confianza — seguro confiar en esta relación |
| 0.5 - 0.79 | Confianza media — verificar con lectura de código |
| < 0.5 | Baja confianza — tratar como pista, verificar manualmente |

## Anti-Patrones (NUNCA hacer esto)

1. **Leer 4+ archivos secuencialmente para "entender"** → delegar un `gitnexus_query` en su lugar
2. **`grep_search` para preguntas estructurales** → usar `gitnexus_query` (agrupa por procesos)
3. **Proponer cambios sin análisis de impacto** → siempre ejecutar `gitnexus_impact` primero
4. **Editar sin conocer los callers** → siempre ejecutar `gitnexus_context` en los símbolos target
5. **Verificar sin `detect_changes`** → siempre mapear diffs a flujos de ejecución

## Protocolo de Fallback

Si GitNexus no está disponible (no indexado, no instalado, o error):
1. Advertir al usuario: "GitNexus no disponible — fallback a exploración basada en archivos"
2. Proceder con lectura estándar de archivos y `grep_search`
3. Recomendar: `npx gitnexus analyze --embeddings` para habilitar capacidades completas

## Presupuesto de Tokens

Cada llamada a GitNexus cuesta ~3.4K tokens (vs ~400K para lectura file-by-file equivalente). Usarlas generosamente — son la forma más barata y precisa de entender el código.
