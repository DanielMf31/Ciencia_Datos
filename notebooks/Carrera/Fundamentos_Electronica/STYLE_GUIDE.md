# Guía de estilo para notebooks de Electrónica

Esta guía documenta todos los patrones de estilo, estructura y formato utilizados en los notebooks de la carpeta `notebooks/Electronica/`. Está pensada para que un agente de Claude pueda generar notebooks nuevos sobre otros temas manteniendo un estilo coherente.

---

## 1. Estructura general del notebook

Cada notebook sigue esta secuencia de secciones, siempre en este orden:

```
1. Título y objetivos de aprendizaje
2. Imports y configuración global
3. Introducción conceptual (analogías, explicación intuitiva)
4. Estructura/anatomía del componente (diagramas visuales)
5. Formulario completo (todas las fórmulas del tema)
6. Zonas de funcionamiento / estados / modos
7. Gráficas características (curvas teóricas generadas con Python)
8. Modelos simplificados (para cálculo manual)
9. Metodología de resolución (pasos numerados)
10. Ejemplo resuelto tipo A (el más básico, paso a paso en markdown)
11. Ejemplo resuelto tipo B (variación o caso especial)
12. Catálogo de tipos de circuitos/ejercicios
    - Para CADA tipo: teoría + ecuaciones + efecto de parámetros + ejercicio resuelto + diagrama
13. Ejercicios adicionales (casos especiales, saturación, cálculos inversos)
14. Resumen y tabla de fórmulas clave
```

Cada sección principal se separa con `---` en una celda markdown propia.

---

## 2. Celda de título (celda 0)

Siempre es la primera celda. Formato exacto:

```markdown
# Tema N - Título del tema

**Fundamentos de Electrónica - 2º GIERM**

---

## Objetivos de aprendizaje

- Objetivo 1
- Objetivo 2
- ...
```

- Título: `#` (h1), una sola vez en todo el notebook
- Subtítulo: en negrita, indica la asignatura y curso
- Separador `---`
- Lista de 4-6 objetivos concretos con viñetas `-`

---

## 3. Celda de imports y configuración (celda 1)

Siempre es la segunda celda. Contiene TODO el setup:

```python
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from matplotlib.lines import Line2D
import schemdraw
import schemdraw.elements as elm

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 13
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['figure.dpi'] = 100

COLOR_PRINCIPAL = '#2171b5'   # azul - curvas principales, datos
COLOR_RECTA = '#cb181d'       # rojo - rectas de carga, límites, saturación
COLOR_PUNTO = '#238b45'       # verde - puntos de operación, resultados OK
COLOR_N = '#a6cee3'           # azul claro - semiconductor tipo N
COLOR_P = '#b2df8a'           # verde claro - semiconductor tipo P

print('Configuración lista.')
```

### Reglas:
- `schemdraw` se usa para diagramas de circuitos eléctricos
- Los colores se definen como **constantes globales** y se reutilizan en todo el notebook
- El estilo matplotlib es `seaborn-v0_8-whitegrid`
- `figsize` por defecto: `(12, 6)` para gráficas, ajustable por celda
- El `print()` final confirma que la celda se ejecutó

---

## 4. Celdas markdown: reglas de formato

### Encabezados

```
## N. Título de sección          ← secciones principales (h2)
### N.M Título de subsección      ← subsecciones (h3)
#### Ejercicio resuelto: Tipo X   ← ejercicios (h4)
```

- **h1** (`#`): solo el título del notebook
- **h2** (`##`): secciones principales, precedidas de `---`
- **h3** (`###`): subsecciones dentro de una sección
- **h4** (`####`): ejercicios resueltos

### Separadores

Cada sección principal comienza con `---` en la primera línea de la celda markdown.

### Negrita y énfasis

- `**texto**` para conceptos clave, resultados, nombres de zonas
- `$fórmula$` inline para variables y fórmulas cortas
- `$$fórmula$$` en línea separada para ecuaciones principales
- No usar cursiva excepto para anglicismos (*Bipolar Junction Transistor*)

### Tablas

Se usan para:
1. **Formularios**: columnas `| Fórmula | Descripción |` o `| Fórmula | Uso |`
2. **Zonas de funcionamiento**: matriz de estados
3. **Modelos equivalentes**: columnas `| Entrada | Salida | Modelo |`
4. **Comparativas**: columnas `| Concepto | Tipo A | Tipo B |`
5. **Resúmenes finales**: columnas `| Fórmula clave | Uso |`

Ejemplo de tabla de formulario:
```markdown
| Fórmula | Descripción |
|---------|-------------|
| $I_C = \beta \cdot I_B$ | **Aproximación más usada** en zona activa |
```

### Listas de efectos de parámetros

Para explicar cómo cada componente afecta al circuito, se usa este patrón:

```markdown
**Cómo afectan las resistencias al punto de operación:**
- Si **$R_B$ aumenta** $\to$ $I_B$ disminuye $\to$ $I_C$ disminuye $\to$ $V_{CE}$ aumenta (se aleja de saturación)
- Si **$R_C$ aumenta** $\to$ la caída $R_C \cdot I_C$ aumenta $\to$ $V_{CE}$ disminuye (puede saturar)
```

La flecha `$\to$` conecta causa con efecto en cadena.

---

## 5. Fórmulas LaTeX

### Inline vs display

- **Inline** `$...$`: para variables sueltas, valores numéricos, condiciones
  ```markdown
  La tensión $V_{CE} = 5.27$ V es mayor que $V_{CE_{sat}}$
  ```

- **Display** `$$...$$`: para ecuaciones principales, derivaciones, fórmulas de referencia
  ```markdown
  $$I_B = \frac{V_{CC} - V_{BE}}{R_B + R_E(\beta + 1)}$$
  ```

### Fórmulas destacadas (boxed)

Las fórmulas más importantes del tema se encierran en `\boxed{}`:
```markdown
$$\boxed{I_B = \frac{V_{CC} - V_{BE}}{R_B + R_E(\beta + 1)}}$$
```

### Convenciones LaTeX

| Elemento | LaTeX | Resultado |
|----------|-------|-----------|
| Subíndices compuestos | `V_{CE_{sat}}` | $V_{CE_{sat}}$ |
| Multiplicación | `\cdot` | $\cdot$ |
| Aproximadamente | `\approx` | $\approx$ |
| Fracción | `\dfrac{}{}` en tablas, `\frac{}{}` en display | |
| Ohmios | `\Omega` | $\Omega$ |
| Micro | `\mu` | $\mu$ |
| Implica | `\implies` | $\implies$ |
| Flecha causa-efecto | `\to` | $\to$ |
| Espacio fino | `\;` entre número y unidad | $43\;\mu\text{A}$ |
| Unidades en texto | `\text{mA}`, `\text{k}\Omega` | |

### Unidades en ecuaciones resueltas

Siempre incluir unidades con `\text{}`:
```markdown
$$I_B = \frac{12 - 0.7}{240\text{k}\Omega} = 47.08\;\mu\text{A}$$
```

---

## 6. Ejercicios resueltos en markdown

Los ejercicios se resuelven **íntegramente en celdas markdown**, NO con `print()` en Python. El código Python se reserva exclusivamente para generar gráficas y diagramas.

### Estructura de un ejercicio

```markdown
#### Ejercicio resuelto: Tipo X

**Datos:** $V_{CC} = 12$ V, $R_B = 240$ k$\Omega$, $R_C = 2.2$ k$\Omega$, $\beta = 100$

**Paso 1-2:** Suponer Activa ($V_{BE} = 0.7$ V)

**Paso 3-4:**

$$I_B = \frac{V_{CC} - V_{BE}}{R_B} = \frac{12 - 0.7}{240\text{k}\Omega} = 47.08\;\mu\text{A}$$

$$I_C = \beta \cdot I_B = 100 \times 47.08 = 4.71\;\text{mA}$$

$$V_{CE} = V_{CC} - R_C \cdot I_C = 12 - 2.2\text{k} \times 4.71 = 1.64\;\text{V}$$

**Paso 5:** $V_{CE} = 1.64$ V $> 0.2$ V $\to$ **ACTIVA confirmada.**
```

### Reglas:
- **Datos** en negrita, variables en LaTeX inline, valores con unidad
- Cada paso referenciado como **Paso N:** en negrita
- Las ecuaciones muestran: fórmula general = sustitución = resultado numérico
- El resultado final siempre incluye la **verificación** del estado
- Si la hipótesis falla, se documenta explícitamente y se repite con otro estado

### Ejercicio con cambio de hipótesis

Cuando el intento de activa falla y hay que probar saturación:

```markdown
**Intento 1 (Activa):**
$$V_{CE} = ... = -2.9\;\text{V}$$
$V_{CE}$ es **negativo** $\to$ imposible $\to$ **la hipótesis de activa falla**.

**Intento 2 (Saturación):** $V_{BE} = 0.8$ V, $V_{CE} = 0.2$ V
...
**Verificar**: $I_C < \beta \cdot I_B$ $\to$ **SATURACIÓN confirmada.**
```

---

## 7. Diagramas de circuitos con schemdraw

Los diagramas se generan con `schemdraw` en celdas de código separadas, **justo después** del ejercicio resuelto en markdown.

### Patrón de código

```python
fig, ax = plt.subplots(figsize=(7, 6))
ax.set_title('Tipo X: Nombre', fontsize=14, fontweight='bold')
d = schemdraw.Drawing(canvas=ax)
# ... componentes ...
d.draw()
plt.tight_layout()
plt.show()
```

### Reglas:
- `figsize=(7, 6)` o `(8, 7)` para diagramas de circuito (más cuadrados)
- `canvas=ax` para integrar schemdraw en matplotlib
- Título con `ax.set_title()`, no con schemdraw
- Etiquetas de componentes con LaTeX: `label('$R_C$', loc='left')`
- Usar `elm.BjtNpn(circle=True)` o `elm.BjtPnp(circle=True)` para transistores
- Usar `elm.Dot(open=True).label('$V_{CC}$')` para nodos de alimentación
- Usar `elm.Ground()` para masa
- **No guardar en archivo** (`plt.savefig` eliminado), solo `plt.show()`

### Componentes schemdraw más usados

```python
elm.Resistor()          # Resistencia
elm.SourceV()           # Fuente de tensión
elm.BjtNpn(circle=True) # Transistor NPN
elm.BjtPnp(circle=True) # Transistor PNP
elm.Ground()            # Masa/tierra
elm.Dot(open=True)      # Nodo de alimentación
elm.Line()              # Cable
elm.CurrentLabelInline() # Etiqueta de corriente
```

### Posicionamiento

```python
d += elm.Resistor().right().label('$R$')     # dirección + etiqueta
d += elm.Line().up().length(3)               # longitud explícita
d += elm.Line().at(bjt.base).left()          # desde un punto del BJT
d += elm.Line().toy(top)                     # hasta la coordenada Y de 'top'
d += elm.Line().tox(bjt.base)               # hasta la coordenada X de un punto
```

---

## 8. Gráficas con matplotlib

### Tipos de gráficas usadas

1. **Curvas características** (exponenciales, familias de curvas)
2. **Rectas de carga con punto de operación**
3. **Diagramas de estructura** (con patches)
4. **Comparativas** (subplots lado a lado)
5. **Efectos de parámetros** (barrido de una variable)
6. **Modelos linealizados** (3x2 subplots)

### Patrón general

```python
fig, ax = plt.subplots(figsize=(12, 7))

# Datos y cálculos
# ...

# Curvas
ax.plot(x, y, color=COLOR_PRINCIPAL, lw=2.5, label='...')

# Punto de operación
ax.plot(x_op, y_op, 'o', color=COLOR_PUNTO, ms=14, zorder=5, label='...')

# Anotación del punto
ax.annotate(f'A\n$V_{{CE}}={vce:.1f}$ V\n$I_C={ic:.1f}$ mA',
            xy=(x_op, y_op), xytext=(x_op+1.5, y_op+1.5),
            fontsize=12, color=COLOR_PUNTO, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=COLOR_PUNTO, lw=2),
            bbox=dict(boxstyle='round', facecolor='white', edgecolor=COLOR_PUNTO))

# Ejes
ax.set_xlabel(r'$V_{CE}$ (V)')
ax.set_ylabel(r'$I_C$ (mA)')
ax.set_title('Título descriptivo')
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

### Reglas críticas:
- **SIEMPRE usar raw strings** (`r'...'`) para etiquetas con LaTeX: `r'$V_{CE}$ (V)'`
- Esto evita `SyntaxWarning: invalid escape sequence` con caracteres como `\c`, `\m`, `\g`, `\p`
- Colores: usar las constantes globales (`COLOR_PRINCIPAL`, `COLOR_RECTA`, `COLOR_PUNTO`)
- Grosor de línea: `lw=2` para curvas normales, `lw=2.5` para la recta de carga o curva principal
- Puntos de operación: `'o'` con `ms=14` y `zorder=5`
- Grid siempre activado: `ax.grid(True, alpha=0.3)`
- `plt.tight_layout()` antes de `plt.show()`
- **No guardar en archivo**, solo mostrar

### Familias de curvas

Para dibujar varias curvas parametrizadas (ej. familia de salida):

```python
for ib, color in zip([10e-6, 20e-6, 40e-6], ['#6baed6', '#3182bd', '#08519c']):
    ic = beta * ib * (1 + V_CE / V_A) * np.clip((np.tanh((V_CE - 0.2) / 0.08) + 1) / 2, 0, 1)
    ax.plot(V_CE, ic * 1e3, color=color, lw=2)
```

La transición suave de saturación a activa se modela con `tanh`:
```python
factor = np.clip((np.tanh((V_CE - V_CE_sat) / 0.08) + 1) / 2, 0, 1)
```

### Subplots comparativos

```python
fig, axes = plt.subplots(1, 2, figsize=(16, 7))  # lado a lado
fig, axes = plt.subplots(3, 2, figsize=(14, 16))  # 3 filas (ej. modelos linealizados)
```

### Zonas de color de fondo

```python
ax.axvspan(x_inicio, x_fin, alpha=0.15, color='lightblue', label='Zona')
ax.axvline(x=valor, color='gray', ls='--')
```

---

## 9. Estructura de la sección "Catálogo de tipos"

Esta es la sección más extensa y sigue un patrón repetitivo para cada tipo de circuito:

### Para cada tipo:

```
1. Celda markdown (h3): Nombre del tipo + ecuaciones boxed + explicación de efecto de cada resistencia
2. Celda markdown (h4): Ejercicio resuelto paso a paso en LaTeX
3. Celda code: Diagrama schemdraw del circuito
```

### Celda de tipo (markdown)

```markdown
### 10.N Tipo N: Nombre ($componentes$)

Descripción breve del circuito y su propósito.

$$\boxed{I_B = \frac{...}{...}} \qquad I_C = \beta \cdot I_B \qquad V_{CE} = ...$$

**Cómo afectan las resistencias al punto de operación:**
- Si **$R_X$ aumenta** $\to$ efecto en cadena...
- Si **$R_X$ disminuye** $\to$ efecto contrario...

**Ventaja / Desventaja / Truco:**
...
```

### Tabla resumen al final

La sección de catálogo termina con una tabla resumen de fórmulas:

```markdown
| Tipo | Fórmula de $I_B$ | Qué ve la base |
|------|-------------------|----------------|
| 1. Pol. fija | $\dfrac{V_{CC} - V_{BE}}{R_B}$ | Solo $R_B$ |
| ... | ... | ... |
```

---

## 10. Idioma y convenciones

### Idioma
- **Todo en español**: texto, comentarios de código, títulos de gráficas, etiquetas de ejes
- Variables y símbolos eléctricos en notación estándar internacional ($V_{CE}$, $I_B$, $\beta$)
- Anglicismos aceptados en cursiva: *Bipolar Junction Transistor*, *Early*

### Comentarios en código
- Breves, una línea, en español
- Primer comentario del bloque describe la gráfica: `# Curva característica de ENTRADA`
- No documentar lo obvio

### Tono
- Directo y técnico pero accesible
- Explicar el "por qué", no solo el "qué"
- Usar **negritas** para conceptos que el estudiante debe memorizar
- Incluir "trucos para el examen" cuando aplique
- Señalar "errores frecuentes" cuando haya trampas comunes

### Precisión numérica
- Corrientes en $\mu$A o mA según magnitud
- Tensiones en V con 2 decimales
- Resistencias en $\Omega$ o k$\Omega$
- En ecuaciones resueltas: mostrar sustitución numérica completa

---

## 11. Reglas técnicas para evitar errores

### Raw strings obligatorias

En TODA cadena de Python que contenga LaTeX para matplotlib:

```python
# CORRECTO
ax.set_xlabel(r'$V_{CE}$ (V)')
ax.text(0.5, 0.5, r'$\beta \cdot I_B$')

# INCORRECTO (genera SyntaxWarning)
ax.set_xlabel('$V_{CE}$ (V)')    # \c es escape inválido
ax.text(0.5, 0.5, '$\mu$A')      # \m es escape inválido
```

### f-strings con LaTeX

Cuando se necesita interpolar valores Y usar LaTeX, usar doble llave:

```python
ax.annotate(f'$V_{{CE}}={vce:.1f}$ V', ...)  # {{ }} escapa las llaves
```

### Cálculos

- Los cálculos numéricos se hacen en las celdas de código de las gráficas (para posicionar puntos)
- Los resultados paso a paso se muestran en markdown, NO con `print()`
- Verificar siempre que los valores del markdown coinciden con los del código

---

## 12. Sección obligatoria: Catálogo de tipos de ejercicios

Cada notebook DEBE terminar (antes del resumen final) con una sección extensa titulada **"Catálogo completo de ejercicios: todos los patrones"** que clasifique TODOS los tipos de problemas que pueden aparecer en exámenes.

### Estructura del catálogo

1. **Tabla resumen** al inicio: lista todos los tipos con columnas `| # | Tipo | Componentes | Ecuación clave | Dificultad |`

2. **Para cada tipo de ejercicio**:
   - Celda markdown (h3): nombre del tipo + ecuaciones boxed + **cómo afecta cada componente** al resultado
   - Celda markdown (h4): ejercicio resuelto paso a paso en LaTeX
   - Celda code (opcional): diagrama schemdraw del circuito

3. **Tipos especiales** al final:
   - Determinar el estado/zona desde datos dados
   - Calcular parámetros desde el punto de operación
   - Casos donde la hipótesis inicial falla y hay que cambiar

4. **Tabla resumen final** de fórmulas por tipo de circuito

### Por qué es obligatorio

Esta sección es la más importante del notebook porque permite al estudiante:
- Reconocer patrones de circuitos al instante
- Saber qué ecuación usar sin pensar
- Entender el efecto de cada resistencia/componente
- Anticipar si habrá ecuación cuadrática o no

### Ejemplo de lista de tipos (adaptable a cada tema)

Para transistores (BJT/FET): tipos según la topología de resistencias.
Para OPAM: tipos según la configuración (inversor, no inversor, sumador, etc.).
Para pequeña señal: tipos según el dispositivo (diodo, BJT, MOSFET) y la configuración.

---

## 13. Checklist para crear un notebook nuevo

1. [ ] Celda 0: título + objetivos
2. [ ] Celda 1: imports con colores globales y estilo matplotlib
3. [ ] Introducción con analogía intuitiva
4. [ ] Diagramas de estructura del componente
5. [ ] Formulario completo con tablas `| Fórmula | Descripción |`
6. [ ] Fórmulas principales con `\boxed{}`
7. [ ] Gráficas características con curvas generadas en Python
8. [ ] Modelos simplificados para cálculo manual
9. [ ] Metodología de resolución en pasos numerados
10. [ ] Al menos 2 ejemplos resueltos completos en markdown
11. [ ] Catálogo de todos los tipos de circuitos/ejercicios
12. [ ] Para cada tipo: ecuaciones + efecto de parámetros + ejercicio + diagrama
13. [ ] Ejercicios adicionales con casos especiales
14. [ ] Tabla resumen final de fórmulas clave
15. [ ] Todas las cadenas LaTeX en código usan `r'...'`
16. [ ] Sin `print()` para resoluciones, todo en markdown
17. [ ] Sin `plt.savefig()`, solo `plt.show()`
18. [ ] Verificar cálculos numéricos con `ast.parse()` y ejecución
