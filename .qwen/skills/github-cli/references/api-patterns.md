# GitHub API — Patrones Avanzados con `gh api`

Referencia de patrones frecuentes para usar la API de GitHub vía `gh api`.

---

## Estructura base

```bash
gh api ENDPOINT [--method GET|POST|PUT|PATCH|DELETE] [--field KEY=VALUE] [--jq EXPR]
```

---

## Repositorios

```bash
# Metadata completa de un repo
gh api repos/OWNER/REPO

# Lista de ramas
gh api repos/OWNER/REPO/branches --jq '.[].name'

# Rama por defecto
gh api repos/OWNER/REPO --jq '.default_branch'

# Topics/etiquetas del repo
gh api repos/OWNER/REPO/topics

# Añadir topics
gh api --method PUT repos/OWNER/REPO/topics \
  --field names[]="python" --field names[]="cli"

# Contribuidores con número de commits
gh api repos/OWNER/REPO/contributors \
  --jq '.[] | "\(.contributions) commits — \(.login)"'

# Lenguajes usados (bytes por lenguaje)
gh api repos/OWNER/REPO/languages

# Estadísticas de participación (52 semanas)
gh api repos/OWNER/REPO/stats/participation
```

---

## Issues vía API

```bash
# Issues con paginación
gh api repos/OWNER/REPO/issues?state=open&per_page=100&page=1

# Issues de un milestone específico
gh api repos/OWNER/REPO/issues?milestone=MILESTONE_NUMBER

# Crear issue
gh api --method POST repos/OWNER/REPO/issues \
  --field title="Título del issue" \
  --field body="Descripción" \
  --field labels[]="bug"

# Comentar en un issue
gh api --method POST repos/OWNER/REPO/issues/NUMBER/comments \
  --field body="Mi comentario"
```

---

## Pull Requests vía API

```bash
# PRs con toda la info
gh api repos/OWNER/REPO/pulls?state=open

# Archivos modificados en un PR
gh api repos/OWNER/REPO/pulls/NUMBER/files \
  --jq '.[].filename'

# Checks/CI de un PR
gh api repos/OWNER/REPO/commits/COMMIT_SHA/check-runs \
  --jq '.check_runs[] | "\(.name): \(.conclusion)"'
```

---

## Contenido y Código

```bash
# Leer un archivo (en base64)
gh api repos/OWNER/REPO/contents/path/to/file \
  --jq '.content' | base64 -d

# Listar directorio
gh api repos/OWNER/REPO/contents/src \
  --jq '.[].name'

# Árbol completo del repo
gh api repos/OWNER/REPO/git/trees/HEAD?recursive=1 \
  --jq '[.tree[] | select(.type=="blob") | .path]'

# Ver commits recientes
gh api repos/OWNER/REPO/commits?per_page=10 \
  --jq '.[] | "\(.sha[:7]) \(.commit.message | split("\n")[0])"'

# Commits de un archivo específico
gh api repos/OWNER/REPO/commits?path=src/main.py \
  --jq '.[].commit.message'
```

---

## Releases vía API

```bash
# Último release
gh api repos/OWNER/REPO/releases/latest \
  --jq '{tag: .tag_name, date: .published_at, url: .html_url}'

# Todos los releases
gh api repos/OWNER/REPO/releases \
  --jq '.[] | "\(.tag_name) — \(.published_at[:10])"'

# Assets de un release
gh api repos/OWNER/REPO/releases/latest \
  --jq '.assets[] | "\(.name): \(.browser_download_url)"'
```

---

## Usuarios y Organizaciones

```bash
# Perfil de un usuario
gh api users/USERNAME

# Repos públicos de un usuario
gh api users/USERNAME/repos?sort=updated \
  --jq '.[] | "\(.name): ⭐\(.stargazers_count)"'

# Miembros de una organización
gh api orgs/ORG/members --jq '.[].login'

# Repos de una organización
gh api orgs/ORG/repos?type=public&sort=stars \
  --jq '.[] | "\(.name): ⭐\(.stargazers_count)"'
```

---

## GraphQL — Consultas Avanzadas

```bash
# Mis repos ordenados por actividad reciente
gh api graphql -f query='
  query {
    viewer {
      repositories(first: 20, orderBy: {field: UPDATED_AT, direction: DESC}) {
        nodes {
          name
          description
          stargazerCount
          updatedAt
          primaryLanguage { name }
        }
      }
    }
  }
'

# Issues de un repo con etiquetas
gh api graphql -f query='
  query($owner: String!, $name: String!) {
    repository(owner: $owner, name: $name) {
      issues(first: 20, states: OPEN) {
        nodes {
          number
          title
          labels(first: 5) { nodes { name } }
        }
      }
    }
  }
' -f owner="OWNER" -f name="REPO"

# PRs abiertas con reviewers
gh api graphql -f query='
  query($owner: String!, $name: String!) {
    repository(owner: $owner, name: $name) {
      pullRequests(first: 10, states: OPEN) {
        nodes {
          number
          title
          author { login }
          reviewRequests(first: 5) {
            nodes { requestedReviewer { ... on User { login } } }
          }
        }
      }
    }
  }
' -f owner="OWNER" -f name="REPO"
```

---

## Paginación Automática

Para obtener TODOS los resultados (no solo la primera página):

```bash
# --paginate descarga todas las páginas automáticamente
gh api --paginate repos/OWNER/REPO/issues?state=closed \
  --jq '.[] | .title'

# Combinar con jq para procesar el stream
gh api --paginate repos/OWNER/REPO/stargazers \
  --jq '.[] | .login' > todos-los-stargazers.txt
```

---

## Scopes de Token

Si un comando falla por permisos, actualiza el token:

```bash
# Ver scopes actuales
gh auth status

# Agregar scope para repos privados
gh auth refresh -s repo

# Agregar scope para delete repos
gh auth refresh -s delete_repo

# Agregar scope para leer org
gh auth refresh -s read:org
```
