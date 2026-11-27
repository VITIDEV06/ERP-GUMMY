"""Controlador de productos: registrar, consultar, editar y eliminar."""
from sqlalchemy import func
from sqlalchemy import or_
from sqlalchemy import select

from models.database import get_session
from models.detalle_venta_model import DetalleVenta
from models.movimiento_model import ENTRADA
from models.movimiento_model import SALIDA
from models.movimiento_model import MovimientoInventario
from models.producto_model import Producto


def _a_dict(p: Producto) -> dict:
    return {
        "id": p.id,
        "nombre": p.nombre,
        "categoria": p.categoria or "Sin categoría",
        "precio": p.precio,
        "stock": p.stock,
        "stock_minimo": p.stock_minimo,
        "bajo_stock": p.bajo_stock(),
    }


def listar_productos(busqueda: str = "") -> list[dict]:
    with get_session() as session:
        consulta = select(Producto).order_by(Producto.nombre)
        if busqueda:
            patron = f"%{busqueda.strip()}%"
            consulta = consulta.where(or_(Producto.nombre.ilike(patron), Producto.categoria.ilike(patron)))
        return [_a_dict(p) for p in session.scalars(consulta)]


def listar_categorias() -> list[str]:
    with get_session() as session:
        consulta = select(Producto.categoria).where(Producto.categoria.is_not(None)).distinct()
        return sorted(session.scalars(consulta))


def validar_datos(datos: dict):
    """Convierte y valida los datos del formulario. Devuelve (datos_limpios, error)."""
    nombre = (datos.get("nombre") or "").strip()
    if not nombre:
        return None, "El nombre es obligatorio."
    try:
        precio = float(str(datos.get("precio", "")).replace(",", "."))
        stock = int(datos.get("stock") or 0)
        stock_minimo = int(datos.get("stock_minimo") or 0)
    except ValueError:
        return None, "Precio y cantidades deben ser números."
    if precio <= 0:
        return None, "El precio debe ser mayor que cero."
    if stock < 0 or stock_minimo < 0:
        return None, "Las cantidades no pueden ser negativas."
    categoria = (datos.get("categoria") or "").strip() or None
    return {"nombre": nombre, "categoria": categoria, "precio": round(precio, 2),
            "stock": stock, "stock_minimo": stock_minimo}, None


def crear_producto(datos: dict):
    """Devuelve (True, mensaje) o (False, error)."""
    limpios, error = validar_datos(datos)
    if error:
        return False, error
    with get_session() as session:
        producto = Producto(**limpios)
        session.add(producto)
        session.flush()
        # La cantidad inicial queda registrada como una entrada de inventario
        if producto.stock > 0:
            session.add(MovimientoInventario(producto_id=producto.id, tipo=ENTRADA,
                                             cantidad=producto.stock, motivo="Alta de producto"))
        session.commit()
    return True, "Producto registrado."


def actualizar_producto(producto_id: int, datos: dict):
    limpios, error = validar_datos(datos)
    if error:
        return False, error
    with get_session() as session:
        producto = session.get(Producto, producto_id)
        if producto is None:
            return False, "El producto no existe."
        diferencia = limpios["stock"] - producto.stock
        for campo, valor in limpios.items():
            setattr(producto, campo, valor)
        # Si se cambio la cantidad a mano se registra un ajuste para no perder el historial
        if diferencia != 0:
            session.add(MovimientoInventario(
                producto_id=producto.id, tipo=ENTRADA if diferencia > 0 else SALIDA,
                cantidad=abs(diferencia), motivo="Ajuste desde Productos"))
        session.commit()
    return True, "Producto actualizado."


def eliminar_producto(producto_id: int):
    with get_session() as session:
        producto = session.get(Producto, producto_id)
        if producto is None:
            return False, "El producto no existe."
        ventas = session.scalar(select(func.count(DetalleVenta.id)).where(DetalleVenta.producto_id == producto_id))
        if ventas:
            return False, "No se puede eliminar: el producto aparece en ventas registradas."
        # Sus movimientos de inventario se eliminan junto con el producto
        for mov in session.scalars(select(MovimientoInventario).where(MovimientoInventario.producto_id == producto_id)):
            session.delete(mov)
        session.delete(producto)
        session.commit()
    return True, "Producto eliminado."
