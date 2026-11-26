from sqlalchemy import create_engine
engine = create_engine("sqlite://", echo=True)

#Creado boilerplate para creación del engine de la base de datos