---
name: context7-cli
description: Fetch up-to-date library documentation via ctx7 CLI. Use when user asks about any library, framework, API, or needs code examples and setup instructions.
---

# Context7 CLI — Library Documentation

## Overview

Fetch up-to-date library documentation directly in the terminal using the `ctx7` CLI. No MCP overhead, no browser needed.

**Prerequisite:** `ctx7` installed globally (`npm install -g ctx7`, version 0.3.10+)

## Trigger

Use this skill when:
- User asks about any library, framework, or API
- User needs code examples, setup instructions, or configuration
- User mentions a specific library name (React, Next.js, Prisma, Express, etc.)
- Questions about "how to" with any known library

## Workflow — ALWAYS Two Steps

```fish
# Step 1: Resolve library name → get Library ID
ctx7 library <name> "<query>"

# Step 2: Query documentation with the resolved ID
ctx7 docs <library-id> "<specific question>"
```

**Example:**
```fish
# User asks: "How do I set up authentication in Next.js?"

# Step 1: Find the library
ctx7 library nextjs "authentication middleware setup"
# → Returns: /vercel/next.js (among others)

# Step 2: Query docs
ctx7 docs /vercel/next.js "How to set up authentication middleware"
```

## Commands Reference

### `ctx7 library <name> [query]`

Searches Context7 index by name. Returns matching libraries with IDs.

**Parameters:**
- `name` (required): Library/package name
- `query` (optional): Natural language description of what you're doing — improves ranking

**Output fields:**
- **Library ID**: Format `/org/project` — pass to `ctx7 docs`
- **Code Snippets**: Number of indexed examples (higher = more coverage)
- **Source Reputation**: High, Medium, Low, Unknown
- **Benchmark Score**: Quality 0-100
- **Versions**: Version-specific IDs when available

### `ctx7 docs <library-id> "<query>"`

Takes a library ID and natural-language question. Returns code snippets + explanations.

**Flags:**
- `--json`: Output as structured JSON (pipeable to other tools)

```fish
# Pipe to grep/head
ctx7 docs /facebook/react "useEffect cleanup" | head -50

# Structured JSON
ctx7 docs /facebook/react "hooks" --json | jq '.snippets[0].code'
```

## Query Best Practices

1. **Be specific:** `"How to set up authentication with JWT in Express.js"` not `"auth"`
2. **Describe the goal:** What you're trying to accomplish, not keywords
3. **Include framework + version context** when relevant
4. **For multiple results:** Pick closest name + highest snippet count + strongest reputation

## Common Library IDs

| Library | ID | Library | ID |
|---------|-----|---------|-----|
| React | `/facebook/react` | Next.js | `/vercel/next.js` |
| Vue | `/vuejs/core` | Express | `/expressjs/express` |
| Prisma | `/prisma/prisma` | Zod | `/colinhacks/zod` |
| React Query | `/tanstack/react-query` | Zustand | `/pmndrs/zustand` |
| React Hook Form | `/react-hook-form/react-hook-form` | Tailwind | `/tailwindlabs/tailwindcss` |
| Axios | `/axios/axios` | TypeScript | `/microsoft/TypeScript` |
| Serde | `/serde-rs/serde` | Tokio | `/tokio-rs/tokio` |
| Axum | `/tokio-rs/axum` | Supabase | `/supabase/supabase` |

## Authentication (Optional)

Works without login. For higher rate limits:
```fish
ctx7 login           # OAuth browser flow
export CONTEXT7_API_KEY=your_key  # Or env var
```

## Integration with Other Tools

- **Exa MCP:** Exa for community examples, Stack Overflow, tutorials. `ctx7` for official docs.
- **Jina MCP:** Jina for web search, blog posts, best practices. `ctx7` for API reference.
- **GitNexus:** GitNexus for local code analysis. `ctx7` for external library docs.
