"""Ventas: registrar una venta con varios productos y consultar las ventas realizadas."""
import flet as ft

from controllers import venta_controller as controlador
from controllers.cliente_controller import listar_clientes
from controllers.producto_controller import listar_productos
from views.componentes import MORADO, NARANJA, ROJO, TEXTO_SUAVE
from views.componentes import (boton_principal, campo, encabezado, fecha_texto, moneda,
                               mostrar_mensaje, panel, tabla)


def construir_ventas_view(page: ft.Page, usuario: dict) -> ft.Control:
    carrito = []  # [{"producto_id", "nombre", "precio", "cantidad", "stock"}]
    productos = {}  # id (texto) -> datos del producto

    # ---------------- Formulario de nueva venta ----------------
    combo_cliente = ft.Dropdown(label="Cliente (opcional)", expand=True, menu_height=320, dense=True)
    combo_producto = ft.Dropdown(label="Producto", expand=True, dense=True,
                                 menu_height=320)
    campo_cantidad = campo("Cantidad", "1", ancho=100, keyboard_type=ft.KeyboardType.NUMBER)
    contenedor_carrito = ft.Column(scroll=ft.ScrollMode.AUTO, height=240)
    texto_total = ft.Text(moneda(0), size=26, weight=ft.FontWeight.BOLD, color=NARANJA)
    historial = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)

    def cargar_catalogos():
        productos.clear()
        for p in listar_productos():
            productos[str(p["id"])] = p
        combo_producto.options = [
            ft.DropdownOption(key=k, text=f"{p['nombre']} · {moneda(p['precio'])} · stock {p['stock']}")
            for k, p in productos.items() if p["stock"] > 0
        ]
        combo_cliente.options = [ft.DropdownOption(key=str(c["id"]), text=c["nombre"]) for c in listar_clientes()]

    def dibujar_carrito():
        filas = [[i["nombre"], i["cantidad"], moneda(i["precio"]), moneda(i["precio"] * i["cantidad"]),
                  ft.IconButton(ft.Icons.CLOSE, icon_color=ROJO, icon_size=18, tooltip="Quitar",
                                on_click=lambda e, i=i: quitar(i))]
                 for i in carrito]
        contenedor_carrito.controls = [tabla(["Producto", "Cant.", "Precio", "Subtotal", ""], filas,
                                             numericas=(1, 2, 3), mensaje_vacio="Agrega productos a la venta.",
                                             espacio=12)]
        texto_total.value = moneda(controlador.calcular_total(carrito))
        page.update()

    def agregar(e):
        producto = productos.get(combo_producto.value or "")
        if producto is None:
            mostrar_mensaje(page, "Selecciona un producto.", error=True)
            return
        try:
            cantidad = int(campo_cantidad.value)
        except ValueError:
            cantidad = 0
        if cantidad <= 0:
            mostrar_mensaje(page, "La cantidad debe ser un número mayor que cero.", error=True)
            return
        existente = next((i for i in carrito if i["producto_id"] == producto["id"]), None)
        total_pedido = cantidad + (existente["cantidad"] if existente else 0)
        if total_pedido > producto["stock"]:
            mostrar_mensaje(page, f"Solo hay {producto['stock']} unidades de {producto['nombre']}.", error=True)
            return
        if existente:
            existente["cantidad"] = total_pedido
        else:
            carrito.append({"producto_id": producto["id"], "nombre": producto["nombre"],
                            "precio": producto["precio"], "cantidad": cantidad})
        combo_producto.value = None
        campo_cantidad.value = "1"
        dibujar_carrito()

    def quitar(item):
        carrito.remove(item)
        dibujar_carrito()

    def registrar(e):
        ok, mensaje = controlador.registrar_venta(carrito, cliente_id=_id(combo_cliente.value),
                                                  usuario_id=usuario["id"])
        mostrar_mensaje(page, mensaje, error=not ok)
        if ok:
            carrito.clear()
            combo_cliente.value = None
            cargar_catalogos()  # el stock cambio
            dibujar_carrito()
            dibujar_historial()

    # ---------------- Historial de ventas ----------------
    def ver_detalle(venta):
        filas = [[d["producto"], d["cantidad"], moneda(d["precio"]), moneda(d["subtotal"])]
                 for d in controlador.detalle_de_venta(venta["id"])]
        page.show_dialog(ft.AlertDialog(
            title=ft.Text(f"Venta #{venta['id']}", weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Text(f"{fecha_texto(venta['fecha'])} · Cliente: {venta['cliente']} · Vendedor: {venta['vendedor']}",
                        color=TEXTO_SUAVE, size=12),
                tabla(["Producto", "Cantidad", "Precio", "Subtotal"], filas, numericas=(1, 2, 3)),
                ft.Text(f"Total: {moneda(venta['total'])}", size=18, weight=ft.FontWeight.BOLD),
            ], tight=True, scroll=ft.ScrollMode.AUTO),
            actions=[ft.TextButton("Cerrar", on_click=lambda e: page.pop_dialog())],
        ))

    def dibujar_historial():
        filas = [[v["id"], fecha_texto(v["fecha"]), v["cliente"], v["productos"], moneda(v["total"]),
                  ft.IconButton(ft.Icons.VISIBILITY_OUTLINED, icon_color=MORADO, tooltip="Ver detalle",
                                on_click=lambda e, v=v: ver_detalle(v))]
                 for v in controlador.listar_ventas()]
        historial.controls = [tabla(["#", "Fecha", "Cliente", "Productos", "Total", ""], filas,
                                    numericas=(0, 3, 4), mensaje_vacio="Aún no hay ventas registradas.")]
        page.update()

    nueva_venta = panel(ft.Column([
        ft.Row([combo_cliente]),
        ft.Row([combo_producto, campo_cantidad]),
        ft.OutlinedButton("Agregar a la venta", icon=ft.Icons.ADD_SHOPPING_CART, on_click=agregar),
        ft.Divider(),
        contenedor_carrito,
        ft.Row([ft.Text("Total", size=16, color=TEXTO_SUAVE), texto_total],
               alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Row([boton_principal("Registrar venta", ft.Icons.POINT_OF_SALE, registrar)],
               alignment=ft.MainAxisAlignment.END),
    ], spacing=12), "Nueva venta", expand=2)

    vista = ft.Column(
        [
            encabezado("Ventas", "Registra ventas y consulta el historial"),
            ft.Row([nueva_venta, panel(historial, "Ventas realizadas", expand=3)],
                   spacing=16, expand=True, vertical_alignment=ft.CrossAxisAlignment.START),
        ],
        spacing=18, expand=True,
    )
    cargar_catalogos()
    dibujar_carrito()
    dibujar_historial()
    return vista


def _id(valor):
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None
