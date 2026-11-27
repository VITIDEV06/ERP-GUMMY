"""GUMMY ERP - punto de entrada.

Ejecutar con:  python main.py
La aplicacion se abre en el navegador (modo web de Flet).
"""
from pathlib import Path

import flet as ft

from models.database import init_db
from services.carga_inicial import cargar_datos_iniciales
from views.componentes import FONDO, NARANJA, OSCURO
from views.clientes_view import construir_clientes_view
from views.dashboard_view import construir_dashboard_view
from views.inventario_view import construir_inventario_view
from views.login_view import construir_login_view
from views.productos_view import construir_productos_view
from views.reportes_view import construir_reportes_view
from views.ventas_view import construir_ventas_view

CARPETA_ASSETS = str(Path(__file__).resolve().parent / "assets")
PUERTO = 8550

# (titulo, icono, funcion que construye la vista, solo_admin)
SECCIONES = [
    ("Dashboard", ft.Icons.DASHBOARD_OUTLINED, construir_dashboard_view, False),
    ("Productos", ft.Icons.INVENTORY_2_OUTLINED, construir_productos_view, False),
    ("Inventario", ft.Icons.WAREHOUSE_OUTLINED, construir_inventario_view, False),
    ("Ventas", ft.Icons.POINT_OF_SALE_OUTLINED, construir_ventas_view, False),
    ("Clientes", ft.Icons.PEOPLE_OUTLINE, construir_clientes_view, False),
    ("Reportes", ft.Icons.INSERT_CHART_OUTLINED, construir_reportes_view, True),
]


def main(page: ft.Page):
    page.title = "GUMMY ERP"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed=NARANJA)
    page.bgcolor = FONDO

    def mostrar_login():
        page.controls.clear()
        page.add(construir_login_view(page, al_iniciar_sesion=mostrar_aplicacion))

    def mostrar_aplicacion(usuario: dict):
        # El vendedor no ve las secciones marcadas como solo_admin
        secciones = [s for s in SECCIONES if usuario["es_admin"] or not s[3]]
        area_trabajo = ft.Container(expand=True, padding=28, bgcolor=FONDO)

        def abrir_seccion(indice: int):
            titulo, _, construir, _ = secciones[indice]
            area_trabajo.content = ft.Container(ft.ProgressRing(color=NARANJA), alignment=ft.Alignment.CENTER)
            page.update()
            area_trabajo.content = construir(page, usuario)
            page.update()

        menu = ft.NavigationRail(
            selected_index=0,
            extended=True,
            min_extended_width=220,
            bgcolor=OSCURO,
            indicator_color=ft.Colors.with_opacity(0.25, NARANJA),
            selected_label_text_style=ft.TextStyle(color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
            unselected_label_text_style=ft.TextStyle(color=ft.Colors.WHITE_70),
            leading=ft.Container(
                ft.Column([
                    ft.Image(src="Logo.png", width=120),
                    ft.Text(usuario["nombre"], color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
                    ft.Text(usuario["rol"].capitalize(), color=NARANJA, size=12),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                padding=ft.Padding.only(top=20, bottom=20),
            ),
            destinations=[
                ft.NavigationRailDestination(icon=ft.Icon(icono, color=ft.Colors.WHITE_70),
                                             selected_icon=ft.Icon(icono, color=NARANJA), label=titulo)
                for titulo, icono, _, _ in secciones
            ],
            trailing=ft.Container(
                ft.TextButton("Cerrar sesión", icon=ft.Icons.LOGOUT, on_click=lambda e: mostrar_login(),
                              style=ft.ButtonStyle(color=ft.Colors.WHITE_70)),
                padding=ft.Padding.only(top=30),
            ),
            on_change=lambda e: abrir_seccion(e.control.selected_index),
        )

        page.controls.clear()
        page.add(ft.Row([menu, area_trabajo], spacing=0, expand=True))
        abrir_seccion(0)

    mostrar_login()


if __name__ == "__main__":
    init_db()                 # crea data/gummy_erp.db y las tablas si no existen
    cargar_datos_iniciales()  # usuarios de prueba y datos de demostracion (solo si esta vacia)
    print(f"GUMMY ERP disponible en http://localhost:{PUERTO}")
    ft.run(main, view=ft.AppView.WEB_BROWSER, port=PUERTO, assets_dir=CARPETA_ASSETS)
