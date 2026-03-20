# Índice de Conceptos - Ciencia de Datos

Índice comprensivo de todos los conceptos aplicados en este proyecto de aprendizaje.
Cubre dos sub-proyectos:

| Sub-proyecto | Datos | Ubicación de notebooks |
|---|---|---|
| **Telemetría Vehicular** | Datos simulados | `notebooks/telemetria_vehicular/phase1-6/` |
| **NYC Taxi** | Datos reales (BigQuery) | `notebooks/nyc_taxi/phase1-6/` |
| **Formulario Estadístico** | Referencia de fórmulas | `notebooks/nyc_taxi/00_formulario_estadistico.ipynb` |

> **Convención:** Los notebooks de Telemetría se referencian como `telemetria_vehicular/phase{N}/{archivo}`.
> Los notebooks de NYC Taxi se referencian como `nyc_taxi/phase{N}/{archivo}`.
> El formulario estadístico contiene todas las fórmulas con teoría, visualizaciones y ejemplos.

---

## 1. Fundamentos de Datos

### NumPy - Arrays

**Definición:** Estructura de datos multidimensional homogénea (`ndarray`) que permite almacenar y manipular colecciones de datos numéricos de forma eficiente.
**Usado en:** `telemetria_vehicular/phase1/01_numpy_fundamentals.ipynb`
**Referencia:** [numpy.ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html)

### NumPy - Operaciones Vectorizadas

**Definición:** Operaciones que se aplican elemento a elemento sobre arrays completos sin necesidad de bucles explícitos, aprovechando optimizaciones en C bajo el capó.
**Usado en:** `telemetria_vehicular/phase1/01_numpy_fundamentals.ipynb`
**Referencia:** [Vectorization en NumPy](https://numpy.org/doc/stable/reference/ufuncs.html)

### NumPy - Broadcasting

**Definición:** Mecanismo que permite operar entre arrays de diferentes dimensiones, expandiendo automáticamente el array más pequeño para que las formas sean compatibles.
**Usado en:** `telemetria_vehicular/phase1/01_numpy_fundamentals.ipynb`
**Referencia:** [Broadcasting](https://numpy.org/doc/stable/user/basics.broadcasting.html)

### NumPy - Generación Aleatoria

**Definición:** Módulo `numpy.random` para generar números pseudoaleatorios con diversas distribuciones (normal, uniforme, Poisson, etc.), esencial para simulaciones y muestreo.
**Usado en:** `telemetria_vehicular/phase1/01_numpy_fundamentals.ipynb`, `telemetria_vehicular/phase1/03_vehicle_simulator.ipynb`, `telemetria_vehicular/phase1/04_survey_simulator.ipynb`
**Referencia:** [numpy.random](https://numpy.org/doc/stable/reference/random/index.html)

### Pandas - DataFrame

**Definición:** Estructura tabular bidimensional con etiquetas en filas y columnas, equivalente a una tabla SQL o una hoja de cálculo en memoria.
**Usado en:** `telemetria_vehicular/phase1/02_pandas_fundamentals.ipynb`, `nyc_taxi/phase1/02_pandas_nyc_taxi.ipynb`
**Referencia:** [pandas.DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html)

### Pandas - Series

**Definición:** Estructura unidimensional etiquetada, equivalente a una columna individual de un DataFrame. Soporta operaciones vectorizadas y alineación por índice.
**Usado en:** `telemetria_vehicular/phase1/02_pandas_fundamentals.ipynb`, `nyc_taxi/phase1/02_pandas_nyc_taxi.ipynb`
**Referencia:** [pandas.Series](https://pandas.pydata.org/docs/reference/api/pandas.Series.html)

### Pandas - Indexing (loc, iloc, boolean indexing)

**Definición:** Mecanismos para seleccionar subconjuntos de datos: `loc` por etiqueta, `iloc` por posición entera, y boolean indexing mediante condiciones lógicas.
**Usado en:** `telemetria_vehicular/phase1/02_pandas_fundamentals.ipynb`, `nyc_taxi/phase1/02_pandas_nyc_taxi.ipynb`
**Referencia:** [Indexing and Selecting Data](https://pandas.pydata.org/docs/user_guide/indexing.html)

### Pandas - groupby

**Definición:** Operación split-apply-combine que agrupa filas por valores de una o más columnas y aplica funciones de agregación (sum, mean, count, etc.) a cada grupo.
**Usado en:** `telemetria_vehicular/phase1/02_pandas_fundamentals.ipynb`, `telemetria_vehicular/phase2/01_univariate_telemetry.ipynb`, `nyc_taxi/phase1/02_pandas_nyc_taxi.ipynb`
**Referencia:** [pandas.DataFrame.groupby](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html)

### Pandas - merge

**Definición:** Combinación de dos DataFrames mediante columnas clave, equivalente a un JOIN en SQL. Soporta inner, left, right y outer joins.
**Usado en:** `telemetria_vehicular/phase1/05_data_merging.ipynb`
**Referencia:** [pandas.DataFrame.merge](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html)

### Pandas - pivot_table

**Definición:** Reorganiza datos creando una tabla cruzada con valores agregados, similar a las tablas dinámicas de Excel.
**Usado en:** `telemetria_vehicular/phase2/04_bivariate_analysis.ipynb`
**Referencia:** [pandas.pivot_table](https://pandas.pydata.org/docs/reference/api/pandas.pivot_table.html)

### Pandas - resample

**Definición:** Remuestreo de series temporales a una frecuencia diferente (upsampling o downsampling), agrupando por intervalos de tiempo.
**Usado en:** `telemetria_vehicular/phase2/02_temporal_patterns.ipynb`, `telemetria_vehicular/phase5/03_time_series_decomposition.ipynb`
**Referencia:** [pandas.DataFrame.resample](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.resample.html)

### SQL / BigQuery - SELECT, WHERE, GROUP BY

**Definición:** Cláusulas fundamentales de SQL para seleccionar columnas, filtrar filas y agrupar resultados con funciones de agregación.
**Usado en:** `nyc_taxi/phase1/02_pandas_nyc_taxi.ipynb`
**Referencia:** [BigQuery SQL Reference](https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax)

### SQL / BigQuery - JOIN

**Definición:** Operación para combinar filas de dos o más tablas basándose en columnas relacionadas (INNER, LEFT, RIGHT, FULL, CROSS).
**Usado en:** `nyc_taxi/phase1/02_pandas_nyc_taxi.ipynb`, `nyc_taxi/phase2/` *(pendiente)*
**Referencia:** [BigQuery JOIN](https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax#join_types)

### SQL / BigQuery - CASE WHEN

**Definición:** Expresión condicional en SQL que permite crear columnas derivadas basándose en lógica if-then-else dentro de una consulta.
**Usado en:** `nyc_taxi/phase1/02_pandas_nyc_taxi.ipynb`, `nyc_taxi/phase4/` *(pendiente)*
**Referencia:** [CASE Expression](https://cloud.google.com/bigquery/docs/reference/standard-sql/conditional_expressions#case)

### SQL / BigQuery - Window Functions

**Definición:** Funciones analíticas (ROW_NUMBER, RANK, LAG, LEAD, SUM OVER) que calculan valores sobre un conjunto de filas relacionadas sin colapsar el resultado.
**Usado en:** `nyc_taxi/phase2/` *(pendiente)*, `nyc_taxi/phase5/` *(pendiente)*
**Referencia:** [Analytic Functions](https://cloud.google.com/bigquery/docs/reference/standard-sql/analytic-function-concepts)

### SQL / BigQuery - TABLESAMPLE y FARM_FINGERPRINT

**Definición:** Técnicas para obtener muestras reproducibles de tablas grandes. `TABLESAMPLE` muestrea bloques, mientras que `FARM_FINGERPRINT` con `MOD` permite muestreo determinístico a nivel de fila.
**Usado en:** `nyc_taxi/phase1/02_pandas_nyc_taxi.ipynb`
**Referencia:** [TABLESAMPLE](https://cloud.google.com/bigquery/docs/table-sampling), [FARM_FINGERPRINT](https://cloud.google.com/bigquery/docs/reference/standard-sql/hash_functions#farm_fingerprint)

### SQL / BigQuery - Estimación de Costos (dry_run)

**Definición:** Ejecución de consultas en modo `dry_run` para estimar la cantidad de bytes procesados antes de ejecutar la consulta real, permitiendo controlar costos.
**Usado en:** `nyc_taxi/phase1/02_pandas_nyc_taxi.ipynb`
**Referencia:** [Dry Run Queries](https://cloud.google.com/bigquery/docs/samples/bigquery-query-dry-run)

### Tipos de Datos - Numéricos

**Definición:** Variables continuas (float) y discretas (int) que representan magnitudes medibles como velocidad, temperatura, distancia o conteos.
**Usado en:** `telemetria_vehicular/phase1/02_pandas_fundamentals.ipynb`, `telemetria_vehicular/phase1/03_vehicle_simulator.ipynb`

### Tipos de Datos - Categóricos (Nominales y Ordinales)

**Definición:** Variables nominales sin orden intrínseco (tipo de vehículo, zona) y ordinales con orden natural (nivel de satisfacción, categoría de riesgo).
**Usado en:** `telemetria_vehicular/phase1/04_survey_simulator.ipynb`, `telemetria_vehicular/phase2/03_survey_eda.ipynb`, `telemetria_vehicular/phase4/01_feature_engineering.ipynb`
**Referencia:** [pandas.Categorical](https://pandas.pydata.org/docs/user_guide/categorical.html)

### Tipos de Datos - Datetime

**Definición:** Tipo de dato para representar fechas y horas, permitiendo operaciones temporales como resampleo, diferencias de tiempo y extracción de componentes (hora, día de semana, mes).
**Usado en:** `telemetria_vehicular/phase1/03_vehicle_simulator.ipynb`, `telemetria_vehicular/phase2/02_temporal_patterns.ipynb`, `nyc_taxi/phase1/02_pandas_nyc_taxi.ipynb`
**Referencia:** [pandas.to_datetime](https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html)

### Tipos de Datos - Geoespaciales

**Definición:** Datos de latitud y longitud que representan ubicaciones geográficas, utilizados para análisis espacial y visualización en mapas.
**Usado en:** `telemetria_vehicular/phase1/03_vehicle_simulator.ipynb`, `telemetria_vehicular/phase2/05_geospatial_visualization.ipynb`, `nyc_taxi/phase1/02_pandas_nyc_taxi.ipynb`

### Limpieza de Datos - Missing Values

**Definición:** Tratamiento de valores faltantes (NaN/null) mediante detección (`isnull`), eliminación (`dropna`) o imputación (media, mediana, forward fill, interpolación).
**Usado en:** `telemetria_vehicular/phase1/05_data_merging.ipynb`, `nyc_taxi/phase1/02_pandas_nyc_taxi.ipynb`
**Referencia:** [Working with missing data](https://pandas.pydata.org/docs/user_guide/missing_data.html)

### Limpieza de Datos - Outliers

**Definición:** Identificación y tratamiento de valores atípicos usando métodos estadísticos (IQR, z-score) o reglas de negocio para decidir si eliminar, recortar o mantener.
**Usado en:** `telemetria_vehicular/phase2/01_univariate_telemetry.ipynb`, `telemetria_vehicular/phase5/05_anomaly_detection.ipynb`, `nyc_taxi/phase1/02_pandas_nyc_taxi.ipynb`

### Limpieza de Datos - Validación de Rangos

**Definición:** Verificación de que los valores caen dentro de rangos lógicos o físicamente posibles (ej: velocidad >= 0, temperatura entre -40 y 60).
**Usado en:** `telemetria_vehicular/phase1/03_vehicle_simulator.ipynb`, `nyc_taxi/phase1/02_pandas_nyc_taxi.ipynb`

### Limpieza de Datos - Duplicados

**Definición:** Detección y eliminación de registros duplicados usando `duplicated()` y `drop_duplicates()`, considerando subconjuntos de columnas clave.
**Usado en:** `telemetria_vehicular/phase1/05_data_merging.ipynb`, `nyc_taxi/phase1/02_pandas_nyc_taxi.ipynb`
**Referencia:** [pandas.DataFrame.drop_duplicates](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.drop_duplicates.html)

---

## 2. Visualización

### matplotlib - figure, axes, subplots

**Definición:** API orientada a objetos de matplotlib donde `Figure` es el contenedor y `Axes` son los paneles individuales de gráficos. `subplots()` crea grillas de múltiples gráficos.
**Usado en:** `telemetria_vehicular/phase2/01_univariate_telemetry.ipynb`, `telemetria_vehicular/phase2/02_temporal_patterns.ipynb`
**Referencia:** [matplotlib.pyplot.subplots](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html)

### matplotlib - Gráficos de Línea (line plot)

**Definición:** Representación de datos como puntos conectados por líneas, ideal para series temporales y tendencias a lo largo del tiempo.
**Usado en:** `telemetria_vehicular/phase2/02_temporal_patterns.ipynb`, `telemetria_vehicular/phase5/03_time_series_decomposition.ipynb`, `telemetria_vehicular/phase5/04_time_series_forecasting.ipynb`
**Referencia:** [matplotlib.pyplot.plot](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html)

### matplotlib - Gráficos de Barras (bar plot)

**Definición:** Representación de datos categóricos mediante rectángulos cuya altura o longitud es proporcional al valor que representan.
**Usado en:** `telemetria_vehicular/phase2/01_univariate_telemetry.ipynb`, `telemetria_vehicular/phase2/03_survey_eda.ipynb`
**Referencia:** [matplotlib.pyplot.bar](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.bar.html)

### matplotlib - Gráficos de Dispersión (scatter plot)

**Definición:** Representación de la relación entre dos variables numéricas como puntos en un plano cartesiano, útil para identificar correlaciones y patrones.
**Usado en:** `telemetria_vehicular/phase2/04_bivariate_analysis.ipynb`, `telemetria_vehicular/phase3/05_correlation_deep_dive.ipynb`
**Referencia:** [matplotlib.pyplot.scatter](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.scatter.html)

### matplotlib - Histogramas

**Definición:** Representación de la distribución de frecuencias de una variable numérica mediante barras contiguas que muestran la cantidad de observaciones en cada intervalo (bin).
**Usado en:** `telemetria_vehicular/phase2/01_univariate_telemetry.ipynb`, `telemetria_vehicular/phase3/01_probability_distributions.ipynb`
**Referencia:** [matplotlib.pyplot.hist](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.hist.html)

### seaborn - histplot / distplot

**Definición:** Funciones para visualizar distribuciones univariadas con histogramas y estimaciones de densidad kernel (KDE). `histplot` reemplazó a `distplot` en versiones modernas.
**Usado en:** `telemetria_vehicular/phase2/01_univariate_telemetry.ipynb`, `telemetria_vehicular/phase3/01_probability_distributions.ipynb`
**Referencia:** [seaborn.histplot](https://seaborn.pydata.org/generated/seaborn.histplot.html)

### seaborn - heatmap

**Definición:** Visualización matricial con colores que representa la magnitud de valores, frecuentemente usada para matrices de correlación.
**Usado en:** `telemetria_vehicular/phase2/04_bivariate_analysis.ipynb`, `telemetria_vehicular/phase3/05_correlation_deep_dive.ipynb`
**Referencia:** [seaborn.heatmap](https://seaborn.pydata.org/generated/seaborn.heatmap.html)

### seaborn - pairplot

**Definición:** Matriz de gráficos de dispersión y distribuciones para todas las combinaciones de variables numéricas, útil para exploración multivariada rápida.
**Usado en:** `telemetria_vehicular/phase2/04_bivariate_analysis.ipynb`
**Referencia:** [seaborn.pairplot](https://seaborn.pydata.org/generated/seaborn.pairplot.html)

### seaborn - violinplot

**Definición:** Combinación de un boxplot con una estimación de densidad kernel (KDE), mostrando tanto estadísticos resumen como la forma de la distribución.
**Usado en:** `telemetria_vehicular/phase2/01_univariate_telemetry.ipynb`, `telemetria_vehicular/phase3/01_probability_distributions.ipynb`
**Referencia:** [seaborn.violinplot](https://seaborn.pydata.org/generated/seaborn.violinplot.html)

### seaborn - boxplot

**Definición:** Diagrama de caja que muestra mediana, cuartiles, rango intercuartil y valores atípicos, ideal para comparar distribuciones entre grupos.
**Usado en:** `telemetria_vehicular/phase2/01_univariate_telemetry.ipynb`, `telemetria_vehicular/phase2/03_survey_eda.ipynb`
**Referencia:** [seaborn.boxplot](https://seaborn.pydata.org/generated/seaborn.boxplot.html)

### seaborn - FacetGrid

**Definición:** Estructura para crear múltiples gráficos (facetas) condicionados por una o más variables categóricas, permitiendo comparaciones visuales sistemáticas.
**Usado en:** `telemetria_vehicular/phase2/03_survey_eda.ipynb`, `telemetria_vehicular/phase2/04_bivariate_analysis.ipynb`
**Referencia:** [seaborn.FacetGrid](https://seaborn.pydata.org/generated/seaborn.FacetGrid.html)

### Plotly - Express

**Definición:** API de alto nivel de Plotly para crear gráficos interactivos con una sintaxis concisa, ideal para exploración rápida de datos.
**Usado en:** `telemetria_vehicular/phase2/06_interactive_dashboard_plotly.ipynb`, `telemetria_vehicular/phase6/02_interactive_dashboard.ipynb`
**Referencia:** [Plotly Express](https://plotly.com/python/plotly-express/)

### Plotly - Graph Objects

**Definición:** API de bajo nivel de Plotly que ofrece control completo sobre cada elemento del gráfico (traces, layouts, annotations), necesaria para visualizaciones personalizadas.
**Usado en:** `telemetria_vehicular/phase2/06_interactive_dashboard_plotly.ipynb`, `telemetria_vehicular/phase6/02_interactive_dashboard.ipynb`
**Referencia:** [Plotly Graph Objects](https://plotly.com/python/graph-objects/)

### Plotly - scatter_mapbox

**Definición:** Gráfico de dispersión sobre mapas interactivos de Mapbox, permite visualizar puntos geográficos con zoom, pan y capas de mapa base.
**Usado en:** `telemetria_vehicular/phase2/06_interactive_dashboard_plotly.ipynb`
**Referencia:** [Plotly scatter_mapbox](https://plotly.com/python/scattermapbox/)

### Plotly - rangeslider y subplots interactivos

**Definición:** Componentes interactivos como deslizadores de rango temporal y layouts con múltiples paneles sincronizados que permiten exploración dinámica.
**Usado en:** `telemetria_vehicular/phase2/06_interactive_dashboard_plotly.ipynb`, `telemetria_vehicular/phase6/02_interactive_dashboard.ipynb`
**Referencia:** [Plotly Range Slider](https://plotly.com/python/range-slider/)

### Folium - Mapas

**Definición:** Biblioteca para crear mapas interactivos basados en Leaflet.js, permite añadir capas, marcadores y controles directamente desde Python.
**Usado en:** `telemetria_vehicular/phase2/05_geospatial_visualization.ipynb`
**Referencia:** [Folium](https://python-visualization.github.io/folium/)

### Folium - HeatMap

**Definición:** Plugin de Folium que genera mapas de calor geográficos basados en densidad de puntos, útil para identificar zonas de alta concentración.
**Usado en:** `telemetria_vehicular/phase2/05_geospatial_visualization.ipynb`
**Referencia:** [folium.plugins.HeatMap](https://python-visualization.github.io/folium/plugins.html)

### Folium - Markers

**Definición:** Marcadores individuales o agrupados (MarkerCluster) sobre mapas para señalar ubicaciones específicas con popups informativos.
**Usado en:** `telemetria_vehicular/phase2/05_geospatial_visualization.ipynb`
**Referencia:** [Folium Markers](https://python-visualization.github.io/folium/quickstart.html#markers)

### Folium - Choropleth

**Definición:** Mapa temático donde las regiones geográficas se colorean según un valor numérico, útil para visualizar métricas agregadas por zona.
**Usado en:** `telemetria_vehicular/phase2/05_geospatial_visualization.ipynb`
**Referencia:** [Folium Choropleth](https://python-visualization.github.io/folium/quickstart.html#choropleth-maps)

---

## 3. Estadística Inferencial

> **📊 Referencia completa:** Todas las fórmulas estadísticas con teoría detallada, visualizaciones
> y ejemplos numéricos paso a paso están en [`nyc_taxi/00_formulario_estadistico.ipynb`](../notebooks/nyc_taxi/00_formulario_estadistico.ipynb)

### Distribución Normal

**Definición:** Distribución simétrica en forma de campana definida por media y desviación estándar. Muchos fenómenos naturales la siguen aproximadamente (Teorema Central del Límite).
**Usado en:** `telemetria_vehicular/phase3/01_probability_distributions.ipynb`
**Referencia:** [scipy.stats.norm](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.norm.html)

### Distribución Log-Normal

**Definición:** Distribución de una variable cuyo logaritmo sigue una distribución normal, típica de variables estrictamente positivas y sesgadas a la derecha (ingresos, tiempos de viaje).
**Usado en:** `telemetria_vehicular/phase3/01_probability_distributions.ipynb`, `nyc_taxi/phase3/` *(pendiente)*
**Referencia:** [scipy.stats.lognorm](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.lognorm.html)

### Distribución Gamma

**Definición:** Distribución flexible para variables positivas, generalización de la exponencial. Útil para modelar tiempos de espera y consumos.
**Usado en:** `telemetria_vehicular/phase3/01_probability_distributions.ipynb`
**Referencia:** [scipy.stats.gamma](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.gamma.html)

### Distribución Exponencial

**Definición:** Distribución del tiempo entre eventos en un proceso de Poisson, caracterizada por la propiedad de falta de memoria. Un solo parámetro (lambda/rate).
**Usado en:** `telemetria_vehicular/phase3/01_probability_distributions.ipynb`
**Referencia:** [scipy.stats.expon](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.expon.html)

### Distribución de Poisson

**Definición:** Distribución discreta que modela el número de eventos en un intervalo fijo de tiempo o espacio, dado que ocurren con tasa constante e independientemente.
**Usado en:** `telemetria_vehicular/phase3/01_probability_distributions.ipynb`
**Referencia:** [scipy.stats.poisson](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.poisson.html)

### Test de Normalidad - Shapiro-Wilk

**Definición:** Prueba estadística para evaluar si una muestra proviene de una distribución normal. Más potente para muestras pequeñas (n < 5000).
**Usado en:** `telemetria_vehicular/phase3/01_probability_distributions.ipynb`, `telemetria_vehicular/phase3/03_hypothesis_testing_telemetry.ipynb`
**Referencia:** [scipy.stats.shapiro](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.shapiro.html)

### Test de Normalidad - Kolmogorov-Smirnov (K-S)

**Definición:** Prueba no paramétrica que compara la distribución empírica de una muestra contra una distribución teórica. Aplicable a cualquier distribución de referencia.
**Usado en:** `telemetria_vehicular/phase3/01_probability_distributions.ipynb`
**Referencia:** [scipy.stats.kstest](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kstest.html)

### QQ-Plot (Quantile-Quantile Plot)

**Definición:** Gráfico diagnóstico que compara los cuantiles de la muestra contra los cuantiles teóricos. Si los puntos siguen la diagonal, la muestra se ajusta a la distribución de referencia.
**Usado en:** `telemetria_vehicular/phase3/01_probability_distributions.ipynb`, `telemetria_vehicular/phase3/03_hypothesis_testing_telemetry.ipynb`
**Referencia:** [scipy.stats.probplot](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.probplot.html)

### Intervalos de Confianza - Paramétrico

**Definición:** Rango de valores calculado a partir de la muestra que contiene el parámetro poblacional verdadero con una probabilidad dada (típicamente 95%). Asume distribución conocida.
**Usado en:** `telemetria_vehicular/phase3/02_confidence_intervals.ipynb`
**Referencia:** [scipy.stats.t.interval](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.t.html)

### Intervalos de Confianza - Bootstrap

**Definición:** Método no paramétrico que estima intervalos de confianza mediante remuestreo con reemplazo repetido (miles de veces) de la muestra original.
**Usado en:** `telemetria_vehicular/phase3/02_confidence_intervals.ipynb`
**Referencia:** [scipy.stats.bootstrap](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html)

### Test t de Student (t-test)

**Definición:** Prueba para comparar medias entre dos grupos (independientes o pareados). Asume normalidad y homogeneidad de varianzas (o usa corrección de Welch).
**Usado en:** `telemetria_vehicular/phase3/03_hypothesis_testing_telemetry.ipynb`
**Referencia:** [scipy.stats.ttest_ind](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_ind.html)

### ANOVA (Analysis of Variance)

**Definición:** Extensión del t-test para comparar medias de tres o más grupos simultáneamente. Descompone la varianza total en varianza entre grupos y dentro de grupos.
**Usado en:** `telemetria_vehicular/phase3/03_hypothesis_testing_telemetry.ipynb`, `telemetria_vehicular/phase3/04_hypothesis_testing_surveys.ipynb`
**Referencia:** [scipy.stats.f_oneway](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.f_oneway.html)

### Chi-cuadrado (Test de Independencia)

**Definición:** Prueba para evaluar si dos variables categóricas son independientes, comparando frecuencias observadas contra las esperadas bajo independencia.
**Usado en:** `telemetria_vehicular/phase3/04_hypothesis_testing_surveys.ipynb`
**Referencia:** [scipy.stats.chi2_contingency](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2_contingency.html)

### Mann-Whitney U Test

**Definición:** Alternativa no paramétrica al t-test de dos muestras independientes. Compara rangos en lugar de medias, no requiere normalidad.
**Usado en:** `telemetria_vehicular/phase3/03_hypothesis_testing_telemetry.ipynb`
**Referencia:** [scipy.stats.mannwhitneyu](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mannwhitneyu.html)

### Kruskal-Wallis Test

**Definición:** Alternativa no paramétrica a ANOVA para comparar tres o más grupos independientes basándose en rangos.
**Usado en:** `telemetria_vehicular/phase3/03_hypothesis_testing_telemetry.ipynb`
**Referencia:** [scipy.stats.kruskal](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kruskal.html)

### Correlación de Pearson

**Definición:** Medida de asociación lineal entre dos variables continuas, con rango [-1, 1]. Asume relación lineal y normalidad bivariada.
**Usado en:** `telemetria_vehicular/phase3/05_correlation_deep_dive.ipynb`, `telemetria_vehicular/phase2/04_bivariate_analysis.ipynb`
**Referencia:** [scipy.stats.pearsonr](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html)

### Correlación de Spearman

**Definición:** Correlación basada en rangos que mide asociación monótona (no necesariamente lineal). Más robusta ante outliers y no requiere normalidad.
**Usado en:** `telemetria_vehicular/phase3/05_correlation_deep_dive.ipynb`
**Referencia:** [scipy.stats.spearmanr](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html)

### Correlaciones Parciales

**Definición:** Correlación entre dos variables controlando (eliminando) el efecto de una o más variables confusoras, revelando la relación directa.
**Usado en:** `telemetria_vehicular/phase3/05_correlation_deep_dive.ipynb`
**Referencia:** [pingouin.partial_corr](https://pingouin-stats.org/build/html/generated/pingouin.partial_corr.html)

### Tamaño de Efecto - Cohen's d

**Definición:** Medida estandarizada de la diferencia entre dos medias en unidades de desviación estándar. Valores: pequeño (~0.2), medio (~0.5), grande (~0.8).
**Usado en:** `telemetria_vehicular/phase3/03_hypothesis_testing_telemetry.ipynb`
**Referencia:** [Effect Size (Wikipedia)](https://en.wikipedia.org/wiki/Effect_size#Cohen's_d)

### Tamaño de Efecto - Cramér's V

**Definición:** Medida de asociación entre dos variables categóricas basada en chi-cuadrado, normalizada al rango [0, 1].
**Usado en:** `telemetria_vehicular/phase3/04_hypothesis_testing_surveys.ipynb`
**Referencia:** [Cramér's V (Wikipedia)](https://en.wikipedia.org/wiki/Cram%C3%A9r%27s_V)

### Corrección de Bonferroni

**Definición:** Ajuste conservador del nivel de significancia cuando se realizan múltiples pruebas simultáneas. Divide alpha entre el número de comparaciones.
**Usado en:** `telemetria_vehicular/phase3/03_hypothesis_testing_telemetry.ipynb`, `telemetria_vehicular/phase3/04_hypothesis_testing_surveys.ipynb`
**Referencia:** [Bonferroni Correction](https://en.wikipedia.org/wiki/Bonferroni_correction)

### Tukey HSD (Honestly Significant Difference)

**Definición:** Prueba post-hoc tras ANOVA que identifica cuáles pares de grupos difieren significativamente, controlando la tasa de error familiar.
**Usado en:** `telemetria_vehicular/phase3/03_hypothesis_testing_telemetry.ipynb`
**Referencia:** [scipy.stats.tukey_hsd](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.tukey_hsd.html)

---

## 4. Machine Learning Supervisado

### Feature Engineering - Encoding

**Definición:** Transformación de variables categóricas a formato numérico. Incluye One-Hot Encoding (nominales), Label/Ordinal Encoding (ordinales) y Target Encoding.
**Usado en:** `telemetria_vehicular/phase4/01_feature_engineering.ipynb`, `nyc_taxi/phase4/` *(pendiente)*
**Referencia:** [sklearn.preprocessing](https://scikit-learn.org/stable/modules/preprocessing.html#encoding-categorical-features)

### Feature Engineering - Escalado

**Definición:** Normalización de rangos numéricos para que todas las features tengan magnitudes comparables. Incluye StandardScaler (z-score), MinMaxScaler y RobustScaler.
**Usado en:** `telemetria_vehicular/phase4/01_feature_engineering.ipynb`, `telemetria_vehicular/phase5/01_customer_segmentation.ipynb`
**Referencia:** [sklearn.preprocessing (scaling)](https://scikit-learn.org/stable/modules/preprocessing.html#standardization-or-mean-removal-and-variance-scaling)

### Feature Engineering - Features Temporales

**Definición:** Creación de variables derivadas del tiempo: hora del día, día de la semana, mes, es_fin_de_semana, es_hora_pico, variables cíclicas (sin/cos).
**Usado en:** `telemetria_vehicular/phase4/01_feature_engineering.ipynb`, `nyc_taxi/phase4/` *(pendiente)*

### Feature Engineering - Features Geográficas

**Definición:** Creación de variables basadas en coordenadas: distancia haversine, zona geográfica, densidad de puntos, distancia a puntos de referencia.
**Usado en:** `telemetria_vehicular/phase4/01_feature_engineering.ipynb`, `nyc_taxi/phase4/` *(pendiente)*

### Regresión Lineal (Linear Regression)

**Definición:** Modelo que ajusta una relación lineal entre features y variable objetivo minimizando la suma de errores cuadráticos (OLS).
**Usado en:** `telemetria_vehicular/phase4/02_regression_fuel_consumption.ipynb`, `nyc_taxi/phase4/` *(pendiente)*
**Referencia:** [sklearn.linear_model.LinearRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html)

### Regresión Ridge

**Definición:** Regresión lineal con regularización L2 que penaliza coeficientes grandes, reduciendo sobreajuste y manejando multicolinealidad.
**Usado en:** `telemetria_vehicular/phase4/02_regression_fuel_consumption.ipynb`
**Referencia:** [sklearn.linear_model.Ridge](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html)

### Regresión Lasso

**Definición:** Regresión lineal con regularización L1 que puede llevar coeficientes exactamente a cero, realizando selección automática de features.
**Usado en:** `telemetria_vehicular/phase4/02_regression_fuel_consumption.ipynb`
**Referencia:** [sklearn.linear_model.Lasso](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html)

### Random Forest (Regresión y Clasificación)

**Definición:** Ensamble de árboles de decisión entrenados con subconjuntos aleatorios de datos y features (bagging). Robusto, pocas hipótesis, captura no-linealidades.
**Usado en:** `telemetria_vehicular/phase4/02_regression_fuel_consumption.ipynb`, `telemetria_vehicular/phase4/04_classification_driver_risk.ipynb`, `nyc_taxi/phase4/` *(pendiente)*
**Referencia:** [sklearn.ensemble.RandomForestRegressor](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html)

### XGBoost (Regresión y Clasificación)

**Definición:** Algoritmo de boosting por gradiente con árboles, altamente optimizado. Construye árboles secuencialmente, cada uno corrigiendo los errores del anterior.
**Usado en:** `telemetria_vehicular/phase4/02_regression_fuel_consumption.ipynb`, `telemetria_vehicular/phase4/04_classification_driver_risk.ipynb`, `nyc_taxi/phase4/` *(pendiente)*
**Referencia:** [XGBoost Documentation](https://xgboost.readthedocs.io/en/latest/)

### Regresión Logística (Logistic Regression)

**Definición:** Modelo lineal para clasificación que estima probabilidades mediante la función logística (sigmoide). Interpretable y eficiente como baseline.
**Usado en:** `telemetria_vehicular/phase4/04_classification_driver_risk.ipynb`, `telemetria_vehicular/phase4/05_classification_churn_risk.ipynb`
**Referencia:** [sklearn.linear_model.LogisticRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html)

### Evaluación de Regresión - R²

**Definición:** Coeficiente de determinación que indica la proporción de varianza de la variable objetivo explicada por el modelo. Rango (-inf, 1], donde 1 es ajuste perfecto.
**Usado en:** `telemetria_vehicular/phase4/02_regression_fuel_consumption.ipynb`, `telemetria_vehicular/phase4/03_regression_satisfaction.ipynb`
**Referencia:** [sklearn.metrics.r2_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.r2_score.html)

### Evaluación de Regresión - MAE (Mean Absolute Error)

**Definición:** Promedio de los valores absolutos de los errores. Interpretable en las mismas unidades que la variable objetivo, menos sensible a outliers que RMSE.
**Usado en:** `telemetria_vehicular/phase4/02_regression_fuel_consumption.ipynb`, `telemetria_vehicular/phase5/04_time_series_forecasting.ipynb`
**Referencia:** [sklearn.metrics.mean_absolute_error](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.mean_absolute_error.html)

### Evaluación de Regresión - RMSE (Root Mean Squared Error)

**Definición:** Raíz cuadrada del promedio de los errores al cuadrado. Penaliza más los errores grandes que MAE.
**Usado en:** `telemetria_vehicular/phase4/02_regression_fuel_consumption.ipynb`, `telemetria_vehicular/phase5/04_time_series_forecasting.ipynb`
**Referencia:** [sklearn.metrics.root_mean_squared_error](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.root_mean_squared_error.html)

### Evaluación de Clasificación - Accuracy

**Definición:** Proporción de predicciones correctas sobre el total. Simple pero engañosa con clases desbalanceadas.
**Usado en:** `telemetria_vehicular/phase4/04_classification_driver_risk.ipynb`, `telemetria_vehicular/phase4/05_classification_churn_risk.ipynb`
**Referencia:** [sklearn.metrics.accuracy_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.accuracy_score.html)

### Evaluación de Clasificación - Precision

**Definición:** De todas las predicciones positivas, proporción que realmente son positivas. Importante cuando el costo de falsos positivos es alto.
**Usado en:** `telemetria_vehicular/phase4/04_classification_driver_risk.ipynb`, `telemetria_vehicular/phase4/05_classification_churn_risk.ipynb`
**Referencia:** [sklearn.metrics.precision_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_score.html)

### Evaluación de Clasificación - Recall (Sensibilidad)

**Definición:** De todos los positivos reales, proporción que el modelo identificó correctamente. Importante cuando el costo de falsos negativos es alto.
**Usado en:** `telemetria_vehicular/phase4/04_classification_driver_risk.ipynb`, `telemetria_vehicular/phase4/05_classification_churn_risk.ipynb`
**Referencia:** [sklearn.metrics.recall_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.recall_score.html)

### Evaluación de Clasificación - F1 Score

**Definición:** Media armónica de precision y recall. Métrica balanceada útil cuando ambos tipos de error importan y las clases están desbalanceadas.
**Usado en:** `telemetria_vehicular/phase4/04_classification_driver_risk.ipynb`, `telemetria_vehicular/phase4/05_classification_churn_risk.ipynb`
**Referencia:** [sklearn.metrics.f1_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.f1_score.html)

### Evaluación de Clasificación - ROC-AUC

**Definición:** Área bajo la curva ROC (Receiver Operating Characteristic). Mide la capacidad del modelo de discriminar entre clases a través de todos los umbrales posibles. Rango [0.5, 1].
**Usado en:** `telemetria_vehicular/phase4/04_classification_driver_risk.ipynb`, `telemetria_vehicular/phase4/05_classification_churn_risk.ipynb`
**Referencia:** [sklearn.metrics.roc_auc_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html)

### Validación Cruzada - KFold

**Definición:** Técnica que divide los datos en K particiones (folds), entrena en K-1 y evalúa en el restante, rotando K veces para obtener una estimación robusta del rendimiento.
**Usado en:** `telemetria_vehicular/phase4/02_regression_fuel_consumption.ipynb`, `telemetria_vehicular/phase4/04_classification_driver_risk.ipynb`
**Referencia:** [sklearn.model_selection.KFold](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.KFold.html)

### Validación Cruzada - GridSearchCV

**Definición:** Búsqueda exhaustiva de la mejor combinación de hiperparámetros evaluando todas las posibles mediante validación cruzada.
**Usado en:** `telemetria_vehicular/phase4/02_regression_fuel_consumption.ipynb`, `telemetria_vehicular/phase4/04_classification_driver_risk.ipynb`
**Referencia:** [sklearn.model_selection.GridSearchCV](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html)

### Interpretabilidad - Permutation Importance

**Definición:** Medida de importancia de features basada en cuánto se degrada el rendimiento del modelo al permutar aleatoriamente los valores de cada feature.
**Usado en:** `telemetria_vehicular/phase4/06_model_interpretation.ipynb`
**Referencia:** [sklearn.inspection.permutation_importance](https://scikit-learn.org/stable/modules/generated/sklearn.inspection.permutation_importance.html)

### Interpretabilidad - Partial Dependence Plots (PDP)

**Definición:** Gráficos que muestran el efecto marginal de una o dos features sobre la predicción del modelo, promediando sobre las demás features.
**Usado en:** `telemetria_vehicular/phase4/06_model_interpretation.ipynb`
**Referencia:** [sklearn.inspection.PartialDependenceDisplay](https://scikit-learn.org/stable/modules/generated/sklearn.inspection.PartialDependenceDisplay.html)

### Interpretabilidad - Feature Importance (basada en árboles)

**Definición:** Importancia calculada por modelos de árboles (Random Forest, XGBoost) basándose en cuánto reduce cada feature la impureza (Gini/entropía) en los nodos de decisión.
**Usado en:** `telemetria_vehicular/phase4/06_model_interpretation.ipynb`
**Referencia:** [Feature Importance](https://scikit-learn.org/stable/auto_examples/ensemble/plot_forest_importances.html)

---

## 5. Machine Learning No Supervisado

### K-Means Clustering

**Definición:** Algoritmo de partición que agrupa datos en K clusters minimizando la distancia intra-cluster. Requiere especificar K y asume clusters esféricos de tamaño similar.
**Usado en:** `telemetria_vehicular/phase5/01_customer_segmentation.ipynb`, `telemetria_vehicular/phase5/02_driving_pattern_clustering.ipynb`
**Referencia:** [sklearn.cluster.KMeans](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html)

### DBSCAN Clustering

**Definición:** Algoritmo basado en densidad que identifica clusters de forma arbitraria y detecta outliers como puntos de ruido. No requiere especificar K.
**Usado en:** `telemetria_vehicular/phase5/02_driving_pattern_clustering.ipynb`
**Referencia:** [sklearn.cluster.DBSCAN](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html)

### Elbow Method (Método del Codo)

**Definición:** Técnica para seleccionar el número óptimo de clusters graficando la inercia (suma de distancias intra-cluster) vs K, buscando el "codo" donde la mejora marginal decrece.
**Usado en:** `telemetria_vehicular/phase5/01_customer_segmentation.ipynb`, `telemetria_vehicular/phase5/02_driving_pattern_clustering.ipynb`

### Silhouette Score

**Definición:** Métrica de calidad de clustering que mide cuán similar es cada punto a su propio cluster vs el cluster más cercano. Rango [-1, 1], donde valores altos indican clusters bien separados.
**Usado en:** `telemetria_vehicular/phase5/01_customer_segmentation.ipynb`, `telemetria_vehicular/phase5/02_driving_pattern_clustering.ipynb`
**Referencia:** [sklearn.metrics.silhouette_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html)

### PCA (Principal Component Analysis)

**Definición:** Técnica de reducción de dimensionalidad lineal que transforma las features originales en componentes principales ortogonales ordenados por varianza explicada.
**Usado en:** `telemetria_vehicular/phase5/01_customer_segmentation.ipynb`, `telemetria_vehicular/phase5/02_driving_pattern_clustering.ipynb`
**Referencia:** [sklearn.decomposition.PCA](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html)

### t-SNE (t-distributed Stochastic Neighbor Embedding)

**Definición:** Técnica de reducción de dimensionalidad no lineal optimizada para visualización en 2D/3D, preserva estructura local de los datos pero no distancias globales.
**Usado en:** `telemetria_vehicular/phase5/01_customer_segmentation.ipynb`
**Referencia:** [sklearn.manifold.TSNE](https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html)

### Perfilado de Clusters - Radar Charts

**Definición:** Gráficos de radar (spider plots) donde cada eje representa una feature, permitiendo comparar visualmente los perfiles promedio de cada cluster.
**Usado en:** `telemetria_vehicular/phase5/01_customer_segmentation.ipynb`, `telemetria_vehicular/phase5/02_driving_pattern_clustering.ipynb`

### Perfilado de Clusters - Tablas de Estadísticas por Cluster

**Definición:** Resumen tabular con media, mediana y conteo de cada feature por cluster, complementado con tests estadísticos para validar diferencias significativas entre grupos.
**Usado en:** `telemetria_vehicular/phase5/01_customer_segmentation.ipynb`, `telemetria_vehicular/phase5/02_driving_pattern_clustering.ipynb`

---

## 6. Series Temporales

### Descomposición de Series Temporales

**Definición:** Separación de una serie temporal en sus componentes: tendencia (trend), estacionalidad (seasonal) y residuo (residual). Puede ser aditiva (Y = T + S + R) o multiplicativa (Y = T * S * R).
**Usado en:** `telemetria_vehicular/phase5/03_time_series_decomposition.ipynb`, `nyc_taxi/phase5/` *(pendiente)*
**Referencia:** [statsmodels.tsa.seasonal.seasonal_decompose](https://www.statsmodels.org/stable/generated/statsmodels.tsa.seasonal.seasonal_decompose.html)

### Estacionariedad - ADF Test (Augmented Dickey-Fuller)

**Definición:** Prueba estadística para determinar si una serie temporal tiene raíz unitaria (no estacionaria). Una serie estacionaria tiene media y varianza constantes en el tiempo.
**Usado en:** `telemetria_vehicular/phase5/03_time_series_decomposition.ipynb`, `telemetria_vehicular/phase5/04_time_series_forecasting.ipynb`
**Referencia:** [statsmodels.tsa.stattools.adfuller](https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.adfuller.html)

### Diferenciación

**Definición:** Transformación que resta a cada observación el valor anterior (o estacional) para hacer una serie estacionaria. La diferenciación de orden d se indica como I(d) en ARIMA.
**Usado en:** `telemetria_vehicular/phase5/04_time_series_forecasting.ipynb`

### ARIMA (AutoRegressive Integrated Moving Average)

**Definición:** Modelo de serie temporal que combina componentes autorregresivos (AR), de integración/diferenciación (I) y de media móvil (MA), parametrizado como ARIMA(p, d, q).
**Usado en:** `telemetria_vehicular/phase5/04_time_series_forecasting.ipynb`
**Referencia:** [statsmodels.tsa.arima.model.ARIMA](https://www.statsmodels.org/stable/generated/statsmodels.tsa.arima.model.ARIMA.html)

### SARIMA (Seasonal ARIMA)

**Definición:** Extensión de ARIMA que incluye componentes estacionales, parametrizado como SARIMA(p, d, q)(P, D, Q, s) donde s es el período estacional.
**Usado en:** `telemetria_vehicular/phase5/04_time_series_forecasting.ipynb`, `nyc_taxi/phase5/` *(pendiente)*
**Referencia:** [statsmodels.tsa.statespace.sarimax.SARIMAX](https://www.statsmodels.org/stable/generated/statsmodels.tsa.statespace.sarimax.SARIMAX.html)

### Prophet

**Definición:** Modelo de series temporales desarrollado por Meta que descompone la serie en tendencia, estacionalidad y efectos de días festivos. Robusto ante datos faltantes y cambios de tendencia.
**Usado en:** `telemetria_vehicular/phase5/04_time_series_forecasting.ipynb`, `nyc_taxi/phase5/` *(pendiente)*
**Referencia:** [Prophet Documentation](https://facebook.github.io/prophet/)

### Evaluación de Series Temporales - MAPE

**Definición:** Error porcentual absoluto medio (Mean Absolute Percentage Error). Expresa el error como porcentaje del valor real, facilitando interpretación independiente de la escala.
**Usado en:** `telemetria_vehicular/phase5/04_time_series_forecasting.ipynb`
**Referencia:** [sklearn.metrics.mean_absolute_percentage_error](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.mean_absolute_percentage_error.html)

### Evaluación de Series Temporales - Análisis de Residuos

**Definición:** Diagnóstico del modelo verificando que los residuos sean ruido blanco: distribución normal, sin autocorrelación, media cero y varianza constante.
**Usado en:** `telemetria_vehicular/phase5/04_time_series_forecasting.ipynb`

---

## 7. Detección de Anomalías

### Método IQR (Rango Intercuartil)

**Definición:** Detección de outliers definiendo límites como Q1 - 1.5*IQR y Q3 + 1.5*IQR, donde IQR = Q3 - Q1. Valores fuera de estos límites se consideran atípicos.
**Usado en:** `telemetria_vehicular/phase2/01_univariate_telemetry.ipynb`, `telemetria_vehicular/phase5/05_anomaly_detection.ipynb`

### Método Z-Score

**Definición:** Identificación de anomalías basándose en la distancia en desviaciones estándar respecto a la media. Típicamente se usa un umbral de |z| > 3.
**Usado en:** `telemetria_vehicular/phase5/05_anomaly_detection.ipynb`
**Referencia:** [scipy.stats.zscore](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.zscore.html)

### Isolation Forest

**Definición:** Algoritmo de ML que detecta anomalías aislando observaciones mediante particiones aleatorias. Las anomalías requieren menos particiones para ser aisladas (caminos más cortos en el árbol).
**Usado en:** `telemetria_vehicular/phase5/05_anomaly_detection.ipynb`
**Referencia:** [sklearn.ensemble.IsolationForest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html)

### Contextualización de Anomalías

**Definición:** Análisis que correlaciona anomalías detectadas con eventos externos reales (clima extremo, días festivos, incidentes) para determinar si son errores de datos o eventos legítimos.
**Usado en:** `telemetria_vehicular/phase5/05_anomaly_detection.ipynb`, `telemetria_vehicular/phase5/06_predictive_maintenance.ipynb`

---

## 8. MLOps e Infraestructura

### Apache Kafka - Conceptos Generales

**Definición:** Plataforma de streaming distribuida para publicar, suscribir, almacenar y procesar flujos de eventos en tiempo real con alta disponibilidad y durabilidad.
**Usado en:** `telemetria_vehicular/phase6/03_pipeline_documentation.ipynb`
**Referencia:** [Apache Kafka Documentation](https://kafka.apache.org/documentation/)

### Kafka - Producers y Consumers

**Definición:** Producers publican mensajes en topics. Consumers se suscriben a topics y procesan mensajes, organizados en consumer groups para paralelismo.
**Usado en:** `telemetria_vehicular/phase6/03_pipeline_documentation.ipynb`

### Kafka - Topics y Partitions

**Definición:** Topics son categorías lógicas donde se publican mensajes. Cada topic se divide en partitions para distribución paralela, cada partición mantiene orden de llegada.
**Usado en:** `telemetria_vehicular/phase6/03_pipeline_documentation.ipynb`

### Apache Airflow - DAGs

**Definición:** Directed Acyclic Graphs que definen flujos de trabajo como grafos de tareas con dependencias, permitiendo orquestación, programación y monitoreo de pipelines de datos.
**Usado en:** `telemetria_vehicular/phase6/03_pipeline_documentation.ipynb`
**Referencia:** [Apache Airflow Documentation](https://airflow.apache.org/docs/)

### Airflow - Tasks y Schedules

**Definición:** Tasks son unidades de trabajo individuales dentro de un DAG (PythonOperator, BashOperator, etc.). Schedules definen la frecuencia de ejecución (cron expressions).
**Usado en:** `telemetria_vehicular/phase6/03_pipeline_documentation.ipynb`

### Prometheus

**Definición:** Sistema de monitoreo y alerta de código abierto que recolecta métricas como series temporales, con modelo de datos multidimensional y lenguaje de consultas PromQL.
**Usado en:** `telemetria_vehicular/phase6/03_pipeline_documentation.ipynb`
**Referencia:** [Prometheus Documentation](https://prometheus.io/docs/)

### Grafana

**Definición:** Plataforma de visualización y dashboarding que se conecta a múltiples fuentes de datos (Prometheus, Loki, etc.) para crear paneles de monitoreo en tiempo real.
**Usado en:** `telemetria_vehicular/phase6/03_pipeline_documentation.ipynb`
**Referencia:** [Grafana Documentation](https://grafana.com/docs/)

### Loki

**Definición:** Sistema de agregación de logs inspirado en Prometheus, diseñado para ser eficiente en costos indexando solo metadatos (labels) en lugar del contenido completo de los logs.
**Usado en:** `telemetria_vehicular/phase6/03_pipeline_documentation.ipynb`
**Referencia:** [Grafana Loki](https://grafana.com/docs/loki/latest/)

### Alertas de Monitoreo

**Definición:** Reglas configuradas en Prometheus/Grafana que disparan notificaciones cuando métricas cruzan umbrales definidos (latencia alta, errores frecuentes, recursos agotados).
**Usado en:** `telemetria_vehicular/phase6/03_pipeline_documentation.ipynb`

### Docker

**Definición:** Plataforma de contenedores que empaqueta aplicaciones con todas sus dependencias en unidades aisladas y reproducibles, garantizando que funcionen igual en cualquier entorno.
**Usado en:** `telemetria_vehicular/phase6/03_pipeline_documentation.ipynb`
**Referencia:** [Docker Documentation](https://docs.docker.com/)

### Docker Compose

**Definición:** Herramienta para definir y ejecutar aplicaciones multi-contenedor mediante un archivo YAML, orquestando servicios, redes y volúmenes localmente.
**Usado en:** `telemetria_vehicular/phase6/03_pipeline_documentation.ipynb`
**Referencia:** [Docker Compose](https://docs.docker.com/compose/)

### Multi-stage Builds

**Definición:** Técnica de Docker que usa múltiples etapas FROM en un Dockerfile para separar compilación de runtime, produciendo imágenes finales más pequeñas y seguras.
**Usado en:** `telemetria_vehicular/phase6/03_pipeline_documentation.ipynb`
**Referencia:** [Multi-stage builds](https://docs.docker.com/build/building/multi-stage/)

### GitHub Actions - CI/CD

**Definición:** Plataforma de automatización de GitHub que ejecuta workflows definidos en YAML ante eventos (push, PR), para testing, linting y despliegue automático.
**Usado en:** `telemetria_vehicular/phase6/03_pipeline_documentation.ipynb`
**Referencia:** [GitHub Actions](https://docs.github.com/en/actions)

### Google BigQuery

**Definición:** Data warehouse serverless de Google Cloud para análisis SQL a escala de petabytes, con modelo de precios por bytes procesados y almacenamiento columnar.
**Usado en:** `nyc_taxi/phase1/02_pandas_nyc_taxi.ipynb`, todos los notebooks de `nyc_taxi/`
**Referencia:** [BigQuery Documentation](https://cloud.google.com/bigquery/docs)

### Google Cloud Storage

**Definición:** Servicio de almacenamiento de objetos para datos no estructurados, con clases de almacenamiento (Standard, Nearline, Coldline, Archive) y control de acceso granular.
**Usado en:** `telemetria_vehicular/phase6/03_pipeline_documentation.ipynb`
**Referencia:** [Cloud Storage](https://cloud.google.com/storage/docs)

### Google Cloud Functions

**Definición:** Servicio serverless de funciones evento-driven que ejecuta código en respuesta a eventos de Cloud sin gestionar infraestructura.
**Usado en:** `telemetria_vehicular/phase6/03_pipeline_documentation.ipynb`
**Referencia:** [Cloud Functions](https://cloud.google.com/functions/docs)

### Vertex AI

**Definición:** Plataforma unificada de Google Cloud para MLOps que abarca desde entrenamiento hasta despliegue y monitoreo de modelos en producción.
**Usado en:** `telemetria_vehicular/phase6/03_pipeline_documentation.ipynb`
**Referencia:** [Vertex AI](https://cloud.google.com/vertex-ai/docs)

### Dataproc

**Definición:** Servicio administrado de Google Cloud para ejecutar clusters de Apache Spark y Hadoop, con autoescalado y integración nativa con otros servicios de GCP.
**Usado en:** `telemetria_vehicular/phase6/03_pipeline_documentation.ipynb`
**Referencia:** [Dataproc](https://cloud.google.com/dataproc/docs)

---

## 9. DevOps y Buenas Prácticas

### Git - Branching

**Definición:** Estrategia de ramificación para desarrollo paralelo. Las ramas permiten trabajar en features, fixes o experimentos sin afectar la rama principal.
**Usado en:** Aplicado en todo el proyecto
**Referencia:** [Git Branching](https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell)

### Git - Commits

**Definición:** Instantáneas del estado del proyecto con mensajes descriptivos. Buenas prácticas: mensajes concisos en imperativo, commits atómicos y frecuentes.
**Usado en:** Aplicado en todo el proyecto
**Referencia:** [Git Basics](https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository)

### Git - .gitignore

**Definición:** Archivo que especifica patrones de archivos y directorios que Git debe ignorar (datos grandes, credenciales, entornos virtuales, checkpoints).
**Usado en:** Aplicado en todo el proyecto
**Referencia:** [gitignore](https://git-scm.com/docs/gitignore)

### Entornos Virtuales (venv)

**Definición:** Entornos Python aislados que evitan conflictos de dependencias entre proyectos. Cada proyecto mantiene sus propias versiones de paquetes.
**Usado en:** Aplicado en todo el proyecto
**Referencia:** [venv](https://docs.python.org/3/library/venv.html)

### requirements.txt

**Definición:** Archivo que lista las dependencias del proyecto con versiones fijadas (`pip freeze`), permitiendo reproducir el entorno exacto en cualquier máquina.
**Usado en:** `requirements.txt` (raíz del proyecto)
**Referencia:** [pip requirements files](https://pip.pypa.io/en/stable/reference/requirements-file-format/)

### Testing - pytest

**Definición:** Framework de testing para Python con descubrimiento automático de tests, fixtures, parametrización y plugins. Sintaxis simple con `assert`.
**Usado en:** `tests/`
**Referencia:** [pytest Documentation](https://docs.pytest.org/)

### Testing - unittest

**Definición:** Framework de testing incluido en la biblioteca estándar de Python, basado en clases. Útil como base pero menos flexible que pytest.
**Usado en:** `tests/`
**Referencia:** [unittest](https://docs.python.org/3/library/unittest.html)

### Documentación - Docstrings

**Definición:** Cadenas de documentación embebidas en funciones, clases y módulos Python, accesibles programáticamente. Convenciones: Google style, NumPy style o reStructuredText.
**Usado en:** `src/`
**Referencia:** [PEP 257](https://peps.python.org/pep-0257/)

### Documentación - README

**Definición:** Archivo principal de documentación del proyecto que describe propósito, instalación, uso y estructura. Primera impresión para cualquier visitante del repositorio.
**Usado en:** Raíz del proyecto

### Documentación - Concept Index

**Definición:** Índice comprensivo de conceptos técnicos aplicados en el proyecto, con definiciones, referencias a notebooks y enlaces a documentación oficial. Sirve como guía de repaso y referencia rápida.
**Usado en:** `docs/concept_index.md` (este archivo)
