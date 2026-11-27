"""Analisis de datos con Pandas y graficas con Matplotlib.

Cada funcion lee las tablas de la base de datos en un DataFrame y devuelve
resultados sencillos (numeros, DataFrames o imagenes PNG) listos para la vista.
"""
import io

import pandas as pd
from matplotlib.figure import Figure

from models.database import engine

# Paleta de la identidad visual de GUMMY ERP (tonos del logo)
NARANJA = "#FF6B00"
ROJO = "#D72638"
MORADO = "#7137C8"
DORADO = "#F2A900"
GRIS = "#6B7280"
PALETA = [NARANJA, MORADO, ROJO, DORADO, "#2A9D8F", "#E76F51", "#8E7DBE", "#9CA3AF"]

MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


# ----------------------------------------------------------------------
# Lectura de datos
# ----------------------------------------------------------------------
def ventas_df() -> pd.DataFrame:
    """Una fila por cada producto vendido (detalle de venta)."""
    consulta = """
        SELECT s.id AS venta_id, s.fecha, p.id AS producto_id, p.nombre AS producto,
               COALESCE(p.categoria, 'Sin categoría') AS categoria,
               d.cantidad, d.precio_unitario, d.subtotal
        FROM sale_detail d
        JOIN sale s ON s.id = d.venta_id
        JOIN product p ON p.id = d.producto_id
    """
    df = pd.read_sql(consulta, engine, parse_dates=["fecha"])
    return df


def productos_df() -> pd.DataFrame:
    return pd.read_sql("SELECT id, nombre, categoria, precio, stock, stock_minimo FROM product", engine)


def movimientos_df() -> pd.DataFrame:
    consulta = """
        SELECT m.id, m.fecha, m.tipo, m.cantidad, m.motivo, p.nombre AS producto
        FROM inventory_movement m JOIN product p ON p.id = m.producto_id
    """
    return pd.read_sql(consulta, engine, parse_dates=["fecha"])


# ----------------------------------------------------------------------
# Indicadores y tablas
# ----------------------------------------------------------------------
def indicadores() -> dict:
    """Tarjetas del dashboard. Si no hay datos devuelve ceros."""
    ventas = ventas_df()
    productos = productos_df()
    return {
        "total_ventas": int(ventas["venta_id"].nunique()) if not ventas.empty else 0,
        "productos": int(len(productos)),
        "bajo_stock": int((productos["stock"] <= productos["stock_minimo"]).sum()) if not productos.empty else 0,
        "ingresos": float(ventas["subtotal"].sum()) if not ventas.empty else 0.0,
    }


def resumen_ventas() -> dict:
    ventas = ventas_df()
    if ventas.empty:
        return {"ventas": 0, "ingresos": 0.0, "ticket_promedio": 0.0, "unidades": 0,
                "primera": None, "ultima": None}
    por_venta = ventas.groupby("venta_id")["subtotal"].sum()
    return {
        "ventas": int(por_venta.count()),
        "ingresos": float(por_venta.sum()),
        "ticket_promedio": float(por_venta.mean()),
        "unidades": int(ventas["cantidad"].sum()),
        "primera": ventas["fecha"].min(),
        "ultima": ventas["fecha"].max(),
    }


def productos_mas_vendidos(n: int = 5) -> pd.DataFrame:
    ventas = ventas_df()
    if ventas.empty:
        return pd.DataFrame(columns=["producto", "unidades", "ingresos"])
    tabla = (ventas.groupby("producto")
             .agg(unidades=("cantidad", "sum"), ingresos=("subtotal", "sum"))
             .sort_values(["unidades", "ingresos"], ascending=False)
             .head(n)
             .reset_index())
    return tabla


def ventas_por_categoria() -> pd.DataFrame:
    ventas = ventas_df()
    if ventas.empty:
        return pd.DataFrame(columns=["categoria", "ingresos"])
    return (ventas.groupby("categoria")["subtotal"].sum()
            .sort_values(ascending=False).rename("ingresos").reset_index())


# Codigos de periodo de Pandas: dia, semana, mes, anio
PERIODOS = {"Día": "D", "Semana": "W", "Mes": "M", "Año": "Y"}


def ingresos_por_periodo(periodo: str = "Mes") -> pd.DataFrame:
    """Agrupa las ventas por dia, semana, mes o anio."""
    ventas = ventas_df()
    if ventas.empty:
        return pd.DataFrame(columns=["periodo", "ventas", "unidades", "ingresos"])
    ventas["periodo"] = ventas["fecha"].dt.to_period(PERIODOS.get(periodo, "M"))
    tabla = (ventas.groupby("periodo")
             .agg(ventas=("venta_id", "nunique"), unidades=("cantidad", "sum"), ingresos=("subtotal", "sum"))
             .reset_index())
    tabla["periodo"] = tabla["periodo"].astype(str)
    return tabla


def rotacion_productos(n: int = 5):
    """Devuelve (mayor_rotacion, menor_rotacion) segun las unidades vendidas.

    Se incluyen los productos que nunca se vendieron (0 unidades).
    """
    productos = productos_df()
    if productos.empty:
        vacio = pd.DataFrame(columns=["producto", "unidades", "stock"])
        return vacio, vacio
    vendidos = ventas_df().groupby("producto_id")["cantidad"].sum()
    productos["unidades"] = productos["id"].map(vendidos).fillna(0).astype(int)
    tabla = productos.rename(columns={"nombre": "producto"})[["producto", "unidades", "stock"]]
    mayor = tabla.sort_values("unidades", ascending=False).head(n)
    menor = tabla.sort_values("unidades", ascending=True).head(n)
    return mayor, menor


def productos_para_reponer() -> pd.DataFrame:
    """Productos en o por debajo del stock minimo y cuanto conviene pedir.

    Sugerencia sencilla: llevar el stock al doble del minimo.
    """
    productos = productos_df()
    if productos.empty:
        return pd.DataFrame(columns=["producto", "stock", "stock_minimo", "sugerido"])
    bajos = productos[productos["stock"] <= productos["stock_minimo"]].copy()
    bajos["sugerido"] = (bajos["stock_minimo"] * 2 - bajos["stock"]).clip(lower=1)
    return (bajos.rename(columns={"nombre": "producto"})
            [["producto", "stock", "stock_minimo", "sugerido"]]
            .sort_values("stock"))


def resumen_movimientos() -> pd.DataFrame:
    movimientos = movimientos_df()
    if movimientos.empty:
        return pd.DataFrame(columns=["tipo", "movimientos", "unidades"])
    return (movimientos.groupby("tipo")
            .agg(movimientos=("id", "count"), unidades=("cantidad", "sum"))
            .reset_index())


# ----------------------------------------------------------------------
# Graficas (se devuelven como bytes PNG para mostrarlas con ft.Image)
# ----------------------------------------------------------------------
def _nueva_figura(ancho=6.4, alto=3.4):
    # Se usa Figure directamente (sin pyplot) porque es seguro en un servidor web
    fig = Figure(figsize=(ancho, alto), dpi=110)
    ax = fig.add_subplot()
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#D1D5DB")
    ax.tick_params(colors=GRIS, labelsize=8)
    ax.grid(axis="y", color="#EEEEEE")
    ax.set_axisbelow(True)
    return fig, ax


def _a_png(fig) -> bytes:
    buffer = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buffer, format="png", facecolor="white")
    return buffer.getvalue()


def _etiqueta_mes(periodo: str) -> str:
    anio, mes = periodo.split("-")
    return f"{MESES[int(mes) - 1]}\n{anio}"


def grafica_ventas_por_mes(ultimos: int = 12):
    """Ingresos de los ultimos meses que tienen ventas."""
    tabla = ingresos_por_periodo("Mes").tail(ultimos)
    if tabla.empty:
        return None
    fig, ax = _nueva_figura()
    etiquetas = [_etiqueta_mes(p) for p in tabla["periodo"]]
    ax.bar(etiquetas, tabla["ingresos"], color=NARANJA, width=0.65)
    ax.set_ylabel("Ingresos ($)", color=GRIS, fontsize=8)
    ax.yaxis.set_major_formatter(lambda v, _: f"${v:,.0f}")
    return _a_png(fig)


def grafica_ingresos_periodo(periodo: str = "Mes"):
    tabla = ingresos_por_periodo(periodo)
    if tabla.empty:
        return None
    fig, ax = _nueva_figura(7.5, 3.4)
    ax.plot(tabla["periodo"], tabla["ingresos"], color=MORADO, marker="o", linewidth=2)
    ax.fill_between(range(len(tabla)), tabla["ingresos"], color=MORADO, alpha=0.08)
    ax.yaxis.set_major_formatter(lambda v, _: f"${v:,.0f}")
    if len(tabla) > 8:
        ax.tick_params(axis="x", rotation=45)
    return _a_png(fig)


def grafica_top_productos(n: int = 5):
    tabla = productos_mas_vendidos(n)
    if tabla.empty:
        return None
    tabla = tabla.iloc[::-1]  # el mas vendido arriba
    fig, ax = _nueva_figura()
    ax.barh(tabla["producto"], tabla["unidades"], color=ROJO, height=0.6)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color="#EEEEEE")
    ax.set_xlabel("Unidades vendidas", color=GRIS, fontsize=8)
    for i, valor in enumerate(tabla["unidades"]):
        ax.text(valor, i, f" {valor}", va="center", fontsize=8, color=GRIS)
    return _a_png(fig)


def grafica_categorias(max_categorias: int = 6):
    tabla = ventas_por_categoria()
    if tabla.empty:
        return None
    # Las categorias pequenas se agrupan en "Otras" para no saturar la grafica
    if len(tabla) > max_categorias:
        principales = tabla.head(max_categorias - 1)
        otras = pd.DataFrame([{"categoria": "Otras", "ingresos": tabla["ingresos"].iloc[max_categorias - 1:].sum()}])
        tabla = pd.concat([principales, otras], ignore_index=True)
    colores = [("#C7CBD1" if c == "Otras" else PALETA[i]) for i, c in enumerate(tabla["categoria"])]
    fig = Figure(figsize=(6.4, 3.4), dpi=110)
    ax = fig.add_subplot()
    ax.pie(tabla["ingresos"], colors=colores, startangle=90, counterclock=False,
           autopct=lambda pct: f"{pct:.0f}%" if pct >= 5 else "", pctdistance=0.78,
           wedgeprops={"width": 0.42, "edgecolor": "white"}, textprops={"fontsize": 8, "color": "white"})
    ax.legend(tabla["categoria"], loc="center left", bbox_to_anchor=(1, 0.5), frameon=False, fontsize=8)
    ax.set_aspect("equal")
    return _a_png(fig)
