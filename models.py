from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, Identity
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel


metadata = MetaData()


class TokenModel(BaseModel):
    access_token: str
    token_type: str


class TokenDataModel(BaseModel):
    username: str | None = None


class UserModel(BaseModel):
    username: str
    idemployee: int | None = None
    disabled: bool | None = None


class UserInDBModel(UserModel):
    password: str


class EmployeeModel(BaseModel):
    id: int
    fio: str
    tel: str
    role: str


class LogeventModel(BaseModel):
    id: int
    idemployee: int
    chat_id: int
    datetimestamp: datetime
    event: str
    status: str
    description: str

class GroupModel(BaseModel):
    id: int
    name: str
    description: str
    codename: str


class GrouprowModel(BaseModel):
    id: int
    idgroup: int
    name: str
    commandtext: str
    filename: str


class ReportModel(BaseModel):
    id: int
    name: str
    description: str
    codename: str
    filename: str


class TaskModel(BaseModel):
    id: int
    idemployee: int
    last_context: str
    message_text: str
