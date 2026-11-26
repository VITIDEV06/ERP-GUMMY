# Datos de origen (`data/raw/`)

Esta carpeta contiene los CSV que sirven de guía para crear y poblar la base de datos de GUMMY ERP. Aquí se explica de dónde salen, cómo se filtraron y qué cambios se les hicieron.

---

## 1. Origen: dataset de Olist en Kaggle

Los datos provienen del dataset público **Brazilian E-Commerce Public Dataset by Olist**:

> https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

Olist es un marketplace brasileño. El dataset tiene unos 100 000 pedidos reales y anonimizados de 2016 a 2018, repartidos en varias tablas. Para este proyecto se usaron seis de ellas y la tabla de traducción de categorías:

| Archivo original de Kaggle | Filas originales | Contenido |
|:---|---:|:---|
| `olist_orders_dataset.csv` | 99 441 | Pedidos: cliente, estado y fechas |
| `olist_order_items_dataset.csv` | 112 650 | Ítems de cada pedido: producto, vendedor, precio y flete |
| `olist_order_payments_dataset.csv` | 103 886 | Pagos de cada pedido |
| `olist_customers_dataset.csv` | 99 441 | Clientes y su ubicación |
| `olist_products_dataset.csv` | 32 951 | Productos: categoría y medidas |
| `olist_sellers_dataset.csv` | 3 095 | Vendedores y su ubicación |
| `product_category_name_translation.csv` | 71 | Nombre de cada categoría en portugués y en inglés |

---

## 2. Relaciones entre las tablas

<p align="center">
  <img src="../../assets/Database%20Relationships%20with%20Added%20Order%20Link.png" alt="Relaciones entre las tablas de la base de datos" width="85%">
</p>

- `venta` se une con `cliente` por `customer_id`.
- `venta`, `compra` y `compra_movimiento` comparten `order_id`.
- `compra` se une con `producto` por `product_id` y con `vendedor` por `seller_id`.

`compra` (los ítems de cada pedido) es la tabla central: es la única que conecta pedidos, productos y vendedores.

---

## 3. Filtrado: `analysis_filtering_scripts.ipynb`

El dataset completo es demasiado grande para un proyecto académico. El notebook [`analysis_filtering_scripts.ipynb`](analysis_filtering_scripts.ipynb) explora los datos y luego conserva solo un subconjunto pequeño y coherente.

### 3.1 Exploración (celdas 1 a 13)

| Celda | Código | Lógica y decisión |
|:---:|:---|:---|
| 1 | `import pandas as pd`<br>`import matplotlib.pyplot as plt` | Carga las librerías de análisis. `matplotlib` se importa pero no se llega a usar. |
| 2 | `pd.read_csv("olist_orders_dataset.csv")` | Carga la tabla de pedidos, que es el punto de partida del análisis. |
| 3–5 | `.head()`, `.describe()`, `.shape` | Primer vistazo: 99 441 pedidos y 8 columnas. `describe()` muestra que `order_id` y `customer_id` son únicos (99 441 valores distintos cada uno), que hay 8 estados de pedido y que algunas fechas están vacías (por ejemplo, `order_approved_at` tiene 99 281 valores). |
| 6–8 | `olo_customers = pd.read_csv(...)`<br>`olo_customers['customer_id'].value_counts()` | Carga los clientes y cuenta cuántas veces aparece cada `customer_id`. Todos aparecen **una sola vez**. |
| 9 | `olist_orders_dataset['order_id'].value_counts()` | Lo mismo con los pedidos: cada `order_id` aparece una vez. **Conclusión:** en Olist cada pedido tiene su propio `customer_id`, así que la relación pedido–cliente es 1 a 1. |
| 10–12 | `olo_items = pd.read_csv(...)`<br>`olo_items['order_id'].value_counts()` | Carga los ítems y cuenta cuántos ítems tiene cada pedido. Aquí sí hay repeticiones: el pedido más grande tiene 21 ítems. Esta cantidad es la que se usa después para filtrar. |
| 13 | `same_orders = olist_orders_dataset.loc[...isin(olo_items['order_id'])]`<br>`same_orders['frequency_in_items'] = ...map(...value_counts())` | Se queda con los pedidos que tienen al menos un ítem y les agrega la columna **`frequency_in_items`**: el número de ítems del pedido. Luego los ordena por esa columna. |
| 14 | `same_orders['frequency_in_items'].value_counts()` | Muestra cuántos pedidos hay por cada cantidad de ítems. 88 863 pedidos tienen **un solo** ítem y solo **36** tienen más de 7. Esta tabla es la base de la decisión de filtrado. |

**Por qué se filtra por número de ítems:** los pedidos con muchos ítems son los más interesantes para un ERP, porque mezclan varios productos y vendedores en un mismo pedido y ejercitan todas las relaciones del diagrama. Además, quedarse con los que tienen **más de 7** ítems deja solo 36 pedidos: un volumen manejable para desarrollar y probar.

### 3.2 Pipeline de filtrado (celda 15)

La celda 15 es un script completo que genera los CSV reducidos. Paso a paso:

**Configuración**

```python
INPUT_DIR = Path(".")
OUTPUT_DIR = Path("CLEAN")
MIN_FREQUENCY = 7
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
```
- Lee los CSV de la carpeta actual y escribe el resultado en `CLEAN/`, para no sobrescribir los originales.
- `MIN_FREQUENCY = 7` es el umbral elegido en la exploración.
- `mkdir(..., exist_ok=True)` crea `CLEAN/` si no existe y no falla si ya existe.

**Carga:** lee las seis tablas originales (`orders`, `items`, `payments`, `customers`, `products`, `sellers`).

**Paso 1. Filtrar pedidos por frecuencia**

```python
frequency = items["order_id"].value_counts()
valid_order_ids = frequency[frequency > MIN_FREQUENCY].index
filtered_orders = orders.loc[orders["order_id"].isin(valid_order_ids)].copy()
filtered_orders["frequency_in_items"] = filtered_orders["order_id"].map(frequency)
```
- Cuenta los ítems de cada pedido.
- Se queda con los `order_id` que tienen **más de 7** ítems (es decir, 8 o más; la comparación es `>`, no `>=`).
- Filtra la tabla de pedidos con esos `order_id`. El `.copy()` evita que pandas trate el resultado como una vista de la tabla original y avise con `SettingWithCopyWarning` al agregar columnas.
- Agrega `frequency_in_items` a cada pedido.

**Paso 2. Filtrar ítems, pagos y clientes**

```python
filtered_items = items.loc[items["order_id"].isin(filtered_orders["order_id"])].copy()
filtered_payments = payments.loc[payments["order_id"].isin(filtered_orders["order_id"])].copy()
filtered_customers = customers.loc[customers["customer_id"].isin(filtered_orders["customer_id"])].copy()
```
- Conserva solo los ítems y pagos de los pedidos elegidos (unión por `order_id`).
- Conserva solo los clientes de esos pedidos (unión por `customer_id`).

**Paso 3. Filtrar productos**

```python
filtered_products = products.loc[products["product_id"].isin(filtered_items["product_id"])].copy()
```
- Conserva los productos que aparecen en los ítems **ya filtrados**. Por eso este paso va después del paso 2: los productos dependen de los ítems, no de los pedidos.

**Paso 4. Filtrar vendedores**

```python
filtered_sellers = sellers.loc[sellers["seller_id"].isin(filtered_items["seller_id"])].copy()
```
- Igual que el paso 3, pero con `seller_id`.

**Paso 5. Exportar**

```python
for filename, dataframe in datasets.items():
    dataframe.to_csv(OUTPUT_DIR / filename, index=False)
```
- Guarda cada tabla filtrada con su nombre original dentro de `CLEAN/`. `index=False` evita escribir el índice de pandas como una columna extra.

**Resultado de la ejecución**

| Tabla | Filas conservadas |
|:---|---:|
| Pedidos | 36 |
| Ítems | 407 |
| Pagos | 36 |
| Clientes | 36 |
| Productos | 71 |
| Vendedores | 32 |

Como cada paso filtra a partir del anterior, **todas las referencias se conservan**: cada ítem apunta a un pedido, producto y vendedor que existen en las tablas filtradas, y lo mismo pasa con pagos y clientes.

### 3.3 Verificación (celdas 16 y 17)

```python
ol_it = pd.read_csv("./CLEAN/olist_order_items_dataset.csv")
ol_it.order_id.value_counts()
```
Vuelve a leer los ítems exportados y cuenta los ítems por pedido. Todos los pedidos tienen entre 8 y 21 ítems, lo que confirma que el filtro funcionó.

> [!NOTE]
> El notebook lee los archivos con su nombre original de Kaggle (`olist_*.csv`). Esos archivos ya no están en esta carpeta: después del filtrado se renombraron (ver sección 4). Para volver a ejecutarlo hay que descargar los originales de Kaggle y colocarlos junto al notebook.

---

## 4. Cambios hechos sobre los CSV filtrados

### 4.1 Renombrado

Los archivos generados en `CLEAN/` se movieron a esta carpeta y se renombraron al español, siguiendo los nombres de las tablas del ERP. El contenido y el orden de las filas no cambiaron.

| Archivo original de Kaggle | Archivo en `data/raw/` | Filas |
|:---|:---|---:|
| `olist_orders_dataset.csv` | `venta.csv` | 36 |
| `olist_order_items_dataset.csv` | `compra.csv` | 407 |
| `olist_order_payments_dataset.csv` | `compra_movimiento.csv` | 36 |
| `olist_customers_dataset.csv` | `clientes.csv` | 36 |
| `olist_products_dataset.csv` | `producto.csv` | 71 |
| `olist_sellers_dataset.csv` | `vendedor.csv` | 32 |
| `product_category_name_translation.csv` | (sin cambios) | 71 |

### 4.2 Columnas agregadas

**`venta.csv`: `frequency_in_items`** (agregada por el notebook)
Número de ítems del pedido en `compra.csv`. Va de 8 a 21.

**`venta.csv`: `product_id`**
Producto vendido en el pedido. Se obtiene buscando el `order_id` de la venta en `compra.csv`.
- **Decisión:** 19 de los 36 pedidos incluyen más de un producto, pero `venta.csv` tiene una sola fila por pedido. Se eligió el producto con **más ítems** dentro del pedido y, si hay empate, el primero que aparece en `compra.csv`.

**`venta.csv`: `quantity`**
Cantidad de unidades vendidas. Es un número entero **aleatorio** entre 1 y el `order_item_id` máximo del pedido en `compra.csv` **menos 1**, así que siempre es estrictamente menor que ese máximo. Por ejemplo, si un pedido llega hasta el ítem 8, la cantidad va de 1 a 7.
- Se generó con una semilla fija (`numpy.random.default_rng(42)`) para que el resultado sea reproducible.
- **Ojo:** es un dato **simulado**, no viene del dataset de Olist.

**`producto.csv`: `price`**
Precio de venta del producto: el precio que tiene en `compra.csv` **aumentado un 20 %** y redondeado a 2 decimales. Por ejemplo, 1680.0 pasa a 2016.0.
- **Decisión:** 2 productos tienen más de un precio en `compra.csv`. Se usó el precio que **más se repite**:

| `product_id` | Precios en `compra.csv` | Precio usado | `price` |
|:---|:---|---:|---:|
| `422879e10f46682990de24d770e7f83d` | 59.0 (14 veces), 59.9 (2 veces) | 59.0 | 70.80 |
| `53759a2ecddad2bb87a079a1f1519f73` | 53.9 (5 veces), 59.9 (2 veces) | 53.9 | 64.68 |

Las columnas que ya existían no se modificaron.

### 4.3 Columnas que los modelos no usan

Los modelos de la base de datos ([`models/`](../../models/)) no incluyen todas las columnas de los CSV:

| CSV | Columna | Motivo |
|:---|:---|:---|
| `producto.csv` | `product_name_lenght`, `product_description_lenght`, `product_photos_qty` | Descartadas: son metadatos del anuncio en Olist, sin uso en el ERP |
| Todos | `order_id`, `customer_id`, `product_id`, `seller_id` (códigos de 32 caracteres) | Las tablas usan un `id` numérico autoincremental. Al cargar los datos hay que traducir cada código a su `id` nuevo |

---

## 5. Observaciones sobre los datos

- **Códigos postales sin cero inicial:** Olist guardó los códigos postales como números, así que los que empiezan por 0 lo perdieron (`3735` debería ser `03735`). En la base de datos la columna es texto de 5 caracteres; al cargarlos hay que completar con ceros a la izquierda.
- **Producto sin categoría:** un producto de `producto.csv` tiene `product_category_name` vacío. En el modelo esa columna admite `None`.
- **Estado de los pedidos:** los 36 pedidos tienen estado `delivered`.

---

## 6. Pendiente: traducir las categorías al español

Las categorías de `producto.csv` (`product_category_name`) están en **portugués**. El archivo [`product_category_name_translation.csv`](product_category_name_translation.csv) solo las traduce al **inglés** (columna `product_category_name_english`).

**Las categorías de productos deben traducirse al español.** Para ello se puede partir del archivo de traducción y agregarle una columna con el nombre en español. Las 16 categorías que aparecen en `producto.csv` están en ese archivo:

`automotivo`, `bebes`, `bebidas`, `beleza_saude`, `cama_mesa_banho`, `construcao_ferramentas_construcao`, `eletronicos`, `ferramentas_jardim`, `informatica_acessorios`, `moveis_decoracao`, `moveis_escritorio`, `moveis_sala`, `relogios_presentes`, `telefonia`, `telefonia_fixa`, `utilidades_domesticas`.
