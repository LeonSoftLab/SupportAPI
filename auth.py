import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_TIME_MINUTES
import models


# Генерируем JWT-токен
def create_jwt_token(token_data: models.TokenDataModel) -> str:
    to_encode = token_data.dict()
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_TIME_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


# Функция проверки пароля
def verify_password(plain_password, hashed_password):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)


# Функция получения пользователя из базы данных
def get_user(username: str):
    users = [{"username": "leon", "idemployee": 1, "password": "$2b$12$M9tSeWFEHh.cIawXpNhlp.AuJi82D5w4BYiED/Um3DfTNC4yr91zy"},
             {"username": "qwerty", "idemployee": 2, "password": "$2b$12$MgzRp/BgsJ57swyDD9Jy0OpBtl0gPczEZkFQIZs0ZCISi1hvvDm.K"}]
    for user in users:
        if user["username"] == username:
            return user
    return None


# Функция аутентификации пользователя
def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user["password"]):
        return False
    return user
