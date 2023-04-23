from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, Identity
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


metadata = MetaData()


# Класс для данных токена
class TokenDataModel(BaseModel):
    username: str
    exp: datetime


# Класс для запроса на аутентификации
class LoginRequestModel(BaseModel):
    username: str
    password: str


users = Table(
    "users",
    metadata,
    Column("username", String(15), primary_key=True),
    Column("idemployee", Integer, nullable=False),
    Column("password", String(255), nullable=False),
)


class UserModel(BaseModel):
    username: str
    idemployee: int
    password: str


employees = Table(
    "employees",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("fio", String(50), nullable=False),
    Column("tel", String(15), nullable=False),
    Column("role", String(15), nullable=False),
)


class EmployeeModel(BaseModel):
    id: int
    fio: str
    tel: str
    role: str


logevents = Table(
    "logevents",
    metadata,
    Column("id", Integer, Identity(start=1, increment=1), primary_key=True),
    Column("idemployee", Integer, nullable=False),
    Column("chat_id", Integer, nullable=False),
    Column("datetimestamp", TIMESTAMP, default=datetime.utcnow),
    Column("event", String(255), nullable=False),
    Column("status", String(255), nullable=False),
    Column("description", String(4000), nullable=False),
)


class LogeventModel(BaseModel):
    id: int
    idemployee: int
    chat_id: int
    datetimestamp: datetime
    event: str
    status: str
    description: str


groups = Table(
    "groups",
    metadata,
    Column("id", Integer, Identity(start=1, increment=1), primary_key=True),
    Column("name", String, nullable=False),
    Column("description", String, nullable=False),
    Column("codename", String, nullable=False),
)


class GroupModel(BaseModel):
    id: int
    name: str
    description: str
    codename: str


grouprows = Table(
    "grouprows",
    metadata,
    Column("id", Integer, Identity(start=1, increment=1), primary_key=True),
    Column("idgroup", Integer, ForeignKey("groups.id")),
    Column("name", String(255), nullable=False),
    Column("commandtext", String(50), nullable=False),
    Column("filename", String(255), nullable=False),
)


class GrouprowModel(BaseModel):
    id: int
    idgroup: int
    name: str
    commandtext: str
    filename: str


reports = Table(
    "reports",
    metadata,
    Column("id", Integer, Identity(start=1, increment=1), primary_key=True),
    Column("name", String(50), nullable=False),
    Column("description", String(255), nullable=False),
    Column("codename", String(50), nullable=False),
    Column("filename", String(50), nullable=False),
)


class ReportModel(BaseModel):
    id: int
    name: str
    description: str
    codename: str
    filename: str


Tasks = Table(
    "dh_tasks",
    metadata,
    Column("id", Integer, Identity(start=1, increment=1), primary_key=True),
    Column("idemployee", Integer, nullable=False),
    Column("last_context", String(50), nullable=False),
    Column("message_text", String(255), nullable=False),
)


class TaskModel(BaseModel):
    id: int
    idemployee: int
    last_context: str
    message_text: str
