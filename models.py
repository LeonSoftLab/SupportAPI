from sqlalchemy import (
    Integer,
    Table,
    Enum,
    String,
    TIMESTAMP,
    ForeignKey,
    JSON,
    Boolean,
    MetaData,
    Identity,
)
from sqlalchemy.orm import DeclarativeBase, relationship, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs

from schemas import RoleSchema

metadata = MetaData()


class Base(AsyncAttrs, DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"

    user_name = mapped_column(String(15), primary_key=True, autoincrement=False)
    id_employee = mapped_column(Integer, nullable=False)
    disabled = mapped_column(Boolean, default=True, nullable=False)
    password = mapped_column(String(255), nullable=False)
    role = mapped_column(Enum(RoleSchema), default="user", nullable=False)


class ReportModel(Base):
    __tablename__ = "reports"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)  # Identity(start=1, increment=1)
    name = mapped_column(String(50), nullable=False)
    description = mapped_column(String(255), nullable=False)
    code_name = mapped_column(String(50), nullable=False)
    file_name = mapped_column(String(255), nullable=False)


class GroupModel(Base):
    __tablename__ = "groups"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)  # Identity(start=1, increment=1)
    name = mapped_column(String(50), nullable=False)
    description = mapped_column(String(255), nullable=False)
    code_name = mapped_column(String(50), nullable=False)

    rows = relationship('GroupRowModel', back_populates='group')


class GroupRowModel(Base):
    __tablename__ = "group_rows"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)  # Identity(start=1, increment=1)
    id_group = mapped_column(Integer, ForeignKey('groups.id'), nullable=False)
    name = mapped_column(String(255), nullable=False)
    command_text = mapped_column(String(50), nullable=False)
    file_name = mapped_column(String(255), nullable=False)

    group = relationship('GroupModel', back_populates='rows')


class TaskModel(Base):
    __tablename__ = "dh_tasks"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)  # Identity(start=1, increment=1)
    id_employee = mapped_column(Integer, ForeignKey('employees.id'), nullable=False)
    last_context = mapped_column(String(50), nullable=False)
    message_text = mapped_column(String(255), nullable=False)

    #employee = relationship('EmployeeModel', back_populates='tasks')
