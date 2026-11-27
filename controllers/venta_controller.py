"""Controlador de ventas: registra ventas con varios productos y descuenta el inventario."""
from sqlalchemy import select

from models.cliente_model import Cliente
from models.database import get_session
from models.detalle_venta_model import DetalleVenta
from models.movimiento_model import SALIDA
from models.movimiento_model import MovimientoInventario
from models.producto_model import Producto
from models.usuario_model import Usuario
from models.venta_model import Venta


def calcular_total(items: list[dict]) -> float:
    """items: [{"precio": 10.0, "cantidad": 2}, ...]"""
    return round(sum(i["precio"] * i["cantidad"] for i in items), 2)


def registrar_venta(items: list[dict], cliente_id=None, usuario_id=None):
    """Registra la venta en una sola transaccion.

    items: lista de {"producto_id": int, "cantidad": int}
    Devuelve (True, mensaje) o (False, error).
    """
    if not items:
        return False, "Agrega al menos un producto a la venta."

    with get_session() as session:
        venta = Venta(cliente_id=cliente_id or None, usuario_id=usuario_id)
        total = 0.0
        for item in items:
            producto = session.get(Producto, item["producto_id"])
            cantidad = int(item["cantidad"])
            if producto is None:
                return False, "Uno de los productos ya no existe."
            if cantidad <= 0:
                return False, "Las cantidades deben ser mayores que cero."
            if cantidad > producto.stock:
                # return sin commit: la sesion se cierra y no se guarda nada
                return False, f"Stock insuficiente de {producto.nombre} (disponible: {producto.stock})."

            subtotal = round(producto.precio * cantidad, 2)
            total += subtotal
            venta.detalles.append(DetalleVenta(
                producto_id=producto.id, cantidad=cantidad,
                precio_unitario=producto.precio, subtotal=subtotal,
            ))
            # Descuento automatico del inventario
            producto.stock -= cantidad

        venta.total = round(total, 2)
        session.add(venta)
        session.flush()  # para conocer venta.id

        for detalle in venta.detalles:
            session.add(MovimientoInventario(
                producto_id=detalle.producto_id, tipo=SALIDA, cantidad=detalle.cantidad,
                fecha=venta.fecha, motivo=f"Venta #{venta.id}", venta_id=venta.id,
            ))
        session.commit()
        return True, f"Venta #{venta.id} registrada por ${venta.total:,.2f}."


def listar_ventas(limite: int = 300) -> list[dict]:
    with get_session() as session:
        consulta = (
            select(Venta, Cliente.nombre, Usuario.nombre)
            .outerjoin(Cliente, Venta.cliente_id == Cliente.id)
            .outerjoin(Usuario, Venta.usuario_id == Usuario.id)
            .order_by(Venta.fecha.desc())
            .limit(limite)
        )
        return [
            {"id": v.id, "fecha": v.fecha, "cliente": cliente or "Público general",
             "vendedor": vendedor or "-", "total": v.total, "productos": len(v.detalles)}
            for v, cliente, vendedor in session.execute(consulta)
        ]


def detalle_de_venta(venta_id: int) -> list[dict]:
    with get_session() as session:
        consulta = (
            select(DetalleVenta, Producto.nombre)
            .join(Producto, DetalleVenta.producto_id == Producto.id)
            .where(DetalleVenta.venta_id == venta_id)
        )
        return [
            {"producto": nombre, "cantidad": d.cantidad, "precio": d.precio_unitario, "subtotal": d.subtotal}
            for d, nombre in session.execute(consulta)
        ]
