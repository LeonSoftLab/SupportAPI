import pathlib

BASE_DIR = pathlib.Path(__file__).parent

class Config:
    CONNECT_STRING = "Driver={SQL Server Native Client 11.0};Server=DESKTOP-255RLKB\SQLEXPRESS;Database=support;" \
                     "Trusted_Connection=yes"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "mysecretkey"
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_TIME_MINUTES = 30
    # SQLALCHEMY_ECHO = True
