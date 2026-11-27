"""Controlador de autenticacion: verifica usuario/correo y contrasena con bcrypt."""
import bcrypt
from sqlalchemy import or_
from sqlalchemy import select

from models.database import get_session
from models.usuario_model import Usuario


def generar_hash(password: str) -> str:
    """Devuelve el hash bcrypt de la contrasena (incluye la sal)."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def iniciar_sesion(usuario_o_correo: str, password: str):
    """Devuelve (datos_del_usuario, None) si es correcto o (None, mensaje_de_error)."""
    usuario_o_correo = (usuario_o_correo or "").strip().lower()
    if not usuario_o_correo or not password:
        return None, "Escribe tu usuario o correo y tu contraseña."

    with get_session() as session:
        usuario = session.scalar(
            select(Usuario).where(
                or_(Usuario.usuario == usuario_o_correo, Usuario.correo == usuario_o_correo)
            )
        )
        if usuario is None or not verificar_password(password, usuario.password_hash):
            return None, "Usuario o contraseña incorrectos."

        # Se devuelve un diccionario sencillo para que la vista no toque el modelo
        return {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "usuario": usuario.usuario,
            "rol": usuario.rol,
            "es_admin": usuario.es_admin(),
        }, None
