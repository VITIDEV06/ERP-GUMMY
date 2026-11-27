"""Controlador del dashboard: reune indicadores y graficas del servicio de analisis."""
from services import analisis_service as analisis


def obtener_indicadores() -> dict:
    return analisis.indicadores()


def obtener_graficas() -> dict:
    """Cada grafica es una imagen PNG en bytes, o None si no hay datos."""
    return {
        "ventas_mes": analisis.grafica_ventas_por_mes(),
        "top_productos": analisis.grafica_top_productos(),
        "categorias": analisis.grafica_categorias(),
    }
