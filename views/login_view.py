"""Pantalla de inicio de sesion: fondo imagen-login.png y formulario a la derecha."""
import flet as ft

from controllers.auth_controller import iniciar_sesion
from views.componentes import NARANJA, ROJO


def construir_login_view(page: ft.Page, al_iniciar_sesion) -> ft.Control:
    """al_iniciar_sesion(usuario) se llama cuando las credenciales son correctas."""

    estilo_campo = dict(
        border_radius=12, filled=True,
        bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
        border_color=ft.Colors.with_opacity(0.25, ft.Colors.WHITE),
        focused_border_color=NARANJA,
        color=ft.Colors.WHITE,
        label_style=ft.TextStyle(color=ft.Colors.WHITE_70),
        cursor_color=NARANJA,
    )
    campo_usuario = ft.TextField(label="Usuario o correo", prefix_icon=ft.Icons.PERSON_OUTLINE,
                                 autofocus=True, **estilo_campo)
    campo_password = ft.TextField(label="Contraseña", prefix_icon=ft.Icons.LOCK_OUTLINE,
                                  password=True, can_reveal_password=True, **estilo_campo)
    mensaje = ft.Text("", color="#FF8A8A", size=13)

    def ingresar(e):
        usuario, error = iniciar_sesion(campo_usuario.value, campo_password.value)
        if error:
            mensaje.value = error
            campo_password.value = ""
            page.update()
            return
        al_iniciar_sesion(usuario)

    # Enter en cualquiera de los campos tambien inicia sesion
    campo_usuario.on_submit = ingresar
    campo_password.on_submit = ingresar

    formulario = ft.Container(
        width=400,
        padding=36,
        border_radius=22,
        bgcolor=ft.Colors.with_opacity(0.72, "#140B1C"),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.15, NARANJA)),
        blur=ft.Blur(12, 12),
        shadow=ft.BoxShadow(blur_radius=40, color=ft.Colors.with_opacity(0.45, ROJO)),
        content=ft.Column(
            [
                ft.Image(src="Logo.png", width=170),
                ft.Text("Bienvenido", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Text("Inicia sesión para continuar", size=13, color=ft.Colors.WHITE_70),
                ft.Container(height=6),
                campo_usuario,
                campo_password,
                mensaje,
                ft.FilledButton(
                    "Iniciar sesión", icon=ft.Icons.LOGIN, on_click=ingresar, height=48,
                    width=float("inf"),
                    style=ft.ButtonStyle(bgcolor=NARANJA, color=ft.Colors.WHITE,
                                         shape=ft.RoundedRectangleBorder(radius=12)),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            tight=True,
        ),
    )

    return ft.Stack(
        [
            # Fondo: imagen existente del proyecto ocupando toda la pantalla
            ft.Image(src="imagen-login.png", fit=ft.BoxFit.COVER, expand=True,
                     width=float("inf"), height=float("inf")),
            ft.Container(
                content=formulario,
                alignment=ft.Alignment.CENTER_RIGHT,
                padding=ft.Padding.only(right=70, left=20),
                expand=True,
            ),
        ],
        expand=True,
    )
