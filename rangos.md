# Rangos - Memoria del Proyecto

**Última actualización:** 2026-03-31

---

## 📄 Archivo: `preflop_6max_100bb_nl10.json`

### Descripción
Tablas preflop para NL10 (micro-stakes) en formato 6-max con stacks de 100bb. Estrategia GTO base para apertura preflop.

### Detalles técnicos
- **Formato:** JSON estructurado por posición
- **Estructura:** Rangos de apertura por cada posición (UTG, HJ, CO, BTN, SB)
- **Stack depth:** 100bb deep
- **Game type:** 6-max cash game

### Historial

#### 2026-03-31 - Problema de sincronización git
**Problema detectado:** Repositorio local con solo README.md, faltando preflop_6max_100bb_nl10.json.

**Investigación:** `git status` mostró:
```
Your branch is behind 'origin/main' by 2 commits
```

**Solución aplicada:**
```bash
git fetch --all
git pull
```

**Resultado:** Download exitoso del archivo JSON (369 líneas, ~25KB).

---

## 📚 Archivo: `rangos.md` (este archivo)

### Descripción
Memoria persistente del proyecto. Documento vivo que registra:
- Cada archivo JSON creado/actualizado
- Problemas encontrados y soluciones aplicadas
- Cambios en la estructura o lógica
- Notas de desarrollo e investigaciones

### Reglas
1. **Solo append:** Nunca borrar contenido previo
2. **Fechado:** Todas las entradas con fecha YYYY-MM-DD
3. **Estructura por archivo:** Cada JSON tiene su propia sección
4. **Histórico completo:** Mantener el registro cronológico

### Historial

#### 2026-03-31 - Creación del sistema de documentación
**Motivo:** Necesidad de mantener memoria persistente del proyecto, problemas encontrados y soluciones aplicadas.

**Estructura definida:**
- Sección por cada archivo JSON con:
  - Descripción del contenido
  - Detalles técnicos (formato, estructura)
  - Historial de cambios
- Reglas: solo append, siempre fechado

**Archivo creado:** `rangos.md` en la raíz del repositorio.

---

## 📊 Estado actual del repositorio

| Archivo | Líneas/Tamaño | Última modif. |
|---------|--------------|---------------|
| README.md | ~10 líneas | 2026-03-31 |
| preflop_6max_100bb_nl10.json | 369 líneas | 2026-03-31 |
| rangos.md | [este archivo] | 2026-03-31 |

---

*Documento vivo - actualizaciones futuras serán añadidas abajo*
