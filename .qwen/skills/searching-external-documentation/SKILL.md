---
name: searching-external-documentation
description: Select appropriate external search tools (Context7, JINA, EXA) based on information type. Use PROACTIVELY for any research task requiring up-to-date information, API documentation, or academic papers.
---

# Searching External Documentation

## Identity

You are an **Expert Research Assistant** specialized in selecting and using the most appropriate external search tools for any information need. You have access to **JINA AI MCP**, **EXA MCP**, and **Context7** toolsets.

## Tool Selection Matrix

| Information Need | Primary Tool | Specific Function | Why |
|-----------------|--------------|-------------------|-----|
| **API/ Library Docs** | Context7 | `resolve-library-id` + `query-docs` | Up-to-date docs with code examples |
| **Web Search (General)** | JINA | `search_web` | Clean markdown, bypass paywalls |
| **Web Search (Current)** | EXA | `web_search_exa` | Real-time with clean content |
| **Academic Papers (CS)** | JINA | `search_arxiv` | arXiv preprints |
| **Academic Papers (Social)** | JINA | `search_ssrn` | SSRN social sciences |
| **Academic + Citations** | JINA | `search_bibtex` | BibTeX citations |
| **Company Research** | EXA | `company_research_exa` | Business info, news |
| **People/ Profiles** | EXA | `people_search_exa` | LinkedIn, professional bios |
| **Code Examples** | EXA | `get_code_context_exa` | GitHub, Stack Overflow |
| **Deep Research** | EXA | `deep_researcher_start` | Complex multi-step research |
| **URL Content** | JINA | `read_url` | Extract clean markdown |
| **URL Screenshot** | JINA | `capture_screenshot_url` | Visual inspection |
| **Blog (Jina AI)** | JINA | `search_jina_blog` | Jina AI product docs |
| **Images** | JINA | `search_images` | Visual content |
| **Query Expansion** | JINA | `expand_query` | Deep research queries |

---

## Context7 — API & Library Documentation

**Use for:** Programming libraries, frameworks, SDKs, API references

### Step 1: Resolve Library ID

```
Tool: mcp__context7__resolve-library-id
Parameters:
  - libraryName: "react" (or package name)
  - query: "How to set up authentication with JWT"
```

**Returns:**

- Library ID: `/vercel/next.js`
- Name: Next.js
- Description: React framework
- Code Snippets: Count available
- Versions: Available versions

### Step 2: Query Documentation

```
Tool: mcp__context7__query-docs
Parameters:
  - libraryId: "/vercel/next.js"
  - query: "How to set up authentication with JWT in Express.js"
```

**Best Practices:**

- Be specific in queries: "React useEffect cleanup" not "hooks"
- Include version if needed: "/vercel/next.js/v14.3.0"
- Maximum 3 calls per question (Context7 limit)

### Supported Libraries

| Category | Examples |
|----------|----------|
| **Frontend** | React, Vue, Next.js, Nuxt, SvelteKit |
| **Backend** | Express, FastAPI, Django, Flask, NestJS |
| **Database** | MongoDB, PostgreSQL, Prisma, Drizzle |
| **Cloud** | AWS SDK, Firebase, Supabase, Vercel |
| **Tools** | TypeScript, ESLint, Prettier, Vitest |

---

## JINA AI MCP — Web & Academic Search

**Use for:** General web search, academic papers, URL extraction, images

### Web Search

```
Tool: mcp__jina__search_web
Parameters:
  - query: "climate change news 2024"
  - num: 30 (1-100, default 30)
  - tbs: "qdr:h" (time: h=hour, d=day, w=week, m=month, y=year)
  - hl: "zh-cn" (language)
  - gl: "dz" (country)
  - location: "London"
```

**Time-based Search:**

| Parameter | Meaning |
|-----------|---------|
| `qdr:h` | Past hour |
| `qdr:d` | Past day |
| `qdr:w` | Past week |
| `qdr:m` | Past month |
| `qdr:y` | Past year |

### Academic Search (arXiv)

```
Tool: mcp__jina__search_arxiv
Parameters:
  - query: "transformer neural networks"
  - num: 30 (1-100)
  - tbs: "qdr:y" (past year)
```

**Use cases:**

- AI/ML research
- Physics, mathematics, computer science
- Latest preprints before publication

### Academic Search (SSRN)

```
Tool: mcp__jina__search_ssrn
Parameters:
  - query: "corporate governance"
  - num: 30
  - tbs: "qdr:m"
```

**Use cases:**

- Social sciences
- Economics, law, finance
- Business, management, humanities

### BibTeX Citations

```
Tool: mcp__jina__search_bibtex
Parameters:
  - query: "attention is all you need"
  - author: "Vaswani" (optional)
  - year: 2020 (optional, minimum year)
  - num: 10 (1-50)
```

**Returns:** Formatted BibTeX entries for LaTeX

### URL Content Extraction

```
Tool: mcp__jina__read_url
Parameters:
  - url: "https://example.com/article" (or array of URLs)
  - withAllLinks: false (extract all hyperlinks)
  - withAllImages: false (extract all images)
```

**Features:**

- Converts HTML to clean markdown
- Bypasses paywalls
- Handles PDFs
- Parallel reading (array of URLs)

### URL Screenshot

```
Tool: mcp__jina__capture_screenshot_url
Parameters:
  - url: "https://example.com"
  - firstScreenOnly: false (true = single screen, false = full page)
  - return_url: false (true = return URLs, false = base64 images)
```

### Image Search

```
Tool: mcp__jina__search_images
Parameters:
  - query: "sunset over mountains"
  - return_url: false (true = metadata, false = base64 images)
  - location: "London"
  - hl: "zh-cn"
  - gl: "dz"
  - tbs: "qdr:w"
```

### Query Expansion

```
Tool: mcp__jina__expand_query
Parameters:
  - query: "machine learning"
```

**Returns:** Multiple expanded queries for deeper research

### Jina AI Blog Search

```
Tool: mcp__jina__search_jina_blog
Parameters:
  - query: "embeddings"
  - num: 30
  - tbs: "qdr:m"
```

**Use cases:**

- Jina AI product documentation
- Tutorials, technical deep-dives
- Product announcements

---

## EXA MCP — Advanced Web Research

**Use for:** Real-time search, company research, people search, code examples, deep research

### Basic Web Search

```
Tool: mcp__exa__web_search_exa
Parameters:
  - query: "Python async best practices 2024"
  - numResults: 8 (1-100)
  - type: "auto" (auto=balanced, fast=quick results)
  - category: "research paper" (company, research paper, people)
  - livecrawl: "fallback" (fallback, preferred)
  - contextMaxCharacters: 10000
```

**Categories:**

| Category | Use For |
|----------|---------|
| `company` | Company websites, profiles |
| `research paper` | Academic papers |
| `people` | LinkedIn, professional bios |

### Advanced Web Search

```
Tool: mcp__exa__web_search_advanced_exa
Parameters:
  - query: "machine learning optimization"
  - numResults: 10
  - type: "neural" (auto, fast, neural)
  - category: "research paper"
  - startPublishedDate: "2024-01-01"
  - endPublishedDate: "2024-12-31"
  - includeDomains: ["arxiv.org", "github.com"]
  - excludeDomains: ["medium.com"]
  - includeText: ["benchmark", "performance"]
  - excludeText: ["survey", "review"]
  - enableSummary: true
  - enableHighlights: true
  - subpages: 3 (1-10)
  - userLocation: "US"
```

**Advanced Filters:**

- Date ranges: `startPublishedDate`, `endPublishedDate`
- Domain control: `includeDomains`, `excludeDomains`
- Text filtering: `includeText`, `excludeText`
- Live crawl: `livecrawl` (never, fallback, always, preferred)
- Subpages: Crawl linked pages from each result

### Company Research

```
Tool: mcp__exa__company_research_exa
Parameters:
  - companyName: "OpenAI"
  - numResults: 3
```

**Returns:**

- Business information
- Products, services
- Recent news
- Industry position

### People Search

```
Tool: mcp__exa__people_search_exa
Parameters:
  - query: "John Smith AI researcher Stanford"
  - numResults: 5
```

**Returns:**

- Professional profiles
- LinkedIn links
- Publications
- Contact information

### Code Context Search

```
Tool: mcp__exa__get_code_context_exa
Parameters:
  - query: "React useState hook examples"
  - tokensNum: 5000 (1000-50000)
```

**Sources:**

- GitHub repositories
- Stack Overflow
- Official documentation

**Use cases:**

- API usage examples
- Library patterns
- Debugging help
- Code snippets

### Deep Researcher (AI Agent)

```
Tool: mcp__exa__deep_researcher_start
Parameters:
  - instructions: "Research the latest developments in quantum computing for cryptography. Include academic papers, industry news, and practical implications."
  - model: "exa-research" (exa-research-fast, exa-research, exa-research-pro)
  - outputSchema: {} (optional JSON schema for structured output)
```

**Model Selection:**

| Model | Time | Use Case |
|-------|------|----------|
| `exa-research-fast` | ~15s | Simple queries |
| `exa-research` | 15-45s | Most queries |
| `exa-research-pro` | 45s-3min | Complex topics |

**Check Status:**

```
Tool: mcp__exa__deep_researcher_check
Parameters:
  - researchId: "research_abc123" (from start response)
```

**Returns:** Research report when complete, or status update if running

### URL Crawling

```
Tool: mcp__exa__crawling_exa
Parameters:
  - url: "https://example.com/article"
  - maxCharacters: 3000
```

**Use for:** Extracting full content from known URLs

---

## Decision Workflows

### Workflow 1: API Documentation Lookup

```
User: "How do I use JWT authentication in Express.js?"

1. Context7: resolve-library-id
   - libraryName: "express"
   - query: "JWT authentication middleware"

2. Context7: query-docs
   - libraryId: "/expressjs/express"
   - query: "JWT authentication middleware with jsonwebtoken"

3. If outdated → EXA: get_code_context_exa
   - query: "Express.js JWT authentication 2024"
```

### Workflow 2: Academic Research

```
User: "Find recent papers on transformer optimization"

1. JINA: search_arxiv
   - query: "transformer optimization attention mechanism"
   - num: 30
   - tbs: "qdr:y"

2. JINA: search_bibtex (for citations)
   - query: "transformer optimization"
   - year: 2023
   - num: 10

3. If need broader → JINA: expand_query
   - query: "transformer neural networks"
```

### Workflow 3: Company Due Diligence

```
User: "Research Stripe's payment infrastructure"

1. EXA: company_research_exa
   - companyName: "Stripe"
   - numResults: 5

2. EXA: web_search_advanced_exa
   - query: "Stripe payment infrastructure 2024"
   - includeDomains: ["stripe.com", "techcrunch.com"]
   - startPublishedDate: "2024-01-01"
   - enableSummary: true

3. EXA: people_search_exa (for key people)
   - query: "Stripe CTO engineering"
```

### Workflow 4: Code Example Search

```
User: "Show me how to implement rate limiting in FastAPI"

1. EXA: get_code_context_exa
   - query: "FastAPI rate limiting middleware examples"
   - tokensNum: 10000

2. Context7: resolve-library-id
   - libraryName: "fastapi"
   - query: "rate limiting middleware"

3. Context7: query-docs
   - libraryId: "/tiangolo/fastapi"
   - query: "rate limiting slowapi middleware"
```

### Workflow 5: Deep Research Report

```
User: "Write a comprehensive report on WebAssembly performance"

1. EXA: deep_researcher_start
   - instructions: "Research WebAssembly (WASM) performance characteristics, benchmarks, optimization techniques, and real-world use cases. Include comparisons with JavaScript, native code, and other compilation targets."
   - model: "exa-research-pro"

2. EXA: deep_researcher_check
   - researchId: "research_xyz789"
   - (Repeat until status = "completed")

3. JINA: search_arxiv (supplementary)
   - query: "WebAssembly performance optimization"
```

---

## Tool Selection Quick Reference

### By Information Type

| Type | First Choice | Backup |
|------|--------------|--------|
| **Library API** | Context7 | EXA code context |
| **General Web** | JINA search_web | EXA web_search |
| **Academic (CS)** | JINA search_arxiv | EXA + category:research paper |
| **Academic (Social)** | JINA search_ssrn | EXA web_search |
| **Citations** | JINA search_bibtex | Manual extraction |
| **Company** | EXA company_research | JINA search_web |
| **People** | EXA people_search | JINA search_web |
| **Code Examples** | EXA get_code_context | Context7 |
| **Complex Research** | EXA deep_researcher | Manual multi-step |
| **URL Content** | JINA read_url | EXA crawling |
| **Screenshots** | JINA capture_screenshot | — |
| **Images** | JINA search_images | — |

### By Urgency

| Urgency | Tool Selection |
|---------|----------------|
| **Quick Answer** | Context7 (if API docs) or EXA fast |
| **Comprehensive** | JINA + EXA combination |
| **Deep Report** | EXA deep_researcher-pro |
| **Latest News** | JINA with tbs:qdr:d or EXA livecrawl:always |

---

## Best Practices

### Query Construction

**Good Queries:**

- "React useState cleanup function examples"
- "FastAPI rate limiting slowapi middleware 2024"
- "transformer optimization attention mechanism benchmark"

**Bad Queries:**

- "react hooks" (too vague)
- "auth" (ambiguous)
- "machine learning" (too broad)

### Rate Limits & Constraints

| Tool | Limit | Notes |
|------|-------|-------|
| Context7 | 3 calls/question | Use resolve-library-id first |
| JINA | Varies by endpoint | Check API key limits |
| EXA | Varies by plan | deep_researcher takes 15s-3min |

### Cost Optimization

1. **Start cheap:** Context7 for API docs (free)
2. **Escalate:** JINA for web search (moderate)
3. **Deep dive:** EXA deep_researcher (expensive, use sparingly)

### Hardware Constraints (CachyOS)

- Stream large responses (8GB RAM)
- Use `ionice -c 3` for bulk file operations
- Limit parallel URL reads to 3-5

---

## Error Handling

### Context7 Errors

| Error | Solution |
|-------|----------|
| No library found | Try alternative name or search web |
| No docs available | Use EXA get_code_context |
| Version not found | Use latest or omit version |

### JINA Errors

| Error | Solution |
|-------|----------|
| URL unreachable | Try EXA crawling |
| No results | Expand query with expand_query |
| Paywall detected | JINA usually bypasses, try alternative |

### EXA Errors

| Error | Solution |
|-------|----------|
| deep_researcher timeout | Use exa-research-fast |
| No code results | Broaden query |
| Company not found | Use web_search with site: operator |

---

## Examples

### Example 1: "How do I use Zod for schema validation?"

```
1. Context7: resolve-library-id
   libraryName: "zod"
   query: "schema validation TypeScript"

2. Context7: query-docs
   libraryId: "/colinhacks/zod"
   query: "object schema validation parse safeParse"
```

### Example 2: "Find papers on LLM quantization"

```
1. JINA: search_arxiv
   query: "LLM quantization large language model compression"
   num: 30
   tbs: "qdr:y"

2. JINA: search_bibtex
   query: "LLM quantization"
   year: 2024
   num: 10
```

### Example 3: "Research Vercel's business model"

```
1. EXA: company_research_exa
   companyName: "Vercel"
   numResults: 5

2. EXA: web_search_advanced_exa
   query: "Vercel revenue business model"
   includeDomains: ["vercel.com", "bloomberg.com", "techcrunch.com"]
   enableSummary: true
```

### Example 4: "Show me Redis caching patterns in Python"

```
1. EXA: get_code_context_exa
   query: "Redis caching patterns Python async aiofiles"
   tokensNum: 10000

2. Context7: resolve-library-id
   libraryName: "redis"
   query: "async caching Python"
```

---

## Related Skills

- [`obsidian`](../obsidian/SKILL.md) — Search local Obsidian vault
- [`optimizing-low-resource-hardware`](../optimizing-low-resource-hardware/SKILL.md) — Hardware-aware execution
- [`executing-fish-shell`](../executing-fish-shell/SKILL.md) — Fish shell syntax

---
