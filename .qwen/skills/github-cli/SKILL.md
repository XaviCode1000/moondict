---
name: github-cli
description: >
  GitHub CLI (gh) operations: repos, issues, PRs, releases, Actions, search.
  Use when interacting with GitHub from terminal.
  Trigger: gh command, github cli, pull request, issue, repo, fork, release,
  github actions, workflow, gh search, gh api, github automation
license: MIT
metadata:
  author: gazadev
  version: "1.0.0"
  sources:
    - GitHub CLI Official Documentation
    - gh manual pages
---

# GitHub CLI (gh) — Skill Completa

Eres un experto en la CLI oficial de GitHub (`gh`). Tu objetivo es ayudar al usuario a aprovechar
al máximo esta herramienta, tanto para gestionar sus propios repositorios como para explorar y
consultar repositorios de terceros publicados en GitHub.

## 🐟 Shell Note

Los ejemplos de comandos `gh` son compatibles con Fish shell sin modificaciones.
Para operaciones de shell general (variables, loops, condiciones), consultar la skill `fish-skills`.

---

## 1. Setup y Configuración ⚡ EMPEZAR AQUÍ

> Si el usuario tiene `gh` instalado pero NO autenticado, este es el primer paso obligatorio.
> Sin autenticación, la mayoría de comandos fallarán o estarán limitados a repos públicos con rate limit bajo.

### Paso 1 — Autenticación (obligatorio)

```bash
# Verificar estado actual
gh auth status
# Si dice "not logged in" o "no credentials", continúa con el siguiente paso

# Autenticar con GitHub.com (abre el navegador automáticamente)
gh auth login
# Selecciona: GitHub.com → HTTPS o SSH → Login with a web browser
# Se abrirá el navegador para autorizar. Después vuelve a la terminal.

# Verificar que quedó bien
gh auth status
# Debe mostrar: ✓ Logged in to github.com as TU_USUARIO
```

**¿Por qué importa el protocolo (HTTPS vs SSH)?**
- **HTTPS**: más fácil de configurar, funciona en cualquier red. Recomendado para empezar.
- **SSH**: más seguro para uso diario, no pide credenciales en cada `git push`. Requiere tener una clave SSH ya configurada en GitHub.

### Paso 2 — Configuración recomendada

```bash
# Editor de texto para cuando gh necesite que escribas algo (ej: cuerpo de un PR)
gh config set editor "code -w"     # VS Code  (el -w espera a que cierres el archivo)
gh config set editor "nano"        # nano (alternativa simple en Linux/Mac)
gh config set editor "notepad"     # Notepad en Windows

# Protocolo de Git preferido
gh config set git_protocol ssh     # SSH (si ya tienes clave SSH en GitHub)
gh config set git_protocol https   # HTTPS (opción más simple)

# Ver toda la configuración actual
gh config list
```

### Paso 3 — Verificar que todo funciona

```bash
# Debe mostrar tu nombre de usuario y los scopes del token
gh auth status

# Prueba real: listar tus repos
gh repo list --limit 5

# Prueba con repo de tercero
gh repo view cli/cli
```

### Instalar `gh` (si aún no está instalado)

```fish
# CachyOS/Arch Linux
sudo pacman -S github-cli

# Verificar instalación
gh --version
```

---

## 2. Exploración de Repositorios de Terceros

> Una de las capacidades más potentes de `gh`: puedes inspeccionar cualquier repo público
> — issues, PRs, releases, código, estructura — **sin clonarlo ni abrir el navegador**.
> Ideal para evaluar librerías antes de usarlas, seguir proyectos activos, o investigar bugs conocidos.

### Ver información de un repositorio
```bash
# Vista general
gh repo view OWNER/REPO

# Abrir en el navegador
gh repo view OWNER/REPO --web

# Obtener datos específicos en JSON
gh repo view OWNER/REPO --json name,description,stargazerCount,forkCount,languages

# Ver el README directamente en la terminal
gh repo view OWNER/REPO --readme
```

### Buscar repositorios públicos
```bash
# Buscar por término
gh search repos "machine learning python"

# Con filtros avanzados
gh search repos "react dashboard" --language javascript --sort stars --limit 20

# Repos con más estrellas de una organización
gh search repos --owner vercel --sort stars --limit 10

# Buscar por tema (topic)
gh search repos --topic "fastapi" --stars ">500"
```

### Explorar código fuente de terceros
```bash
# Listar archivos de un repo (requiere clonación temporal o usar la API)
gh api repos/OWNER/REPO/contents/

# Ver el contenido de un archivo específico
gh api repos/OWNER/REPO/contents/PATH/TO/FILE --jq '.content' | base64 -d

# Ver estructura de directorios
gh api repos/OWNER/REPO/git/trees/HEAD?recursive=1 --jq '[.tree[].path]'
```

---

## 3. Mis Repositorios — Gestión Completa

### Listar y navegar
```bash
# Listar todos mis repos
gh repo list

# Listar repos con detalles
gh repo list --json name,description,isPrivate,stargazerCount --limit 50

# Listar repos de una organización
gh repo list ORGANIZATION --limit 30
```

### Crear repositorios
```bash
# Interactivo
gh repo create

# Directo (público)
gh repo create mi-proyecto --public --description "Descripción del proyecto"

# Directo (privado, clonar automáticamente)
gh repo create mi-proyecto --private --clone

# Desde un directorio local existente
gh repo create --source=. --public --push
```

### Operaciones comunes
```bash
# Clonar cualquier repositorio
gh repo clone OWNER/REPO

# Clonar en directorio específico
gh repo clone OWNER/REPO ~/mis-proyectos/nombre-local

# Hacer fork de un repo de terceros
gh repo fork OWNER/REPO

# Fork y clonar en un paso
gh repo fork OWNER/REPO --clone

# Archivar un repo
gh repo archive OWNER/REPO

# Renombrar
gh repo rename nuevo-nombre

# Eliminar (¡cuidado!)
gh repo delete OWNER/REPO --confirm
```

---

## 4. Issues

> Issues son el sistema de seguimiento de tareas y bugs de GitHub. Con `gh` puedes
> trabajar con issues **tanto de tus propios repos como de repos de terceros** —
> sin necesidad de abrir el navegador. Útil para: reportar bugs en librerías que usas,
> hacer seguimiento de features que esperas, o gestionar el backlog de tu proyecto.

### Consultar issues (propios y de terceros)
```bash
# Listar issues abiertos
gh issue list --repo OWNER/REPO

# Filtrar por estado, etiqueta, asignado
gh issue list --state closed --label bug --assignee "@me"

# Buscar issues por texto
gh search issues "memory leak" --repo OWNER/REPO --state open

# Ver detalle completo de un issue (con comentarios)
gh issue view 42 --repo OWNER/REPO --comments

# Ver en el navegador
gh issue view 42 --web
```

### Crear y gestionar issues
```bash
# Crear issue interactivo
gh issue create

# Crear issue con todos los campos
gh issue create \
  --title "Bug: Login falla en Safari" \
  --body "Descripción detallada..." \
  --label "bug" \
  --assignee "@me" \
  --milestone "v2.0"

# Cerrar un issue
gh issue close 42 --comment "Resuelto en PR #55"

# Reabrir
gh issue reopen 42

# Agregar etiqueta
gh issue edit 42 --add-label "priority:high"
```

---

## 5. Pull Requests

> Los PRs son el mecanismo central de colaboración en GitHub. Con `gh pr` puedes
> crear, revisar, aprobar y mergear PRs desde la terminal. También puedes inspeccionar
> PRs de repos de terceros para entender cómo se implementó un cambio o si ya existe
> un fix para un bug que encontraste.

### Consultar PRs (propios y de terceros)
```bash
# Listar PRs abiertos
gh pr list --repo OWNER/REPO

# PRs que me han asignado para revisar
gh search prs --review-requested=@me --state=open

# PRs que yo creé en todos mis repos
gh search prs --author=@me --state=open

# Ver detalle con diff
gh pr view 123 --comments

# Ver los archivos cambiados
gh pr diff 123

# Ver en el navegador
gh pr view 123 --web
```

### Crear y gestionar PRs
```bash
# Crear PR desde rama actual (interactivo)
gh pr create

# PR completo con todos los campos
gh pr create \
  --base main \
  --head feature/mi-feature \
  --title "feat: nueva funcionalidad X" \
  --body "## Descripción\n\nDetalles del cambio..." \
  --reviewer usuario1,usuario2 \
  --label "enhancement"

# Crear como draft
gh pr create --draft

# Hacer checkout de un PR para revisión local
gh pr checkout 123

# Mergear PR
gh pr merge 123 --squash --delete-branch

# Aprobar PR
gh pr review 123 --approve

# Solicitar cambios
gh pr review 123 --request-changes --body "Necesita pruebas unitarias"
```

---

## 6. Releases y Tags

```bash
# Ver releases de cualquier repo
gh release list --repo OWNER/REPO

# Ver detalles del último release
gh release view --repo OWNER/REPO

# Ver release específico
gh release view v2.0.0 --repo OWNER/REPO

# Descargar assets de un release
gh release download v2.0.0 --repo OWNER/REPO

# Descargar un asset específico
gh release download v2.0.0 --repo OWNER/REPO --pattern "*.tar.gz"

# Crear un release
gh release create v1.0.0 \
  --title "v1.0.0 - Primera versión estable" \
  --notes "## Cambios\n- Feature A\n- Fix B" \
  ./dist/*.zip
```

---

## 7. GitHub Actions — Workflows

> Usa `gh run` para monitorear y controlar pipelines de CI/CD sin abrir el navegador.
> Especialmente útil para: ver por qué falló un build, reintentar sin hacer push, 
> disparar deploys manuales, o monitorear releases en tiempo real.

### Ver estado de workflows
```bash
# Ver workflows disponibles en el repo actual
gh workflow list

# Ver workflows de un repo de tercero
gh workflow list --repo OWNER/REPO

# Ver las últimas ejecuciones (todas)
gh run list

# Filtrar por estado: success | failure | cancelled | in_progress
gh run list --status failure

# Ejecuciones de un workflow específico
gh run list --workflow ci.yml --limit 10

# Ver en qué rama corrió cada ejecución
gh run list --json headBranch,status,conclusion,workflowName
```

### Inspeccionar una ejecución
```bash
# Resumen visual de una ejecución (usa el ID del run list)
gh run view 1234567

# Ver logs completos
gh run view 1234567 --log

# Ver SOLO los logs de los pasos que fallaron (muy útil para debug)
gh run view 1234567 --log-failed

# Monitorear en tiempo real hasta que termine (se actualiza cada 3s)
gh run watch

# Monitorear un run específico
gh run watch 1234567
```

### Controlar ejecuciones
```bash
# Re-ejecutar un run fallido
gh run rerun 1234567

# Re-ejecutar solo los jobs que fallaron
gh run rerun 1234567 --failed

# Cancelar un run en progreso
gh run cancel 1234567

# Disparar un workflow manualmente (debe tener workflow_dispatch configurado)
gh workflow run ci.yml

# Disparar con inputs personalizados
gh workflow run deploy.yml --field environment=production --field version=2.0

# Disparar en una rama específica
gh workflow run ci.yml --ref develop

# Activar/desactivar un workflow
gh workflow enable ci.yml
gh workflow disable dependabot.yml
```

### Encadenar con notificaciones
```bash
# Disparar workflow y esperar resultado (útil en scripts)
gh run watch && echo "✅ CI pasó correctamente"

# Encadenar: push + abrir PR + monitorear CI
git push origin feature/mi-rama
gh pr create --fill
gh run watch
```

---

## 8. Búsqueda Avanzada — `gh search`

> `gh search` te da acceso a toda GitHub como motor de búsqueda desde la terminal.
> Sirve tanto para descubrir librerías/herramientas como para investigar problemas conocidos
> en proyectos que usas (ej: "¿alguien más reportó este error?").

### Buscar repositorios
```bash
# Por término general
gh search repos "task queue python"

# Con filtros combinados (los más útiles)
gh search repos "graphql client" \
  --language typescript \
  --stars ">1000" \
  --sort stars \
  --limit 15

# Repos de una organización específica
gh search repos --owner microsoft --language python --sort updated

# Repos creados o actualizados recientemente
gh search repos "fastapi" --updated ">2024-01-01" --sort updated

# Por topic/etiqueta oficial de GitHub
gh search repos --topic "machine-learning" --topic "python" --stars ">500"

# Repos con licencia específica
gh search repos "web scraper" --license mit --sort stars
```

### Buscar issues y PRs (muy útil para investigar bugs)
```bash
# "¿Este error ya fue reportado?"
gh search issues "SSL certificate error" --repo requests/requests --state open

# Buscar en toda GitHub por lenguaje
gh search issues "segfault on ARM" --language c --state open

# PRs mergeados que arreglaron algo específico
gh search prs "fix: memory leak" --language go --state merged --sort updated

# Issues sin respuesta (sin assignee ni comentarios)
gh search issues "installation fails" --language python --no-assignee

# Buscar por etiqueta en toda GitHub
gh search issues --label "good first issue" --language javascript --state open
```

### Buscar código
```bash
# Buscar un patrón de código específico
gh search code "useState useCallback" --language typescript

# Buscar en un repositorio específico
gh search code "def train_model" --repo huggingface/transformers

# Buscar en una organización
gh search code "API_KEY" --owner mi-organizacion

# Buscar archivos por nombre
gh search code "filename:docker-compose.yml" --owner OWNER
```

### Buscar usuarios y organizaciones
```bash
# Encontrar organizaciones por tema
gh search users --type org "machine learning"

# Usuarios con muchos seguidores
gh search users "deep learning" --followers ">1000" --type user
```

---

## 9. API de GitHub — Acceso Avanzado

> Usa `gh api` cuando los comandos de alto nivel no tienen lo que necesitas.
> Da acceso completo a la API REST de GitHub y también a GraphQL.
> No necesitas gestionar tokens ni headers — `gh` los maneja automáticamente.
> 
> Para patrones más avanzados (paginación, GraphQL, stats), ver:
> `references/api-patterns.md`

```bash
# Cualquier endpoint de la API REST
gh api repos/OWNER/REPO

# Con campos específicos usando jq
gh api repos/OWNER/REPO --jq '.stargazers_count'

# Listar contributors
gh api repos/OWNER/REPO/contributors --jq '.[].login'

# Ver estadísticas de commits
gh api repos/OWNER/REPO/stats/commit_activity

# GraphQL query
gh api graphql -f query='
  query {
    viewer {
      repositories(first: 10, orderBy: {field: UPDATED_AT, direction: DESC}) {
        nodes { name, updatedAt, stargazerCount }
      }
    }
  }
'
```

Para referencia completa de la API REST, ver: `references/api-patterns.md` (incluido en esta skill)

---

## 10. Alias y Automatización

```bash
# Crear alias para comandos frecuentes
gh alias set prs "pr list --author @me"
gh alias set myissues "issue list --assignee @me"
gh alias set draft "pr create --draft"

# Ver todos los alias definidos
gh alias list

# Eliminar alias
gh alias delete prs

# Usar alias en scripts
gh prs  # equivale a: gh pr list --author @me
```

---

## 11. Flujos de Trabajo Completos

### Flujo: Contribuir a un repo de terceros
```bash
# 1. Explorar el repo
gh repo view OWNER/REPO

# 2. Hacer fork
gh repo fork OWNER/REPO --clone
cd REPO

# 3. Crear rama
git checkout -b fix/mi-arreglo

# 4. Hacer cambios... luego:
git add . && git commit -m "fix: descripción del arreglo"
git push origin fix/mi-arreglo

# 5. Crear PR hacia el repo original
gh pr create --repo OWNER/REPO --head TU_USUARIO:fix/mi-arreglo
```

### Flujo: Monitorear un proyecto de terceros
```bash
# Ver issues recientes
gh issue list --repo OWNER/REPO --state open --limit 20

# Ver últimos PRs mergeados
gh pr list --repo OWNER/REPO --state merged --limit 10

# Ver último release
gh release view --repo OWNER/REPO

# Ver si hay workflows fallando
gh run list --repo OWNER/REPO --status failure
```

---

## Patrones de Output y Formato

La mayoría de comandos soportan `--json` + `--jq` para scripting:

```bash
# JSON completo
gh issue list --json number,title,state,labels

# Filtrar con jq
gh issue list --json number,title --jq '.[] | "\(.number): \(.title)"'

# Formato de tabla personalizado
gh issue list --template '{{range .}}#{{.number}} {{.title}}{{"\n"}}{{end}}'
```

---

## Referencia Rápida de Grupos de Comandos

| Grupo | Descripción |
|-------|-------------|
| `gh repo` | Repositorios: crear, clonar, fork, ver, listar |
| `gh issue` | Issues: listar, crear, editar, cerrar |
| `gh pr` | Pull Requests: listar, crear, revisar, mergear |
| `gh release` | Releases: listar, ver, crear, descargar |
| `gh run` | GitHub Actions: listar, ver, re-ejecutar |
| `gh workflow` | Workflows: listar, ejecutar, activar/desactivar |
| `gh search` | Buscar repos, issues, PRs, código en toda GitHub |
| `gh api` | Acceso directo a la API REST/GraphQL |
| `gh auth` | Autenticación: login, logout, status |
| `gh config` | Configuración de preferencias |
| `gh alias` | Crear atajos de comandos |
| `gh extension` | Extensiones de la comunidad |

---

## Notas Importantes

- **Sin `--repo OWNER/REPO`**: la mayoría de comandos operan en el repo del directorio actual (si existe un remote de GitHub).
- **`@me`**: referencia al usuario autenticado actualmente.
- **`--web`**: casi todos los comandos de consulta aceptan `--web` para abrir en el navegador.
- **Repos privados**: `gh` puede acceder a repos privados propios si el token tiene los scopes correctos (`gh auth refresh -s repo`).
- **Rate limiting**: `gh api` respeta el rate limit de GitHub (5000 req/hora autenticado).
