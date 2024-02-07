from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

import schemas
import controllers
from config import Config


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_schema = OAuth2PasswordBearer(tokenUrl="login")

# Updated in the main unit when the login_for_access_token function is called
local_users: list[schemas.UserSchema]

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials, Possibly incorrect login or password, also check your account",
    headers={"WWW-Authenticate": "Bearer"},
)

access_exception = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access this route",
            headers={"WWW-Authenticate": "Bearer"},
        )

token_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def create_access_token(token: schemas.TokenSchema) -> schemas.TokenSchema:
    """Generate JWT token"""
    try:
        token.exp = datetime.utcnow() + timedelta(minutes=Config.JWT_EXPIRATION_TIME_MINUTES)
        to_encode = {"sub": token.sub, "exp": token.exp}
        token.access_token = jwt.encode(to_encode, key=Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM)
        token.token_type = "Bearer"
        return token
    except Exception as e:
        print(str(e))
        raise token_exception


async def verify_password(plain_password, hashed_password):
    """Password hash matching function"""
    return pwd_context.verify(plain_password, hashed_password)


async def get_password_hash(password):
    return pwd_context.hash(password)


async def verify_token(token) -> dict:
    try:
        payload = jwt.decode(token, key=Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
        return payload
    except Exception as e:
        raise token_exception


async def _get_user(user_name: str):
    """Function to get user from database"""
    for user in local_users:
        if user.user_name == user_name:
            return user
    return None


async def authenticate_user(user_name: str, password: str):
    user = await _get_user(user_name)
    if not user:
        return False
    if not await verify_password(password, user.hashed_password):
        return False
    return user


async def check_current_user(token: Annotated[str, Depends(oauth2_schema)]) -> schemas.UserSchema:
    try:
        payload = await verify_token(token)
        user_name: str = payload.get("sub")
        if user_name is None:
            raise credentials_exception
    except Exception as e:
        raise credentials_exception
    user = await _get_user(user_name)
    if not user:
        raise credentials_exception
    return user


async def check_active_user(current_user: Annotated[schemas.UserSchema, Depends(check_current_user)]) -> schemas.UserSchema:
    if current_user.disabled:
        raise credentials_exception
    else:
        return current_user


async def check_admin_user(current_user: Annotated[schemas.UserSchema, Depends(check_active_user)]) -> schemas.UserSchema:
    if current_user.role.value != "admin":
        raise access_exception
    else:
        return current_user


async def update_list_users(session_db):
    global local_users
    _user = controllers.UserController(session_db)
    local_users = _user.get()
