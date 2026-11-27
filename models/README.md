# Guía: cómo agregar objetos a la base de datos

Esta guía explica **cómo** se guardan registros en la base de datos de GUMMY ERP con SQLAlchemy. No trae el código resuelto: te da el patrón, un ejemplo de referencia y las preguntas que debes responder para escribir tu propio código.

---

## 1. Antes de empezar

Archivos que vas a usar:

| Archivo | Qué contiene |
|:---|:---|
| [`database.py`](database.py) | El `engine` (conexión a `data/gummy_erp.db`), la clase `Base`, `get_session()` e `init_db()` |
| [`usuario_model.py`](usuario_model.py) | `Usuario` → tabla `user` (rol `administrador` o `vendedor`) |
| [`producto_model.py`](producto_model.py) | `Producto` → tabla `product` |
| [`cliente_model.py`](cliente_model.py) | `Cliente` → tabla `customer` |
| [`venta_model.py`](venta_model.py) | `Venta` → tabla `sale` (encabezado de la venta) |
| [`detalle_venta_model.py`](detalle_venta_model.py) | `DetalleVenta` → tabla `sale_detail` (antes `Compra`: los productos de cada venta) |
| [`movimiento_model.py`](movimiento_model.py) | `MovimientoInventario` → tabla `inventory_movement` (entradas y salidas) |

> El modelo `Vendedor` (tabla `seller` de Olist) se eliminó: ahora "vendedor" es un **rol** de `Usuario`. Los pagos (`CompraMovimiento`) se reemplazaron por los movimientos de inventario, que sí usa el ERP.

Las tablas se crean llamando una vez a `init_db()` desde la raíz del proyecto. Ejecuta tu código **siempre desde la raíz** (`GUMMY-ERP/`), porque los modelos se importan como `models.<archivo>`.

### Cómo se relacionan las tablas

En el código, cada relación es una `ForeignKey`:

| Tabla | Columna | Apunta a |
|:---|:---|:---|
| `Venta` | `cliente_id` | `Cliente.id` (opcional) |
| `Venta` | `usuario_id` | `Usuario.id` |
| `DetalleVenta` | `venta_id` | `Venta.id` |
| `DetalleVenta` | `producto_id` | `Producto.id` |
| `MovimientoInventario` | `producto_id` | `Producto.id` |
| `MovimientoInventario` | `venta_id` | `Venta.id` (solo en salidas por venta) |

Atributos de **relación**: `venta.cliente`, `venta.usuario`, `venta.detalles` (lista), `detalle.venta`, `detalle.producto` y `movimiento.producto`. El diagrama de la base está en el [README principal](../README.md#base-de-datos).

> Ejemplo resuelto en el proyecto: `controllers/venta_controller.py` crea una `Venta`, le agrega varios `DetalleVenta` con `venta.detalles.append(...)` y guarda todo con un solo `commit()`. `services/carga_inicial.py` muestra cómo cargar los CSV de `data/raw/`.

---

## 2. El patrón: crear objetos y guardarlos

Este es el ejemplo de la documentación oficial de SQLAlchemy ([ORM Quick Start](https://docs.sqlalchemy.org/en/20/orm/quickstart.html#create-objects-and-persist)). Usa dos clases de ejemplo, `User` y `Address`, que **no existen** en este proyecto; sirven solo para ver la forma:

```python
from sqlalchemy.orm import Session

with Session(engine) as session:
    spongebob = User(
        name="spongebob",
        fullname="Spongebob Squarepants",
        addresses=[Address(email_address="spongebob@sqlalchemy.org")],
    )
    sandy = User(
        name="sandy",
        fullname="Sandy Cheeks",
        addresses=[
            Address(email_address="sandy@sqlalchemy.org"),
            Address(email_address="sandy@squirrelpower.org"),
        ],
    )
    patrick = User(name="patrick", fullname="Patrick Star")

    session.add_all([spongebob, sandy, patrick])

    session.commit()
```

Lo que hace cada parte:

| Paso | Código | Qué pasa |
|:---|:---|:---|
| 1. Abrir una sesión | `with Session(engine) as session:` | La `Session` usa el `engine` para hablar con la base de datos. El `with` la cierra al terminar. |
| 2. Crear objetos | `User(name=..., fullname=...)` | Cada modelo ya tiene un constructor automático: se le pasan las columnas **por nombre**. El `id` no se pasa: lo asigna la base de datos. |
| 3. Enlazar objetos | `addresses=[Address(...)]` | En lugar de escribir el `id` del otro registro, se le pasa el **objeto**. SQLAlchemy rellena la `ForeignKey` solo. |
| 4. Agregarlos | `session.add_all([...])` | Marca los objetos como pendientes. Todavía **no** están en la base de datos. Para uno solo existe `session.add(obj)`. |
| 5. Confirmar | `session.commit()` | Ejecuta los `INSERT` y confirma la transacción. Si no llamas a `commit()`, no se guarda nada. |

Con `echo=True` en `database.py` (por defecto está en `False`) verás en la consola los `INSERT` que se ejecutan. Fíjate en el orden: primero las filas de `user_account` y después las de `address`, porque `address` necesita el `id` del usuario.

---

## 3. Cómo aplicarlo en GUMMY ERP

En este proyecto no se usa `Session(engine)` directamente: `database.py` ya ofrece `get_session()`, que devuelve una sesión conectada a `data/gummy_erp.db`. El resto del patrón es igual.

Responde estas preguntas antes de escribir código:

**a) ¿Qué columnas pide el modelo?**
Abre el archivo del modelo y lista sus atributos `Mapped[...]`.
- ¿Cuáles son `Optional[...]`? Esas pueden quedar vacías (`None`); las demás son obligatorias.
- ¿Qué tipo pide cada una? Por ejemplo, las fechas de `Venta` y `MovimientoInventario` son `datetime`, no texto. ¿Cómo conviertes `"2017-10-06 15:28:20"` en un `datetime`?

**b) ¿En qué orden se insertan las tablas?**
Mira el diagrama de la sección 1. Una fila no puede apuntar a otra que todavía no existe (las `ForeignKey` están activadas en SQLite).
- ¿Qué tablas no dependen de ninguna otra?
- ¿Cuál necesita que existan `Cliente` y `Producto`?
- ¿Cuáles necesitan que exista `Venta`?

**c) ¿Cómo enlazas un registro con otro?**
Tienes dos caminos; elige uno y úsalo de forma consistente:
- Pasar el **objeto** en el atributo de relación (como `addresses=[...]` en el ejemplo).
- Pasar el **número de `id`** en la columna `ForeignKey`. En ese caso, ¿el `id` ya existe? Un objeto recién creado no tiene `id` hasta que se hace `commit()` o `session.flush()`.

**d) Si cargas los datos desde los CSV de [`data/raw/`](../data/raw/)**
Lee primero [`data/raw/README.md`](../data/raw/README.md). Ten en cuenta:
- Los CSV identifican cada fila con un texto de 32 caracteres (`order_id`, `customer_id`, `product_id`, `seller_id`), pero las tablas usan un `id` numérico autoincremental. ¿Cómo vas a recordar qué `id` nuevo le tocó a cada código del CSV para poder enlazar después las tablas que dependen de él?
- Algunos códigos postales perdieron el cero inicial (`3735` debería ser `03735`). La columna es texto de 5 caracteres.
- Pandas lee las celdas vacías como `NaN`. La base de datos espera `None`.
- Hay columnas del CSV que **no** existen en los modelos (por ejemplo `product_name_lenght`, `product_description_lenght` y `product_photos_qty`). No se pueden pasar al constructor.

---

## 4. Comprobar que se guardó

Después del `commit()`, abre una sesión nueva y consulta la tabla. El patrón general es:

```python
from sqlalchemy import select

with get_session() as session:
    resultado = session.scalars(select(<Modelo>)).all()
```

Cada modelo tiene un `__repr__`, así que puedes imprimir los objetos para revisarlos. Sigue también los atributos de relación (por ejemplo, desde una venta llega a su cliente) para confirmar que los enlaces quedaron bien.

---

## 5. Errores frecuentes

| Error | Causa probable | Qué revisar |
|:---|:---|:---|
| `IntegrityError: FOREIGN KEY constraint failed` | El registro apunta a un `id` que no existe | El orden de inserción y el `id` que estás pasando |
| `IntegrityError: NOT NULL constraint failed` | Falta una columna obligatoria | Las columnas que no son `Optional` |
| `TypeError: '<x>' is an invalid keyword argument` | Pasaste una columna que el modelo no tiene | El nombre exacto del atributo en el modelo |
| `StatementError ... SQLite DateTime type only accepts Python datetime` | Pasaste una fecha como texto | La conversión a `datetime` |
| `ModuleNotFoundError: No module named 'models'` | Ejecutaste el script desde otra carpeta | Ejecuta desde la raíz del proyecto |
| No aparece nada en la base de datos | Falta `session.commit()` | Que el `commit()` esté dentro del `with` |

Si un `commit()` falla, la transacción queda anulada. Llama a `session.rollback()` antes de volver a usar esa sesión.

---

## 6. Lista de verificación

- [ ] Llamé a `init_db()` y existe `data/gummy_erp.db`.
- [ ] Para cada modelo sé qué columnas son obligatorias y de qué tipo.
- [ ] Decidí el orden de inserción a partir del diagrama.
- [ ] Decidí cómo enlazar registros: por objeto o por `id`.
- [ ] Si cargo desde CSV: tengo una forma de traducir los códigos del CSV a los `id` nuevos.
- [ ] Hago `commit()` y consulto con una sesión nueva para verificar.

Referencias:
- [SQLAlchemy ORM Quick Start](https://docs.sqlalchemy.org/en/20/orm/quickstart.html)
- [Inserting rows using the ORM](https://docs.sqlalchemy.org/en/20/tutorial/orm_data_manipulation.html#inserting-rows-using-the-orm-unit-of-work-pattern)
