"""Carga inicial de datos.

1. Crea los usuarios de prueba (administrador y vendedor) si no hay usuarios.
2. Si la base no tiene productos ni ventas, carga los datos de demostracion
   desde los CSV de data/raw/ (dataset de Olist filtrado por el equipo).

Nunca borra ni modifica datos existentes: solo inserta cuando las tablas estan vacias.
"""
from datetime import datetime
from datetime import timedelta
from pathlib import Path

import pandas as pd
from sqlalchemy import func
from sqlalchemy import select

from models.cliente_model import Cliente
from models.database import get_session
from models.detalle_venta_model import DetalleVenta
from models.movimiento_model import ENTRADA
from models.movimiento_model import SALIDA
from models.movimiento_model import MovimientoInventario
from models.producto_model import Producto
from models.usuario_model import ROL_ADMIN
from models.usuario_model import ROL_VENDEDOR
from models.usuario_model import Usuario
from models.venta_model import Venta
from controllers.auth_controller import generar_hash

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

# Credenciales de prueba (documentadas en el README)
USUARIOS_PRUEBA = [
    {"nombre": "Administrador GUMMY", "usuario": "admin", "correo": "admin@gummy.com",
     "password": "admin123", "rol": ROL_ADMIN},
    {"nombre": "Vendedor GUMMY", "usuario": "vendedor", "correo": "vendedor@gummy.com",
     "password": "vendedor123", "rol": ROL_VENDEDOR},
]

# Traduccion al espanol de las 16 categorias que aparecen en producto.csv
CATEGORIAS_ES = {
    "automotivo": "Automotriz",
    "bebes": "Bebés",
    "bebidas": "Bebidas",
    "beleza_saude": "Belleza y salud",
    "cama_mesa_banho": "Cama, mesa y baño",
    "construcao_ferramentas_construcao": "Herramientas de construcción",
    "eletronicos": "Electrónica",
    "ferramentas_jardim": "Herramientas de jardín",
    "informatica_acessorios": "Accesorios de cómputo",
    "moveis_decoracao": "Muebles y decoración",
    "moveis_escritorio": "Muebles de oficina",
    "moveis_sala": "Muebles de sala",
    "relogios_presentes": "Relojes y regalos",
    "telefonia": "Telefonía",
    "telefonia_fixa": "Telefonía fija",
    "utilidades_domesticas": "Artículos para el hogar",
}


def cargar_datos_iniciales() -> None:
    _crear_usuarios_prueba()
    _cargar_datos_demo()


def _crear_usuarios_prueba() -> None:
    with get_session() as session:
        if session.scalar(select(func.count(Usuario.id))) > 0:
            return
        for datos in USUARIOS_PRUEBA:
            session.add(Usuario(
                nombre=datos["nombre"],
                usuario=datos["usuario"],
                correo=datos["correo"],
                password_hash=generar_hash(datos["password"]),
                rol=datos["rol"],
            ))
        session.commit()


def _cargar_datos_demo() -> None:
    with get_session() as session:
        hay_productos = session.scalar(select(func.count(Producto.id))) > 0
        hay_ventas = session.scalar(select(func.count(DetalleVenta.id))) > 0
        if hay_productos or hay_ventas or not RAW_DIR.exists():
            return

        productos_df = pd.read_csv(RAW_DIR / "producto.csv")
        clientes_df = pd.read_csv(RAW_DIR / "clientes.csv", dtype={"customer_zip_code_prefix": str})
        ventas_df = pd.read_csv(RAW_DIR / "venta.csv", parse_dates=["order_purchase_timestamp"])
        items_df = pd.read_csv(RAW_DIR / "compra.csv")

        # Unidades vendidas por producto: sirve para calcular un stock inicial coherente
        vendidos = items_df.groupby("product_id").size()

        # --- Productos --------------------------------------------------
        productos = {}  # codigo CSV -> objeto Producto
        contador_categoria = {}
        for i, fila in productos_df.iterrows():
            categoria = CATEGORIAS_ES.get(fila["product_category_name"], "Sin categoría")
            contador_categoria[categoria] = contador_categoria.get(categoria, 0) + 1
            producto = Producto(
                nombre=f"{categoria} {contador_categoria[categoria]:02d}",
                categoria=categoria,
                precio=float(fila["price"]),
                stock=0,
                stock_minimo=5,
                codigo_origen=fila["product_id"],
            )
            # Stock inicial = lo que se vendio + un extra variable (algunos quedan bajos)
            producto._stock_inicial = int(vendidos.get(fila["product_id"], 0)) + (i * 7) % 25
            productos[fila["product_id"]] = producto
            session.add(producto)

        # --- Clientes ---------------------------------------------------
        clientes = {}
        for i, fila in clientes_df.iterrows():
            cliente = Cliente(
                nombre=f"Cliente {i + 1:02d}",
                ciudad=str(fila["customer_city"]).title(),
                estado=fila["customer_state"],
                codigo_postal=str(fila["customer_zip_code_prefix"]).zfill(5),
                codigo_origen=fila["customer_id"],
            )
            clientes[fila["customer_id"]] = cliente
            session.add(cliente)
        session.flush()  # asigna los id

        # --- Entradas de inventario iniciales ---------------------------
        fecha_inicial = ventas_df["order_purchase_timestamp"].min() - timedelta(days=7)
        for producto in productos.values():
            producto.stock = producto._stock_inicial
            session.add(MovimientoInventario(
                producto_id=producto.id, tipo=ENTRADA, cantidad=producto._stock_inicial,
                fecha=fecha_inicial.to_pydatetime(), motivo="Inventario inicial",
            ))

        # --- Ventas y sus detalles --------------------------------------
        vendedor = session.scalar(select(Usuario).where(Usuario.rol == ROL_VENDEDOR))
        for _, fila in ventas_df.iterrows():
            fecha = fila["order_purchase_timestamp"].to_pydatetime()
            venta = Venta(
                fecha=fecha,
                cliente_id=clientes[fila["customer_id"]].id,
                usuario_id=vendedor.id if vendedor else None,
            )
            items = items_df[items_df["order_id"] == fila["order_id"]]
            total = 0.0
            # Cada fila de compra.csv es una unidad: se agrupan por producto
            for codigo, cantidad in items.groupby("product_id").size().items():
                producto = productos[codigo]
                subtotal = round(producto.precio * int(cantidad), 2)
                total += subtotal
                venta.detalles.append(DetalleVenta(
                    producto_id=producto.id, cantidad=int(cantidad),
                    precio_unitario=producto.precio, subtotal=subtotal,
                ))
            venta.total = round(total, 2)
            session.add(venta)
            session.flush()
            for detalle in venta.detalles:
                session.add(MovimientoInventario(
                    producto_id=detalle.producto_id, tipo=SALIDA, cantidad=detalle.cantidad,
                    fecha=fecha, motivo=f"Venta #{venta.id}", venta_id=venta.id,
                ))
                session.get(Producto, detalle.producto_id).stock -= detalle.cantidad

        session.commit()
