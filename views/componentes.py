"""Componentes visuales reutilizados por todas las vistas (colores, tarjetas, tablas, dialogos)."""
import flet as ft

# Colores de la identidad visual de GUMMY ERP (tomados del logo)
NARANJA = "#FF6B00"
ROJO = "#D72638"
MORADO = "#7137C8"
DORADO = "#F2A900"
VERDE = "#2A9D8F"
OSCURO = "#1C1326"      # fondo del menu lateral
FONDO = "#F6F4F8"       # fondo del area de trabajo
TEXTO_SUAVE = "#6B7280"


def moneda(valor) -> str:
    return f"${float(valor or 0):,.2f}"


def fecha_texto(fecha) -> str:
    return fecha.strftime("%d/%m/%Y %H:%M") if fecha else "-"


def encabezado(titulo: str, subtitulo: str = "", acciones=None) -> ft.Control:
    return ft.Row(
        [
            ft.Column([
                ft.Text(titulo, size=26, weight=ft.FontWeight.BOLD),
                ft.Text(subtitulo, size=13, color=TEXTO_SUAVE),
            ], spacing=2, expand=True),
            *(acciones or []),
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )


def panel(contenido: ft.Control, titulo: str = "", expand=None, padding=18) -> ft.Container:
    """Tarjeta blanca con titulo opcional."""
    hijos = [ft.Text(titulo, size=15, weight=ft.FontWeight.W_600)] if titulo else []
    hijos.append(contenido)
    return ft.Container(
        content=ft.Column(hijos, spacing=10, expand=True if expand else None),
        bgcolor=ft.Colors.WHITE,
        border_radius=14,
        padding=padding,
        expand=expand,
        shadow=ft.BoxShadow(blur_radius=12, color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK)),
    )


def tarjeta_indicador(titulo: str, valor: str, icono, color: str) -> ft.Container:
    return ft.Container(
        content=ft.Row([
            ft.Container(
                content=ft.Icon(icono, color=color, size=26),
                bgcolor=ft.Colors.with_opacity(0.12, color),
                border_radius=12, padding=12,
            ),
            ft.Column([
                ft.Text(titulo, size=12, color=TEXTO_SUAVE),
                ft.Text(valor, size=22, weight=ft.FontWeight.BOLD),
            ], spacing=0, expand=True),
        ], spacing=14),
        bgcolor=ft.Colors.WHITE,
        border_radius=14,
        padding=16,
        expand=True,
        border=ft.Border.only(left=ft.BorderSide(4, color)),
        shadow=ft.BoxShadow(blur_radius=12, color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK)),
    )


def tabla(columnas: list[str], filas: list[list], numericas: tuple = (), mensaje_vacio="Sin registros.",
          espacio: int = 28) -> ft.Control:
    """Crea una tabla a partir de una lista de filas (cada celda puede ser texto o un control)."""
    if not filas:
        return ft.Container(ft.Text(mensaje_vacio, color=TEXTO_SUAVE, italic=True), padding=20)

    def celda(valor):
        return ft.DataCell(valor if isinstance(valor, ft.Control) else ft.Text(str(valor), size=13))

    return ft.Row([
        ft.DataTable(
            columns=[ft.DataColumn(ft.Text(c, weight=ft.FontWeight.BOLD, size=13), numeric=i in numericas)
                     for i, c in enumerate(columnas)],
            rows=[ft.DataRow(cells=[celda(v) for v in fila]) for fila in filas],
            heading_row_color=ft.Colors.with_opacity(0.08, NARANJA),
            heading_row_height=42,
            data_row_min_height=38,
            data_row_max_height=44,
            column_spacing=espacio,
            divider_thickness=0.5,
        )
    ], scroll=ft.ScrollMode.AUTO)


def etiqueta(texto: str, color: str) -> ft.Container:
    """Pequena 'pastilla' de color, por ejemplo para 'Bajo stock'."""
    return ft.Container(
        ft.Text(texto, size=11, color=color, weight=ft.FontWeight.W_600),
        bgcolor=ft.Colors.with_opacity(0.12, color),
        border_radius=20,
        padding=ft.Padding.symmetric(horizontal=10, vertical=3),
    )


def imagen_grafica(png, mensaje_vacio="Aún no hay datos suficientes para esta gráfica.") -> ft.Control:
    if not png:
        return ft.Container(
            ft.Column([ft.Icon(ft.Icons.INSERT_CHART_OUTLINED, color=TEXTO_SUAVE, size=40),
                       ft.Text(mensaje_vacio, color=TEXTO_SUAVE, text_align=ft.TextAlign.CENTER)],
                      horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.Alignment.CENTER, height=220,
        )
    return ft.Image(src=png, fit=ft.BoxFit.CONTAIN)


def campo(etiqueta_campo: str, valor="", ancho=None, **kwargs) -> ft.TextField:
    return ft.TextField(label=etiqueta_campo, value="" if valor is None else str(valor),
                        width=ancho, border_radius=10, dense=True, **kwargs)


def buscador(al_cambiar, texto="Buscar...") -> ft.TextField:
    return ft.TextField(hint_text=texto, prefix_icon=ft.Icons.SEARCH, width=280, dense=True,
                        border_radius=10, on_change=al_cambiar, bgcolor=ft.Colors.WHITE)


def boton_principal(texto: str, icono, al_hacer_clic) -> ft.FilledButton:
    return ft.FilledButton(texto, icon=icono, on_click=al_hacer_clic,
                           style=ft.ButtonStyle(bgcolor=NARANJA, color=ft.Colors.WHITE))


def mostrar_mensaje(page: ft.Page, texto: str, error: bool = False) -> None:
    page.show_dialog(ft.SnackBar(
        ft.Text(texto, color=ft.Colors.WHITE),
        bgcolor=ROJO if error else VERDE,
    ))


def dialogo_formulario(page: ft.Page, titulo: str, controles: list, al_guardar, ancho=420) -> None:
    """Abre un dialogo con campos. al_guardar() devuelve (ok, mensaje)."""
    error = ft.Text("", color=ROJO, size=12)

    def guardar(e):
        ok, mensaje = al_guardar()
        if ok:
            page.pop_dialog()
            mostrar_mensaje(page, mensaje)
        else:
            error.value = mensaje
            error.update()

    page.show_dialog(ft.AlertDialog(
        modal=True,
        title=ft.Text(titulo, weight=ft.FontWeight.BOLD),
        content=ft.Container(ft.Column([*controles, error], tight=True, spacing=12,
                                       horizontal_alignment=ft.CrossAxisAlignment.STRETCH), width=ancho),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
            boton_principal("Guardar", ft.Icons.SAVE, guardar),
        ],
    ))


def confirmar(page: ft.Page, mensaje: str, al_confirmar) -> None:
    def si(e):
        page.pop_dialog()
        al_confirmar()

    page.show_dialog(ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirmar"),
        content=ft.Text(mensaje),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
            ft.FilledButton("Sí, continuar", on_click=si, style=ft.ButtonStyle(bgcolor=ROJO)),
        ],
    ))
