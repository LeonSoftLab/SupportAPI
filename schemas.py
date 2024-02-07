import re

from fastapi import HTTPException, status
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, field_validator, ConfigDict, constr

LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")

validator_exception = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail="user_name should contains only letters",
    headers={"WWW-Authenticate": "Bearer"},
)


class RoleSchema(Enum):
    model_config = ConfigDict(from_attributes=True)
    user = "user"
    admin = "admin"


class TokenSchema(BaseModel):
    sub: str
    exp: datetime | None = None
    access_token: str | None = None
    token_type: str | None = None


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_name: str
    disabled: bool = False
    role: RoleSchema = "user"
    hashed_password: str = ""


class UserSchemaInDB(UserSchema):
    id_employee: int = 0


class UserSchemaUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_employee: int | None
    disabled: bool | None
    role: RoleSchema | None = "user"
    password: constr(min_length=1) | None


class UserSchemaCreate(BaseModel):
    user_name: str
    password: str

    @field_validator("user_name")
    def validate_name(cls, value: str) -> str:
        if not LETTER_MATCH_PATTERN.match(value):
            raise validator_exception
        return value


class EmployeeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    fio: str
    tel: str
    dept: str | None = ""


class EmployeeSchemaCreate(BaseModel):
    fio: str
    tel: str
    dept: str | None = ""


class GroupSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str
    code_name: str


class GroupSchemaCreate(BaseModel):
    name: str
    description: str
    code_name: str


class GroupSchemaUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str | None
    description: str | None
    code_name: str | None


class GroupRowSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    id_group: int
    name: str
    command_text: str
    file_name: str


class GroupRowSchemaCreate(BaseModel):
    id_group: int
    name: str
    command_text: str
    file_name: str


class GroupRowSchemaUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_group: int | None
    description: str | None
    code_name: str | None


class ReportSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str
    code_name: str
    file_name: str


class ReportSchemaCreate(BaseModel):
    name: str
    description: str
    code_name: str
    file_name: str


class ReportSchemaUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str | None
    description: str | None
    code_name: str | None
    file_name: str | None


class TaskSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    id_employee: int
    last_context: str
    message_text: str


class TaskSchemaCreate(BaseModel):
    id_employee: int
    last_context: str
    message_text: str


class TaskSchemaUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_employee: int | None
    last_context: str | None
    message_text: str | None

