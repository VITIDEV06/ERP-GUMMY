"""Inventario: existencias, entradas/salidas, productos con bajo stock y movimientos."""
import flet as ft

from controllers import inventario_controller as controlador
from controllers.producto_controller import listar_productos
from models.movimiento_model import ENTRADA, SALIDA
from views.componentes import NARANJA, ROJO, VERDE
from views.componentes import (buscador, campo, dialogo_formulario, encabezado, etiqueta,
                               fecha_texto, panel, tabla)

SECCIONES = ["Existencias", "Bajo stock", "Movimientos"]


def construir_inventario_view(page: ft.Page, usuario: dict) -> ft.Control:
    estado = {"seccion": "Existencias"}
    contenido = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)

    def refrescar(e=None):
        seccion = estado["seccion"]
        caja_busqueda.visible = seccion == "Existencias"
        if seccion == "Existencias":
            filas = [[p["id"], p["nombre"], p["categoria"], p["stock"], p["stock_minimo"],
                      etiqueta("Bajo stock", ROJO) if p["bajo_stock"] else etiqueta("OK", VERDE)]
                     for p in controlador.listar_existencias(caja_busqueda.value or "")]
            contenido.controls = [tabla(["ID", "Producto", "Categoría", "Stock", "Mínimo", "Estado"],
                                        filas, numericas=(0, 3, 4))]
        elif seccion == "Bajo stock":
            filas = [[p["nombre"], p["categoria"], p["stock"], p["stock_minimo"]]
                     for p in controlador.productos_bajo_stock()]
            contenido.controls = [tabla(["Producto", "Categoría", "Stock", "Mínimo"], filas,
                                        numericas=(2, 3),
                                        mensaje_vacio="¡Muy bien! Ningún producto tiene bajo stock.")]
        else:
            filas = [[fecha_texto(m["fecha"]), m["producto"],
                      etiqueta("Entrada", VERDE) if m["tipo"] == ENTRADA else etiqueta("Salida", ROJO),
                      m["cantidad"], m["motivo"]]
                     for m in controlador.listar_movimientos()]
            contenido.controls = [tabla(["Fecha", "Producto", "Tipo", "Cantidad", "Motivo"], filas,
                                        numericas=(3,), mensaje_vacio="No hay movimientos registrados.")]
        for boton in selector.controls:
            activo = boton.data == seccion
            boton.style = ft.ButtonStyle(bgcolor=NARANJA if activo else ft.Colors.WHITE,
                                         color=ft.Colors.WHITE if activo else ft.Colors.BLACK_87)
        page.update()

    def cambiar_seccion(nombre):
        estado["seccion"] = nombre
        refrescar()

    def abrir_movimiento(tipo):
        productos = listar_productos()
        producto = ft.Dropdown(
            label="Producto", width=396, menu_height=320, dense=True,
            options=[ft.DropdownOption(key=str(p["id"]), text=f"{p['nombre']} (stock: {p['stock']})")
                     for p in productos],
        )
        cantidad = campo("Cantidad", "", keyboard_type=ft.KeyboardType.NUMBER)
        motivo = campo("Motivo (opcional)", "", hint_text="Compra a proveedor, merma, devolución...")

        def guardar():
            resultado = controlador.registrar_movimiento(producto.value, tipo, cantidad.value, motivo.value)
            if resultado[0]:
                refrescar()
            return resultado

        titulo = "Registrar entrada de inventario" if tipo == ENTRADA else "Registrar salida de inventario"
        dialogo_formulario(page, titulo, [producto, cantidad, motivo], guardar)

    selector = ft.Row([
        ft.OutlinedButton(nombre, data=nombre, on_click=lambda e, n=nombre: cambiar_seccion(n))
        for nombre in SECCIONES
    ])
    caja_busqueda = buscador(refrescar, "Buscar producto")

    acciones = []
    if usuario["es_admin"]:  # el vendedor solo consulta
        acciones = [
            ft.FilledButton("Entrada", icon=ft.Icons.ADD_BOX_OUTLINED, on_click=lambda e: abrir_movimiento(ENTRADA),
                            style=ft.ButtonStyle(bgcolor=VERDE, color=ft.Colors.WHITE)),
            ft.FilledButton("Salida", icon=ft.Icons.INDETERMINATE_CHECK_BOX_OUTLINED,
                            on_click=lambda e: abrir_movimiento(SALIDA),
                            style=ft.ButtonStyle(bgcolor=ROJO, color=ft.Colors.WHITE)),
        ]

    vista = ft.Column(
        [
            encabezado("Inventario", "Existencias y movimientos de entrada y salida", acciones),
            panel(ft.Column([ft.Row([selector, caja_busqueda], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                             contenido], expand=True), expand=True),
        ],
        spacing=18, expand=True,
    )
    refrescar()
    return vista
