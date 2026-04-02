# Guia de Estilo Completa - Notebooks de Ciencia_Datos

> Este archivo contiene la guia de estilo detallada para crear y mantener notebooks.
> El resumen ejecutivo esta en `CLAUDE.md` (raiz del proyecto) que se carga automaticamente.

---

---
## 7. Como se refleja esto en nuestros notebooks

Los notebooks de esta base de conocimiento ya siguen el patron sandwich sin que lo hayamos llamado asi:

| Elemento del notebook | Enfoque | Funcion |
|-----------------------|---------|---------|
| Celda 0: Titulo + contexto + "por que importa" | Top-Down | Te dice DE QUE va y POR QUE lo necesitas |
| **Formulario del tema** (tabla de formulas boxed al inicio) | Top-Down | Mapa de todas las herramientas matematicas del tema |
| Celdas de teoria con formulas | Bottom-Up | Explica cada pieza en detalle |
| Celdas de codigo con diagramas matplotlib | Bottom-Up | Visualizacion de mecanismos, circuitos, respuestas |
| Celdas de codigo con ejemplos numericos | Bottom-Up | Practica concreta con numeros reales |
| Ejercicios resueltos paso a paso (Paso 1, Paso 2...) | Bottom-Up | Practica guiada con explicaciones detalladas |
| Catalogo de tipos de ejercicios | Top-Down | Vision panoramica de todos los patrones posibles |
| Tabla final de resumen + errores frecuentes | Top-Down | Reconecta todo, vision panoramica |

### Estructura estandar de cada notebook de Carrera

Todos los notebooks siguen esta estructura exacta:

```
Cell 0 (MD):  # Tema N - Titulo
              **Asignatura - GIERM**
              ---
              ## Objetivos de aprendizaje

Cell 1 (CODE): Imports + constantes de color + rcParams + helpers de dibujo

## 1. Formulario del Tema    ← TODAS las formulas en tabla con $\boxed{}$
## 2-8. Secciones de teoria  ← MD + CODE alternando (teoria + diagrama)
## 9. Ejercicios resueltos   ← Paso a paso con $\boxed{resultado}$
## 10. Catalogo de ejercicios ← Tabla de tipos + ejemplo resuelto por tipo
## 11. Resumen y formulas clave ← Tabla final + errores frecuentes
```

### Patrones de notebooks segun asignatura

| Asignatura | Patron principal | Ejemplo |
|------------|-----------------|---------|
| **Electronica** | Teoria + diagramas schemdraw + ejercicios DC+AC + catalogo de 8 tipos | `05_modelos_pequena_senal.ipynb` |
| **Circuitos** | Teoria + schemdraw + ejercicios Kirchhoff/Thevenin/fasores | `07_corriente_alterna.ipynb` |
| **Control** | Teoria + simulacion scipy/control + graficas de respuesta temporal/frecuencial | `03_respuesta_temporal.ipynb` |
| **Matematicas** | Teoria + calculo simbolico (sympy) + tabla de formulas | `05_tabla_integrales_edp.ipynb` |
| **Mecanismos** | Diagramas matplotlib puro + calculo numerico (fsolve, Jacobiano) + ejercicios paso a paso | `02_cinematica_mecanismos.ipynb` |
| **ML/DL** | Teoria + codigo ejecutable + graficas explicativas | `lstm-redes-recurrentes.ipynb` |

### Teoria de Mecanismos: patron propio (8 notebooks)

Los notebooks de Mecanismos tienen un patron distinto al resto por la naturaleza del contenido:

| # | Notebook | Contenido |
|---|----------|-----------|
| 01 | `01_introduccion_gdl.ipynb` | Gruebler, Grashof, pares, inversiones, angulo transmision |
| 02 | `02_cinematica_mecanismos.ipynb` | fsolve + Jacobiano, CIR, analisis completo 4-barras y biela-manivela |
| 03 | `03_solido_rigido_cinematica.ipynb` | Chasles, Poisson, Coriolis, movimiento relativo |
| 04 | `04_dinamica_mecanismos.ipynb` | D'Alembert, DCL, potencias virtuales, equilibrado rotores |
| 05 | `05_vibraciones_mecanicas.ipynb` | Vibracion libre/forzada, Lagrange, transmisibilidad |
| 06 | `06_sintesis_mecanismos.ipynb` | Sintesis estructural/dimensional, Freudenstein, Chebyshev |
| 07 | `07_engranajes_trenes.ipynb` | Evolvente, modulo, trenes ordinarios/compuestos, planetarios Willis |
| 08 | `08_formulario_completo.ipynb` | Formulario de referencia rapida de TODOS los temas |

**Diferencias clave con otros notebooks:**
- **NO usa schemdraw** (solo para circuitos electricos). Todos los diagramas de mecanismos se dibujan con `matplotlib.patches`, `ax.plot()`, helpers `draw_link()`, `draw_joint()`, `draw_ground()`
- **Calculo numerico pesado:** `scipy.optimize.fsolve` para posiciones (no lineal), `np.linalg.solve` para velocidades/aceleraciones (lineal via Jacobiano)
- **Patron warm-start:** `x0 = sol` de la iteracion anterior para que fsolve converja
- **3-subplot format** para cinematica: posicion, velocidad, aceleracion vs angulo de entrada

### Guia tecnica: crear notebooks programaticamente

Cuando un notebook tiene muchas celdas (>20), es mas eficiente generarlo con un script Python en vez de celda a celda. Lecciones aprendidas:

**Formato correcto del source en .ipynb:**
```python
# CORRECTO: lista de lineas, cada una con \n al final (excepto la ultima)
"source": ["# Titulo\n", "\n", "Texto de la celda\n", "Ultima linea"]

# INCORRECTO: una sola linea sin saltos
"source": ["# TituloTexto de la celdaUltima linea"]
```

**Patron de generacion que funciona:**
```python
import json, uuid

cells = []

def md(src):
    lines = src.strip().split('\n')
    source = [line + '\n' if i < len(lines) - 1 else line
              for i, line in enumerate(lines)]
    cells.append({"cell_type": "markdown", "metadata": {},
                  "source": source, "id": str(uuid.uuid4())[:12]})

def code(src):
    lines = src.strip().split('\n')
    source = [line + '\n' if i < len(lines) - 1 else line
              for i, line in enumerate(lines)]
    cells.append({"cell_type": "code", "metadata": {},
                  "source": source, "outputs": [],
                  "execution_count": None, "id": str(uuid.uuid4())[:12]})

# Usar \n explicitos dentro de strings (NO triple-quoted en heredocs):
md("# Titulo\n\n**Subtitulo**\n\n---\n\n## Seccion 1")
code("import numpy as np\nimport matplotlib.pyplot as plt\n\nprint('ok')")
```

**Errores a evitar:**
1. **NO usar triple-quoted strings dentro de heredocs bash** (`<< 'EOF'`): los `\n` del Python se interpretan como texto literal y `split('\n')` produce 1 sola linea
2. **Siempre verificar** que `len(cell['source']) > 1` para celdas multi-linea
3. **Usar `\n` explicitos** dentro de strings normales (comillas simples o dobles)

### Paleta de colores estandar (todos los notebooks de Carrera)

```python
COLOR_PRINCIPAL = '#2171b5'   # Azul - curvas principales, barras
COLOR_FIJO      = '#636363'   # Gris - barra fija, ground
COLOR_PUNTO     = '#238b45'   # Verde - resultados, puntos Q
COLOR_ROJO      = '#cb181d'   # Rojo - fuerzas, errores, alertas
COLOR_NARANJA   = '#ff7f00'   # Naranja - secundario, angulos
COLOR_MORADO    = '#6a3d9a'   # Morado - terciario
COLOR_CLARO     = '#a6cee3'   # Azul claro - rellenos, fondos
```

### Asignaturas cubiertas actualmente

| Asignatura | Carpeta | Notebooks | Contenido principal |
|------------|---------|-----------|---------------------|
| Fundamentos de Electronica | `Fundamentos_Electronica/` | 5 | Diodo, BJT, FET, OPAM, pequena senal |
| Teoria de Circuitos | `Teoria_Circuitos/` | 8 | DC, AC, transitorios, fasores, trifasicos |
| Ampliacion de Matematicas | `Ampliacion_Matematicas/` | 5 | Laplace, EDOs, Fourier, EDPs |
| Fundamentos de Control | `Fundamentos_Control/` | 9 | Sistemas, modelado, Bode, Nyquist, PID |
| Teoria de Mecanismos | `Teoria_Mecanismos/` | 8 | GDL, cinematica, dinamica, vibraciones, sintesis, engranajes |

---

## Resumen

| Concepto | Descripcion |
|----------|-------------|
| **Top-Down** | Del panorama general a los detalles. Como mirar el mapa antes de caminar |
| **Bottom-Up** | De las piezas individuales al panorama. Como aprender calles y construir el mapa |
| **Enfoque Sandwich** | Combinar ambos: TD -> BU -> TD. Lo mejor de ambos mundos |
| **Pase 1 (TD)** | Indice, estructura, "para que sirve" (~30 min) |
| **Pase 2 (BU)** | Estudio detallado, ejercicios, derivaciones (grueso del tiempo) |
| **Pase 3 (TD)** | Conectar todo, mapa conceptual, vision completa (~30 min) |
| **Matematicas** | Mas peso en bottom-up (necesitas las herramientas) |
| **Mecanismos** | Mucho bottom-up (calculo numerico) + diagramas matplotlib puro |
| **Ingenieria aplicada** | Mas equilibrado entre TD y BU |
| **Nuestros notebooks** | Patron: formulario -> teoria+diagramas -> ejercicios -> catalogo -> resumen |

### Convencion de nombrado

- Archivos: `NN_snake_case_titulo.ipynb` (NN = numero de 2 digitos)
- Siempre `1` = barra fija, `2` = entrada (en mecanismos)
- Colores: paleta estandar de 7 colores (ver arriba)
- Formulas clave: siempre en `$\boxed{formula}$`
- Ejercicios: **Datos:** + **Paso N:** + **Resultado:** `$\boxed{valor}$`

### Patron gold standard para notebooks de ejercicios resueltos

Cuando se crean notebooks con ejercicios resueltos de boletines, TODOS deben seguir este patron exacto:

#### Estructura obligatoria del notebook

```
Cell 0 (MD):  # Boletin N - Titulo del Tema
              **Asignatura - 2o GIERM**

Cell 1 (CODE): import numpy as np
               from fractions import Fraction as F
               COLOR_PRINCIPAL = '#2171b5'  # ... paleta completa

Cell 2 (MD):  ## Formulario del Tema
              Tabla con TODAS las formulas que se usan en los ejercicios
              Cada formula en $\boxed{formula}$

Per-problem (4 celdas exactas):
  Cell MD: ## Problema N
           **Enunciado:** (copiado literal del PDF)
           **Datos:**
           - $R_1 = 10\;\Omega$
           - $V_g = 20$ V

  Cell MD: **Paso 1 - Titulo descriptivo:**
           $$formula = sustitucion = resultado$$
           **Paso 2 - Titulo descriptivo:**
           $$...$$
           **Resultado:** $\boxed{respuesta\ con\ unidades}$

  Cell CODE: # Problema N - Verificacion (max 2 print statements)

  Cell MD: ---
```

#### Errores frecuentes al generar notebooks de ejercicios (y como evitarlos)

| Error | Descripcion | Solucion |
|-------|-------------|----------|
| **Thinking artifacts** | Frases como "Probemos...", "Hmm...", "Bueno, lo importante...", "No queda directamente" | Escribir SOLO derivaciones matematicas limpias. Sin razonamientos exploratorios |
| **Resultados sin boxed** | `$$R = 25\;\Omega$$` en vez de `$\boxed{R = 25\;\Omega}$` | SIEMPRE usar `$\boxed{...}$` para el resultado final |
| **Demasiados prints** | 5-10 print() por celda de codigo | Max 2 print() por celda. Solo para verificacion numerica |
| **Datos mezclados con pasos** | Datos y solucion en la misma celda MD | Separar: 1 celda para Enunciado+Datos, otra para Pasos+Resultado |
| **Pasos sin titulo** | "Paso 1: Aplicamos KVL..." | "**Paso 1 - Resistencia equivalente:**" (titulo descriptivo) |
| **Falta formulario** | Notebook empieza directamente con problemas | Celda 2 SIEMPRE tiene el formulario del tema |
| **Imports ausentes** | Codigo usa numpy sin importarlo | Primera celda CODE tiene todos los imports |

#### Checklist de verificacion post-creacion

Despues de crear cualquier notebook de ejercicios, verificar:

- [ ] 0 thinking artifacts (buscar: "probemos", "hmm", "bueno,", "no queda", "asumamos", "parece que", "intentemos", "en realidad", "quiza")
- [ ] 100% de resultados con `$\boxed{...}$`
- [ ] Max 2 `print()` por celda de codigo
- [ ] Formulario completo en celda 2
- [ ] Imports organizados en celda 1 (numpy + Fraction + colores)
- [ ] Cada problema tiene exactamente 4 celdas: Enunciado+Datos -> Pasos+Boxed -> Code -> Separador
- [ ] 0 SyntaxError / SyntaxWarning
- [ ] Resultados coinciden con los del PDF del boletin

### Referencia de simbolos schemdraw (v0.22)

Los notebooks de electronica (Fundamentos, General, Circuitos) usan `schemdraw` para diagramas de circuitos.

#### Componentes pasivos

| Elemento | Codigo | Notas |
|----------|--------|-------|
| Resistencia | `elm.Resistor()` | IEEE (zigzag). IEC: `elm.ResistorIEC()` (rectangulo) |
| Resistencia variable | `elm.ResistorVar()` | Con flecha diagonal |
| Potenciometro | `elm.Potentiometer()` | 3 terminales |
| Condensador | `elm.Capacitor()` | Plano. `elm.Capacitor2()` = curvo |
| Condensador variable | `elm.CapacitorVar()` | Con flecha |
| Bobina | `elm.Inductor()` | `elm.Inductor2()` = estilo alternativo |
| Fusible | `elm.Fuse()` | `elm.FuseIEC()`, `elm.FuseIEEE()` |
| Cristal | `elm.Crystal()` | Para osciladores |

#### Fuentes

| Elemento | Codigo | Notas |
|----------|--------|-------|
| Fuente de tension | `elm.SourceV()` | Circulo con +/- |
| Fuente de corriente | `elm.SourceI()` | Circulo con flecha |
| Fuente controlada de tension | `elm.SourceControlledV()` | Rombo |
| Fuente controlada de corriente | `elm.SourceControlledI()` | Rombo con flecha |
| Bateria | `elm.Battery()` | `elm.BatteryCell()` = una celda |
| Fuente senoidal | `elm.SourceSin()` | AC |
| Fuente cuadrada | `elm.SourceSquare()` | Pulso |

#### Transistores MOS

| Elemento | Codigo | Anchors | Notas |
|----------|--------|---------|-------|
| NMOS | `elm.NMos()` | `gate`, `drain`, `source` | Canal N enhancement |
| PMOS | `elm.PMos()` | `gate`, `drain`, `source` | Canal P enhancement (circulo en gate) |
| NFet | `elm.NFet()` | `gate`, `drain`, `source` | Igual que NMos, estilo alternativo |
| PFet | `elm.PFet()` | `gate`, `drain`, `source` | Igual que PMos |
| JFET N | `elm.JFetN()` | `gate`, `drain`, `source` | Junction FET canal N |
| JFET P | `elm.JFetP()` | `gate`, `drain`, `source` | Junction FET canal P |

**Variantes `2`**: `elm.NMos2()`, `elm.PMos2()`, `elm.NFet2()`, `elm.PFet2()` -- estilo con cuerpo visible.

#### Transistores BJT

| Elemento | Codigo | Anchors | Notas |
|----------|--------|---------|-------|
| NPN | `elm.BjtNpn()` | `base`, `collector`, `emitter` | Flecha en emisor hacia fuera |
| PNP | `elm.BjtPnp()` | `base`, `collector`, `emitter` | Flecha en emisor hacia dentro |
| NPN Schottky | `elm.NpnSchottky()` | `base`, `collector`, `emitter` | Con diodo Schottky |
| PNP Schottky | `elm.PnpSchottky()` | `base`, `collector`, `emitter` | Con diodo Schottky |
| NPN foto | `elm.NpnPhoto()` | `base`, `collector`, `emitter` | Fototransistor |

**Variantes `2`**: `elm.BjtNpn2()`, `elm.BjtPnp2()` -- estilo con cuerpo visible.

#### Diodos

| Elemento | Codigo | Notas |
|----------|--------|-------|
| Diodo | `elm.Diode()` | Generico |
| Zener | `elm.Zener()` | Diodo Zener |
| Schottky | `elm.Schottky()` | Barrera Schottky |
| LED | `elm.LED()` | Con flechas de luz. `elm.LED2()` = estilo alternativo |
| Fotodiodo | `elm.Photodiode()` | Con flechas entrantes |
| Varactor | `elm.Varactor()` | Capacitancia variable |

#### Amplificadores operacionales

| Elemento | Codigo | Anchors | Notas |
|----------|--------|---------|-------|
| OpAmp | `elm.Opamp()` | `in1` (+), `in2` (-), `out`, `vd` (V+), `vs` (V-) | Triangulo estandar |

#### Conexiones y miscelaneos

| Elemento | Codigo | Notas |
|----------|--------|-------|
| Linea | `elm.Line()` | Cable/conexion |
| Punto | `elm.Dot()` | Nodo de conexion |
| Tierra | `elm.Ground()` | `elm.GroundChassis()`, `elm.GroundSignal()` |
| Vdd | `elm.Vdd()` | Alimentacion positiva |
| Vss | `elm.Vss()` | Alimentacion negativa |
| Switch | `elm.Switch()` | Interruptor simple |
| Switch SPDT | `elm.SwitchSpdt()` | Conmutador |
| Flecha | `elm.Arrow()` | Para indicar corrientes |
| Gap | `elm.Gap()` | Hueco con voltaje |
| Tag/Label | `elm.Tag()` / `elm.Label()` | Etiquetas |
| Transformador | `elm.Transformer()` | Dos bobinas acopladas |
| 555 | `elm.Ic555()` | Circuito integrado 555 |

#### Metodos comunes de posicionamiento

```python
# Direccion
elm.Resistor().right()       # Hacia la derecha (defecto)
elm.Resistor().left()        # Hacia la izquierda
elm.Resistor().up()          # Hacia arriba
elm.Resistor().down()        # Hacia abajo

# Etiquetas
elm.Resistor().label(r'$R_1$')                    # Etiqueta por defecto
elm.Resistor().label(r'$R_1$', loc='top')          # Arriba
elm.SourceV().label(r'$V_s$', loc='left')          # Izquierda

# Longitud y posicion
elm.Line().length(2)                               # Longitud especifica
elm.Line().tox(d.elements[0].absanchors['start'].x)  # Hasta coordenada X
elm.Line().toy(d.elements[0].absanchors['start'].y)  # Hasta coordenada Y

# Acceder a posicion actual y anchors
d.here                                             # Posicion actual del cursor
elem.absanchors['start']                           # Anchor de inicio (Point)
elem.absanchors['end']                             # Anchor de fin (Point)
elem.absanchors['start'].x                         # Coordenada X
elem.absanchors['start'].y                         # Coordenada Y
```

**IMPORTANTE** (schemdraw 0.22): `elem.endpoints` es un **metodo**, NO una propiedad. Usar `elem.absanchors['start']` y `elem.absanchors['end']` en su lugar.

### Errores frecuentes en notebooks y como evitarlos

| Error | Causa | Solucion |
|-------|-------|----------|
| `SyntaxWarning: invalid escape sequence '\;'` | `\;` en f-string o string normal (no raw) | Usar `r'...'` para LaTeX, o `\\ ` (backslash-espacio) en f-strings |
| `ValueError: \boxed not supported` | `\boxed{}` en titulo/label de matplotlib | `\boxed` solo funciona en celdas Markdown (MathJax). En matplotlib usar `\fbox{}` o nada |
| `ParseException` en matplotlib LaTeX | `\;` (medium space) en mathtext | Reemplazar `\;` por `\,` (thin space, soportado) en `set_title`, `annotate`, `label` |
| `MissingIDFieldWarning` | Celdas sin campo `id` en el JSON | Asegurar que el script de generacion incluye `"id": str(uuid.uuid4())[:12]` |
| `elem.endpoints[0]` TypeError | `endpoints` es metodo en schemdraw 0.22 | Usar `elem.absanchors['start']` en vez de `elem.endpoints[0]` |
| Timeout en nbconvert | Celda con calculo pesado o schemdraw lento | Reducir array sizes, simplificar, o aumentar timeout |

**Regla de oro para LaTeX en Python:**
- **Celdas Markdown**: todo el LaTeX funciona (`\;`, `\boxed`, etc.) -- lo renderiza MathJax
- **Codigo matplotlib** (`set_title`, `annotate`, `label`): solo mathtext parcial -- NO soporta `\;`, `\boxed`, `\text{}` limitado
- **schemdraw labels**: soporta LaTeX completo via matplotlib -- usar `r'$...$'` (raw strings)
- **f-strings con LaTeX**: NUNCA usar `\;` o `\,` directamente -- usar concatenacion: `f'valor={x}' + r'$\,\Omega$'`

**Temas relacionados:**
- [Roadmap de aprendizaje](../00_roadmap_aprendizaje.ipynb) -- ejemplo de herramienta top-down pura
- Todos los notebooks de teoria siguen el patron sandwich descrito aqui