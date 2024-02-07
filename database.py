from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# DATABASE CONFIG
DB_DRIVER = "ODBC Driver 11 for SQL Server"
DB_HOST = "DESKTOP-255RLKB\SQLEXPRESS"
DB_DATABASE = "support"
SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc://@{DB_HOST}/{DB_DATABASE}?&driver={DB_DRIVER}"

# create engine for interaction with database
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
# json_serializer=lambda x: x
# create session for the interaction with database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
Base = declarative_base()
