"""Dashboard: 4 indicadores y 3 graficas generadas con Matplotlib."""
import flet as ft

from controllers.dashboard_controller import obtener_graficas
from controllers.dashboard_controller import obtener_indicadores
from views.componentes import DORADO, MORADO, NARANJA, ROJO
from views.componentes import encabezado, imagen_grafica, moneda, panel, tarjeta_indicador


def construir_dashboard_view(page: ft.Page, usuario: dict) -> ft.Control:
    datos = obtener_indicadores()
    graficas = obtener_graficas()

    tarjetas = ft.Row([
        tarjeta_indicador("Total de ventas", f"{datos['total_ventas']:,}", ft.Icons.RECEIPT_LONG, NARANJA),
        tarjeta_indicador("Productos registrados", f"{datos['productos']:,}", ft.Icons.INVENTORY_2, MORADO),
        tarjeta_indicador("Bajo inventario", f"{datos['bajo_stock']:,}", ft.Icons.WARNING_AMBER, ROJO),
        tarjeta_indicador("Ingresos totales", moneda(datos["ingresos"]), ft.Icons.PAYMENTS, DORADO),
    ], spacing=16)

    aviso = []
    if datos["total_ventas"] == 0:
        aviso.append(ft.Text("Todavía no hay ventas registradas. Registra una venta para ver las gráficas.",
                             italic=True, color=ft.Colors.GREY_600))

    return ft.Column(
        [
            encabezado(f"Hola, {usuario['nombre']}", "Resumen general del negocio"),
            tarjetas,
            *aviso,
            ft.Row([
                panel(imagen_grafica(graficas["ventas_mes"]), "Ventas por mes", expand=3),
                panel(imagen_grafica(graficas["categorias"]), "Ventas por categoría", expand=2),
            ], spacing=16, vertical_alignment=ft.CrossAxisAlignment.START),
            ft.Row([
                panel(imagen_grafica(graficas["top_productos"]), "Productos más vendidos", expand=True),
            ]),
        ],
        spacing=18,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
