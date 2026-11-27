from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

# Archivo SQLite dentro de data/ (los *.db ya estan en .gitignore)
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "gummy_erp.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# echo=False para no llenar la consola con SQL (cambiar a True para depurar)
engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


# SQLite no valida las ForeignKey a menos que se active en cada conexion
@event.listens_for(Engine, "connect")
def _activar_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def get_session() -> Session:
    return SessionLocal()


def init_db() -> None:
    """Crea las tablas que falten. Nunca borra ni sobrescribe datos existentes."""
    # Se importan aqui para registrar todas las tablas en Base.metadata
    # (importarlas arriba crearia una importacion circular)
    from models import usuario_model
    from models import cliente_model
    from models import producto_model
    from models import venta_model
    from models import detalle_venta_model
    from models import movimiento_model

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(engine)
