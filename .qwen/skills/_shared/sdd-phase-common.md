# SDD Phase — Common Protocol

Boilerplate identical across all SDD phase skills. Sub-agents MUST load this alongside their phase-specific SKILL.md.

Executor boundary: every SDD phase agent is an EXECUTOR, not an orchestrator. Do the phase work yourself. Do NOT launch sub-agents, do NOT call `delegate`/`task`, and do NOT bounce work back unless the phase skill explicitly says to stop and report a blocker.

## A. Skill Loading

1. Check if the orchestrator injected a `## Project Standards (auto-resolved)` block in your launch prompt. If yes, follow those rules — they are pre-digested compact rules from the skill registry. **Do NOT read any SKILL.md files.**
2. If no Project Standards block was provided, check for `SKILL: Load` instructions. If present, load those exact skill files.
3. If neither was provided, search for the skill registry as a fallback:
   a. `mem_search(query: "skill-registry", project: "{project}")` — if found, `mem_get_observation(id)` for full content
   b. Fallback: read `.atl/skill-registry.md` from the project root if it exists
   c. From the registry's **Compact Rules** section, apply rules whose triggers match your current task.
4. If no registry exists, proceed with your phase skill only.

NOTE: the preferred path is (1) — compact rules pre-injected by the orchestrator. Paths (2) and (3) are fallbacks for backwards compatibility. Searching the registry is SKILL LOADING, not delegation. If `## Project Standards` is present, IGNORE any `SKILL: Load` instructions — they are redundant.

## A1. GitNexus Protocol (Structural Understanding)

**BEFORE any file-by-file exploration**, load and follow the GitNexus protocol from `skills/_shared/gitnexus-protocol.md`.

**Rule of thumb**: if you need to understand how code works together (calls, imports, processes), query the Knowledge Graph first. GitNexus saves ~400K tokens per structural query vs file-by-file reading and returns in <1ms.

**Phase-specific GitNexus usage** (see `gitnexus-protocol.md` for full tool catalog):

| Phase | GitNexus Tools |
|-------|---------------|
| sdd-explore | `query` → find execution flows; `context` → deep dive symbols; `cypher` → complex structural queries |
| sdd-propose | `impact` (d=2) → blast radius before writing proposal |
| sdd-design | `query` → existing patterns; `context` → entry points; `route_map` → if API changes |
| sdd-tasks | `impact` (direction=downstream) → understand dependency order |
| sdd-apply | `context` → understand patterns before writing; `query` → find similar implementations |
| sdd-verify | `detect_changes` → map diffs to affected execution flows |
| sdd-archive | `status` → ensure index matches HEAD before archiving |
| sdd-init | `list_repos` → check if project indexed; recommend `npx gitnexus analyze --embeddings` if not |

**Anti-patterns (NEVER)**:
1. Read 4+ files sequentially to "understand" → use `gitnexus_query` instead
2. `grep_search` for structural questions → use `gitnexus_query`
3. Propose changes without `gitnexus_impact` → always analyze blast radius first
4. Edit without knowing callers → always `gitnexus_context` on target symbols
5. Verify without `detect_changes` → always map diffs to execution flows

**Fallback**: If GitNexus is not available (not indexed, not installed, error), warn the user and fall back to file-based exploration. Recommend `npx gitnexus analyze --embeddings`.

## B. Artifact Retrieval (Engram Mode)

**CRITICAL**: `mem_search` returns 300-char PREVIEWS, not full content. You MUST call `mem_get_observation(id)` for EVERY artifact. **Skipping this produces wrong output.**

**Run all searches in parallel** — do NOT search sequentially.

```
mem_search(query: "sdd/{change-name}/{artifact-type}", project: "{project}") → save ID
```

Then **run all retrievals in parallel**:

```
mem_get_observation(id: {saved_id}) → full content (REQUIRED)
```

Do NOT use search previews as source material.

## C. Artifact Persistence

Every phase that produces an artifact MUST persist it. Skipping this BREAKS the pipeline — downstream phases will not find your output.

### Engram mode

```
mem_save(
  title: "sdd/{change-name}/{artifact-type}",
  topic_key: "sdd/{change-name}/{artifact-type}",
  type: "architecture",
  project: "{project}",
  content: "{your full artifact markdown}"
)
```

`topic_key` enables upserts — saving again updates, not duplicates.

### OpenSpec mode

File was already written during the phase's main step. No additional action needed.

### Hybrid mode

Do BOTH: write the file to the filesystem AND call `mem_save` as above.

### None mode

Return result inline only. Do not write any files or call `mem_save`.

## D. Return Envelope

Every phase MUST return a structured envelope to the orchestrator:

- `status`: `success`, `partial`, or `blocked`
- `executive_summary`: 1-3 sentence summary of what was done
- `detailed_report`: (optional) full phase output, or omit if already inline
- `artifacts`: list of artifact keys/paths written
- `next_recommended`: the next SDD phase to run, or "none"
- `risks`: risks discovered, or "None"
- `skill_resolution`: how skills were loaded — `injected` (received Project Standards from orchestrator), `fallback-registry` (self-loaded from registry), `fallback-path` (loaded via SKILL: Load path), or `none` (no skills loaded)

Example:

```markdown
**Status**: success
**Summary**: Proposal created for `{change-name}`. Defined scope, approach, and rollback plan.
**Artifacts**: Engram `sdd/{change-name}/proposal` | `openspec/changes/{change-name}/proposal.md`
**Next**: sdd-spec or sdd-design
**Risks**: None
**Skill Resolution**: injected — 3 skills (react-19, typescript, tailwind-4)
(other values: `fallback-registry`, `fallback-path`, or `none — no registry found`)
```
