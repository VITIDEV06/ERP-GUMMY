"""Controlador de clientes: registrar, consultar, editar y eliminar."""
from sqlalchemy import func
from sqlalchemy import or_
from sqlalchemy import select

from models.cliente_model import Cliente
from models.database import get_session
from models.venta_model import Venta

CAMPOS = ("nombre", "telefono", "correo", "ciudad", "estado")


def listar_clientes(busqueda: str = "") -> list[dict]:
    with get_session() as session:
        # Se cuenta cuantas compras tiene cada cliente
        consulta = (
            select(Cliente, func.count(Venta.id))
            .outerjoin(Venta, Venta.cliente_id == Cliente.id)
            .group_by(Cliente.id)
            .order_by(Cliente.nombre)
        )
        if busqueda:
            patron = f"%{busqueda.strip()}%"
            consulta = consulta.where(or_(Cliente.nombre.ilike(patron), Cliente.ciudad.ilike(patron),
                                          Cliente.correo.ilike(patron)))
        return [
            {"id": c.id, "nombre": c.nombre, "telefono": c.telefono or "", "correo": c.correo or "",
             "ciudad": c.ciudad or "", "estado": c.estado or "", "compras": compras}
            for c, compras in session.execute(consulta)
        ]


def _validar(datos: dict):
    limpios = {campo: (datos.get(campo) or "").strip() or None for campo in CAMPOS}
    if not limpios["nombre"]:
        return None, "El nombre es obligatorio."
    if limpios["correo"] and "@" not in limpios["correo"]:
        return None, "El correo no es válido."
    return limpios, None


def crear_cliente(datos: dict):
    limpios, error = _validar(datos)
    if error:
        return False, error
    with get_session() as session:
        session.add(Cliente(**limpios))
        session.commit()
    return True, "Cliente registrado."


def actualizar_cliente(cliente_id: int, datos: dict):
    limpios, error = _validar(datos)
    if error:
        return False, error
    with get_session() as session:
        cliente = session.get(Cliente, cliente_id)
        if cliente is None:
            return False, "El cliente no existe."
        for campo, valor in limpios.items():
            setattr(cliente, campo, valor)
        session.commit()
    return True, "Cliente actualizado."


def eliminar_cliente(cliente_id: int):
    with get_session() as session:
        cliente = session.get(Cliente, cliente_id)
        if cliente is None:
            return False, "El cliente no existe."
        ventas = session.scalar(select(func.count(Venta.id)).where(Venta.cliente_id == cliente_id))
        if ventas:
            return False, f"No se puede eliminar: el cliente tiene {ventas} venta(s) registradas."
        session.delete(cliente)
        session.commit()
    return True, "Cliente eliminado."
