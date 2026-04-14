# Skill: Usar fd para búsquedas de archivos

## Propósito

Reemplazar el uso de herramientas nativas como `glob` y `find` por `fd` para lograr búsquedas de archivos más rápidas, eficientes y confiables.

## Cuándo usar este Skill

Cuando el usuario pida:
- "Encontrar archivos..."
- "Buscar archivos..."
- "Listar archivos..."
- "Dónde está...?"
- "Qué archivos hay en..."

## Instrucciones para el modelo

### ✅ Usar fd en lugar de glob/find

`fd` es una alternativa moderna a `find` escrita en Rust, mucho más rápida y con mejor UX.

### Sintaxis básica de fd

```fish
fd [patrón] [ruta] [opciones]
```

### Búsquedas comunes

```fish
# Buscar por nombre (equivalente a glob)
fd "nombre.txt"
fd "*.ts"
fd -e md  # por extensión

# Buscar en directorio específico
fd "pattern" /ruta/proyecto

# Encontrar solo directorios
fd -t d "node_modules"

# Encontrar solo archivos
fd -t f

# Buscar con regex
fd "^README.*\.md$"

# Ignorar .gitignore automáticamente
fd  # ya lo hace por defecto
```

### Opciones útiles

| Flag | Descripción |
|------|-------------|
| `-e, --extension` | Filtrar por extensión |
| `-t, --type` | Tipo: `f` (file), `d` (directory) |
| `-l, --limit` | Limitar resultados (importante para HDD) |
| `-i, --ignore-case` | Case insensitive |
| `--exclude` | Excluir patrones |
| `--threads` | Número de threads (usar 1 en HDD) |

### Ejemplos prácticos

**Ejemplo 1: Buscar archivos TypeScript**
```fish
Shell fd -e ts
```

**Ejemplo 2: Encontrar archivos con límite (importante para HDD)**
```fish
Shell fd "*.rs" -l 20
```

**Ejemplo 3: Buscar en carpeta específica**
```fish
Shell fd "test" src/
```

**Ejemplo 4: Encontrar directorios**
```fish
Shell fd -t d "node_modules"
```

**Ejemplo 5: Buscar y excluir patrones**
```fish
Shell fd "*.log" --exclude "target"
```

### Para sistemas con HDD + recursos limitados

```fish
# Usar solo 1 thread para no saturar el disco
fd "pattern" --threads 1 -l 50
```

## Ventajas de fd

- ✅ **Más rápido** que find/glob (implementado en Rust)
- ✅ **Output más limpio** y coloreado por defecto
- ✅ **Ignora .gitignore** automáticamente
- ✅ **Sintaxis más simple** y legible
- ✅ **Better regex support**
- ✅ **Threads configurables** para sistemas lentos

## Notas importantes

- Si `fd` no está disponible, caer a `find` o `glob` como fallback
- Para sistemas con HDD, siempre usar `--threads 1` y `-l` para limitar resultados
- Combinar con `Shell` tool para ejecutar