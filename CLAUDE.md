# Guía de Estilo - Ciencia_Datos

## Regla principal
Antes de crear o modificar notebooks, LEER `docs/STYLE_GUIDE.md` para el detalle completo.

## Resumen ejecutivo

### Estructura de notebooks de TEORIA
```
Cell 0 (MD): # Tema N - Titulo  |  **Asignatura - GIERM**  |  ## Objetivos
Cell 1 (CODE): Imports + colores + rcParams
Cell 2 (MD): ## Formulario del Tema (tabla con $\boxed{formula}$)
Cells 3+: Secciones teoria (MD + CODE alternando)
Ejercicios resueltos: MD paso a paso (NO print explicativos)
Catalogo de tipos + Resumen final
```

### Estructura de notebooks de EJERCICIOS (Practica)
```
Cell 0 (MD): # Boletin N - Titulo  |  **Asignatura - GIERM**
Cell 1 (CODE): Imports (numpy, Fraction, colores)
Cell 2 (MD): ## Formulario del Tema (TODAS las formulas usadas)
Per-problem (4 celdas exactas):
  Cell MD: ## Problema N  |  **Enunciado:**  |  **Datos:**
  Cell MD: **Paso 1 - Titulo descriptivo:**  |  $$ecuaciones$$  |  **Resultado:** $\boxed{...}$
  Cell CODE: Verificacion numerica (MAX 2 print)
  Cell MD: ---
```

### Paleta de colores (OBLIGATORIA en todos los notebooks)
```python
COLOR_PRINCIPAL = '#2171b5'   # Azul
COLOR_FIJO      = '#636363'   # Gris
COLOR_PUNTO     = '#238b45'   # Verde
COLOR_ROJO      = '#cb181d'   # Rojo
COLOR_NARANJA   = '#ff7f00'   # Naranja
COLOR_MORADO    = '#6a3d9a'   # Morado
COLOR_CLARO     = '#a6cee3'   # Azul claro
```

### Generacion programatica (patron md()/code())
```python
import json, uuid
cells = []
def md(src):
    lines = src.strip().split('\n')
    source = [line + '\n' if i < len(lines)-1 else line for i,line in enumerate(lines)]
    cells.append({"cell_type":"markdown","metadata":{},"source":source,"id":str(uuid.uuid4())[:12]})
def code(src):
    # igual pero con outputs:[], execution_count:None
```
- Usar `\n` EXPLICITO en strings. NUNCA triple-quoted en heredocs bash.
- Verificar: `len(cell['source']) > 1` para celdas multi-linea.

### Errores PROHIBIDOS
1. **Thinking artifacts**: "Probemos...", "Hmm...", "Bueno,", "No queda", "Asumamos" → NUNCA en notebooks
2. **Resultados sin boxed**: SIEMPRE `$\boxed{resultado}$`
3. **print() excesivos**: MAX 2 por celda de codigo
4. **Escape sequences**: `\;` NO soportado en matplotlib. Usar `\,` o `r''` strings
5. **\boxed en matplotlib**: NO soportado. Solo en celdas Markdown (MathJax)
6. **Datos mezclados con pasos**: Separar en celdas distintas

### Para nudos/mallas (Tema 4 TC) - ESPECIAL
- SIEMPRE mostrar sistema con `\begin{cases}`
- SIEMPRE mostrar forma matricial con `\begin{pmatrix}`
- SIEMPRE sustitucion numerica explicita
- SIEMPRE resolver paso a paso (Cramer o sustitucion)

### Diagramas
- **Electronica**: schemdraw (elm.Resistor, elm.BjtNpn, elm.NMos, elm.Opamp, etc.)
- **Mecanismos**: matplotlib puro (draw_link, draw_joint helpers)
- **Circuitos**: schemdraw para circuitos + matplotlib para graficas

### Checklist post-creacion
- [ ] 0 thinking artifacts
- [ ] 100% resultados con $\boxed{}$
- [ ] Max 2 print() por code cell
- [ ] Formulario al inicio
- [ ] Imports organizados (numpy + colores)
- [ ] 0 SyntaxError / SyntaxWarning
- [ ] Resultados coinciden con PDF
