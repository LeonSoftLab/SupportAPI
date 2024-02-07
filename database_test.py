import asyncio
import os
from typing import Any
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

import aioodbc

import pytest
from starlette.testclient import TestClient

from db.session import get_db
from main import app


CLEAN_TABLES = [
    "users",
]

# DATABASE CONFIG
DB_DRIVER = "ODBC Driver 11 for SQL Server"
DB_HOST = "DESKTOP-255RLKB\SQLEXPRESS"
DB_DATABASE = "support_test"
SQLALCHEMY_TEST_DATABASE_URL = f"mssql+pyodbc://@{DB_HOST}/{DB_DATABASE}?&driver={DB_DRIVER}"

# create engine for interaction with database
test_engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, echo=True)
# create session for the interaction with database
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

CLEAN_TABLES = [
    "users",
]


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def run_migrations():
    os.system("alembic init migrations")
    os.system('alembic revision --autogenerate -m "test running migrations"')
    os.system("alembic upgrade heads")


@pytest.fixture(scope="session")
async def async_session_test():
    engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, echo=True)
    session = sessionmaker(engine, expire_on_commit=False, autocommit=False, autoflush=False)
    yield session


@pytest.fixture(scope="function", autouse=True)
async def clean_tables(async_session_test):
    """Clean data in all tables before running test function"""
    async with async_session_test() as session:
        async with session.begin():
            for table_for_cleaning in CLEAN_TABLES:
                await session.execute(f"""TRUNCATE TABLE {table_for_cleaning};""")


async def _get_test_db():
    try:
        # create engine for interaction with database
        test_engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, echo=True)

        # create session for the interaction with database
        test_session = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
        yield test_session()
    finally:
        pass


@pytest.fixture(scope="function")
async def client() -> Generator[TestClient, Any, None]:
    """
    Create a new FastAPI TestClient that uses the `db_session` fixture to override
    the `get_db` dependency that is injected into routes.
    """

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as client:
        yield client


@pytest.fixture
async def get_user_from_database(pool):
    async def get_user_from_database_by_name(user_name: str):
        async with pool.acquire() as connection:
            return await connection.fetch(
                """SELECT * FROM users WHERE user_name = $1;""", user_name
            )

    return get_user_from_database_by_name


@pytest.fixture(scope="session")
async def aioodbc_pool():
    pool = await aioodbc.create_pool(SQLALCHEMY_TEST_DATABASE_URL)
    yield pool
    pool.close()
