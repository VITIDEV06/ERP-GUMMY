"""Controlador de reportes: convierte los resultados de Pandas en listas para la vista."""
from services import analisis_service as analisis

PERIODOS = list(analisis.PERIODOS.keys())


def _filas(df) -> list[dict]:
    return df.to_dict(orient="records")


def resumen_ventas() -> dict:
    return analisis.resumen_ventas()


def productos_mas_vendidos(n: int = 10) -> list[dict]:
    return _filas(analisis.productos_mas_vendidos(n))


def ingresos_por_periodo(periodo: str = "Mes") -> list[dict]:
    return _filas(analisis.ingresos_por_periodo(periodo))


def rotacion_productos(n: int = 5):
    mayor, menor = analisis.rotacion_productos(n)
    return _filas(mayor), _filas(menor)


def productos_para_reponer() -> list[dict]:
    return _filas(analisis.productos_para_reponer())


def resumen_movimientos() -> list[dict]:
    return _filas(analisis.resumen_movimientos())


def grafica_ingresos(periodo: str = "Mes"):
    return analisis.grafica_ingresos_periodo(periodo)


def grafica_top_productos():
    return analisis.grafica_top_productos(10)
