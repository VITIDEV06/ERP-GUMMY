"""Clientes: registrar, consultar, editar y eliminar (si no tiene ventas)."""
import flet as ft

from controllers import cliente_controller as controlador
from views.componentes import MORADO, ROJO
from views.componentes import (boton_principal, buscador, campo, confirmar, dialogo_formulario,
                               encabezado, mostrar_mensaje, panel, tabla)


def construir_clientes_view(page: ft.Page, usuario: dict) -> ft.Control:
    contenedor_tabla = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)

    def refrescar(e=None):
        clientes = controlador.listar_clientes(caja_busqueda.value or "")
        filas = []
        for c in clientes:
            botones = [ft.IconButton(ft.Icons.EDIT_OUTLINED, icon_color=MORADO, tooltip="Editar",
                                     on_click=lambda e, c=c: abrir_formulario(c))]
            if usuario["es_admin"]:  # solo el administrador elimina clientes
                botones.append(ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=ROJO, tooltip="Eliminar",
                                             on_click=lambda e, c=c: eliminar(c)))
            filas.append([c["id"], c["nombre"], c["telefono"], c["correo"], c["ciudad"], c["compras"],
                          ft.Row(botones, spacing=0)])
        contenedor_tabla.controls = [tabla(["ID", "Nombre", "Teléfono", "Correo", "Ciudad", "Compras", "Acciones"],
                                           filas, numericas=(0, 5), mensaje_vacio="No hay clientes registrados.")]
        contador.value = f"{len(clientes)} cliente(s)"
        page.update()

    def abrir_formulario(cliente=None):
        c = cliente or {}
        nombre = campo("Nombre", c.get("nombre"))
        telefono = campo("Teléfono", c.get("telefono"), keyboard_type=ft.KeyboardType.PHONE)
        correo = campo("Correo", c.get("correo"), keyboard_type=ft.KeyboardType.EMAIL)
        ciudad = campo("Ciudad", c.get("ciudad"), expand=True)
        estado = campo("Estado", c.get("estado"), expand=True)

        def guardar():
            datos = {"nombre": nombre.value, "telefono": telefono.value, "correo": correo.value,
                     "ciudad": ciudad.value, "estado": estado.value}
            if cliente:
                resultado = controlador.actualizar_cliente(cliente["id"], datos)
            else:
                resultado = controlador.crear_cliente(datos)
            if resultado[0]:
                refrescar()
            return resultado

        dialogo_formulario(page, "Editar cliente" if cliente else "Nuevo cliente",
                           [nombre, telefono, correo, ft.Row([ciudad, estado])], guardar)

    def eliminar(cliente):
        def hacerlo():
            ok, mensaje = controlador.eliminar_cliente(cliente["id"])
            mostrar_mensaje(page, mensaje, error=not ok)
            refrescar()
        confirmar(page, f"¿Eliminar al cliente «{cliente['nombre']}»?", hacerlo)

    caja_busqueda = buscador(refrescar, "Buscar por nombre, ciudad o correo")
    contador = ft.Text("", color=ft.Colors.GREY_600)

    vista = ft.Column(
        [
            encabezado("Clientes", "Personas y negocios que compran en tu tienda",
                       [boton_principal("Nuevo cliente", ft.Icons.PERSON_ADD, lambda e: abrir_formulario())]),
            panel(ft.Column([ft.Row([caja_busqueda, contador], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                             contenedor_tabla], expand=True), expand=True),
        ],
        spacing=18, expand=True,
    )
    refrescar()
    return vista
