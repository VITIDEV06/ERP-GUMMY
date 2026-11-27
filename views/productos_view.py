"""Productos: registrar, consultar, editar y eliminar (editar/eliminar solo administrador)."""
import flet as ft

from controllers import producto_controller as controlador
from views.componentes import MORADO, ROJO, VERDE
from views.componentes import (boton_principal, buscador, campo, confirmar, dialogo_formulario,
                               encabezado, etiqueta, moneda, mostrar_mensaje, panel, tabla)


def construir_productos_view(page: ft.Page, usuario: dict) -> ft.Control:
    es_admin = usuario["es_admin"]
    contenedor_tabla = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)

    def refrescar(e=None):
        productos = controlador.listar_productos(caja_busqueda.value or "")
        filas = []
        for p in productos:
            estado = etiqueta("Bajo stock", ROJO) if p["bajo_stock"] else etiqueta("Disponible", VERDE)
            fila = [p["id"], p["nombre"], p["categoria"], moneda(p["precio"]), p["stock"], estado]
            if es_admin:
                fila.append(ft.Row([
                    ft.IconButton(ft.Icons.EDIT_OUTLINED, icon_color=MORADO, tooltip="Editar",
                                  on_click=lambda e, p=p: abrir_formulario(p)),
                    ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=ROJO, tooltip="Eliminar",
                                  on_click=lambda e, p=p: eliminar(p)),
                ], spacing=0))
            filas.append(fila)
        columnas = ["ID", "Nombre", "Categoría", "Precio", "Stock", "Estado"] + (["Acciones"] if es_admin else [])
        contenedor_tabla.controls = [tabla(columnas, filas, numericas=(0, 3, 4),
                                           mensaje_vacio="No hay productos registrados.")]
        contador.value = f"{len(productos)} producto(s)"
        page.update()

    def abrir_formulario(producto=None):
        p = producto or {}
        categorias = controlador.listar_categorias()
        nombre = campo("Nombre", p.get("nombre"))
        # Campo de texto libre: se muestran las categorias existentes como ayuda
        categoria = campo("Categoría", p.get("categoria") if p.get("categoria") != "Sin categoría" else "",
                          helper="Existentes: " + ", ".join(categorias[:6]) + ("..." if len(categorias) > 6 else ""))
        precio = campo("Precio", p.get("precio"), prefix="$ ", keyboard_type=ft.KeyboardType.NUMBER)
        stock = campo("Cantidad disponible", p.get("stock", 0), keyboard_type=ft.KeyboardType.NUMBER, expand=True)
        minimo = campo("Stock mínimo", p.get("stock_minimo", 5), keyboard_type=ft.KeyboardType.NUMBER, expand=True)

        def guardar():
            datos = {"nombre": nombre.value, "categoria": categoria.value,
                     "precio": precio.value, "stock": stock.value, "stock_minimo": minimo.value}
            if producto:
                resultado = controlador.actualizar_producto(producto["id"], datos)
            else:
                resultado = controlador.crear_producto(datos)
            if resultado[0]:
                refrescar()
            return resultado

        dialogo_formulario(page, "Editar producto" if producto else "Nuevo producto",
                           [nombre, categoria, precio, ft.Row([stock, minimo])], guardar)

    def eliminar(producto):
        def hacerlo():
            ok, mensaje = controlador.eliminar_producto(producto["id"])
            mostrar_mensaje(page, mensaje, error=not ok)
            refrescar()
        confirmar(page, f"¿Eliminar el producto «{producto['nombre']}»?", hacerlo)

    caja_busqueda = buscador(refrescar, "Buscar por nombre o categoría")
    contador = ft.Text("", color=ft.Colors.GREY_600)
    # Solo el administrador registra, edita o elimina productos; el vendedor consulta
    acciones = [boton_principal("Nuevo producto", ft.Icons.ADD, lambda e: abrir_formulario())] if es_admin else []

    vista = ft.Column(
        [
            encabezado("Productos", "Catálogo, precios y cantidades disponibles", acciones),
            panel(ft.Column([ft.Row([caja_busqueda, contador], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                             contenedor_tabla], expand=True), expand=True),
        ],
        spacing=18, expand=True,
    )
    refrescar()  # carga inicial de la tabla
    return vista
