"""Reportes: resumen de ventas, ingresos por periodo, productos mas vendidos,
rotacion, reposicion y resumen de movimientos (analisis con Pandas)."""
import flet as ft

from controllers import reporte_controller as controlador
from views.componentes import DORADO, MORADO, NARANJA, VERDE
from views.componentes import (encabezado, fecha_texto, imagen_grafica, moneda, panel, tabla,
                               tarjeta_indicador)


def construir_reportes_view(page: ft.Page, usuario: dict) -> ft.Control:
    resumen = controlador.resumen_ventas()

    tarjetas = ft.Row([
        tarjeta_indicador("Ventas", f"{resumen['ventas']:,}", ft.Icons.RECEIPT_LONG, NARANJA),
        tarjeta_indicador("Ingresos", moneda(resumen["ingresos"]), ft.Icons.PAYMENTS, DORADO),
        tarjeta_indicador("Ticket promedio", moneda(resumen["ticket_promedio"]), ft.Icons.SHOPPING_BAG, MORADO),
        tarjeta_indicador("Unidades vendidas", f"{resumen['unidades']:,}", ft.Icons.INVENTORY, VERDE),
    ], spacing=16)
    rango = (f"Datos del {fecha_texto(resumen['primera'])[:10]} al {fecha_texto(resumen['ultima'])[:10]}"
             if resumen["primera"] is not None else "Todavía no hay ventas registradas.")

    # ---------- Ingresos por periodo (con selector) ----------
    grafica_periodo = ft.Container()
    tabla_periodo = ft.Column(height=260, scroll=ft.ScrollMode.AUTO)
    selector = ft.SegmentedButton(
        selected=["Mes"],
        segments=[ft.Segment(value=p, label=ft.Text(p)) for p in controlador.PERIODOS],
    )

    def cambiar_periodo(e=None):
        periodo = list(selector.selected)[0] if selector.selected else "Mes"
        grafica_periodo.content = imagen_grafica(controlador.grafica_ingresos(periodo))
        filas = [[f["periodo"], f["ventas"], f["unidades"], moneda(f["ingresos"])]
                 for f in reversed(controlador.ingresos_por_periodo(periodo))]
        tabla_periodo.controls = [tabla(["Periodo", "Ventas", "Unidades", "Ingresos"], filas, numericas=(1, 2, 3))]
        page.update()

    selector.on_change = cambiar_periodo

    # ---------- Tablas de analisis ----------
    top = [[i + 1, f["producto"], f["unidades"], moneda(f["ingresos"])]
           for i, f in enumerate(controlador.productos_mas_vendidos(10))]
    mayor, menor = controlador.rotacion_productos(5)
    reponer = [[f["producto"], f["stock"], f["stock_minimo"], f["sugerido"]]
               for f in controlador.productos_para_reponer()]
    movimientos = [[f["tipo"].capitalize(), f["movimientos"], f["unidades"]]
                   for f in controlador.resumen_movimientos()]

    def tabla_rotacion(datos):
        return tabla(["Producto", "Vendidas", "Stock"], [[f["producto"], f["unidades"], f["stock"]] for f in datos],
                     numericas=(1, 2))

    vista = ft.Column(
        [
            encabezado("Reportes", rango),
            tarjetas,
            panel(ft.Column([
                ft.Row([ft.Text("Ingresos por período", size=15, weight=ft.FontWeight.W_600), selector],
                       alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([ft.Container(grafica_periodo, expand=3), ft.Container(tabla_periodo, expand=2)],
                       vertical_alignment=ft.CrossAxisAlignment.START),
            ])),
            ft.Row([
                panel(imagen_grafica(controlador.grafica_top_productos()), "Productos más vendidos", expand=1),
                panel(ft.Column([tabla(["#", "Producto", "Unidades", "Ingresos"], top, numericas=(0, 2, 3))],
                                height=330, scroll=ft.ScrollMode.AUTO), "Top 10 por unidades", expand=1),
            ], spacing=16, vertical_alignment=ft.CrossAxisAlignment.START),
            ft.Row([
                panel(tabla_rotacion(mayor), "Mayor rotación", expand=1),
                panel(tabla_rotacion(menor), "Menor rotación", expand=1),
            ], spacing=16, vertical_alignment=ft.CrossAxisAlignment.START),
            ft.Row([
                panel(ft.Column([tabla(["Producto", "Stock", "Mínimo", "Pedir"], reponer, numericas=(1, 2, 3),
                                       mensaje_vacio="Ningún producto necesita reposición.")],
                                height=300, scroll=ft.ScrollMode.AUTO),
                      "Productos que necesitan reposición", expand=3),
                panel(tabla(["Tipo", "Movimientos", "Unidades"], movimientos, numericas=(1, 2),
                            mensaje_vacio="Sin movimientos."), "Movimientos de inventario", expand=2),
            ], spacing=16, vertical_alignment=ft.CrossAxisAlignment.START),
        ],
        spacing=18, scroll=ft.ScrollMode.AUTO, expand=True,
    )
    cambiar_periodo()
    return vista
