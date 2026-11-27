"""Controlador de inventario: existencias, entradas, salidas y movimientos."""
from sqlalchemy import select

from models.database import get_session
from models.movimiento_model import ENTRADA
from models.movimiento_model import SALIDA
from models.movimiento_model import MovimientoInventario
from models.producto_model import Producto
from controllers.producto_controller import listar_productos


def listar_existencias(busqueda: str = "") -> list[dict]:
    return listar_productos(busqueda)


def productos_bajo_stock() -> list[dict]:
    return [p for p in listar_productos() if p["bajo_stock"]]


def registrar_movimiento(producto_id, tipo: str, cantidad, motivo: str = ""):
    """Registra una entrada o salida y actualiza el stock. Devuelve (ok, mensaje)."""
    if not producto_id:
        return False, "Selecciona un producto."
    if tipo not in (ENTRADA, SALIDA):
        return False, "Tipo de movimiento no válido."
    try:
        cantidad = int(cantidad)
    except (TypeError, ValueError):
        return False, "La cantidad debe ser un número entero."
    if cantidad <= 0:
        return False, "La cantidad debe ser mayor que cero."

    with get_session() as session:
        producto = session.get(Producto, int(producto_id))
        if producto is None:
            return False, "El producto no existe."
        if tipo == SALIDA and cantidad > producto.stock:
            return False, f"Stock insuficiente: solo hay {producto.stock} unidades."

        producto.stock += cantidad if tipo == ENTRADA else -cantidad
        session.add(MovimientoInventario(
            producto_id=producto.id, tipo=tipo, cantidad=cantidad,
            motivo=(motivo or "").strip() or ("Entrada manual" if tipo == ENTRADA else "Salida manual"),
        ))
        session.commit()
        return True, f"{tipo.capitalize()} registrada. Stock actual de {producto.nombre}: {producto.stock}."


def listar_movimientos(limite: int = 200) -> list[dict]:
    with get_session() as session:
        consulta = (
            select(MovimientoInventario, Producto.nombre)
            .join(Producto, MovimientoInventario.producto_id == Producto.id)
            .order_by(MovimientoInventario.fecha.desc(), MovimientoInventario.id.desc())
            .limit(limite)
        )
        return [
            {"id": m.id, "fecha": m.fecha, "producto": nombre, "tipo": m.tipo,
             "cantidad": m.cantidad, "motivo": m.motivo or ""}
            for m, nombre in session.execute(consulta)
        ]
