import uvicorn
from contextlib import asynccontextmanager
from typing import Annotated, Generator
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from pyodbc import OperationalError
from sqlalchemy.orm import Session

import schemas
import auth
import controllers
from database import SessionLocal, engine, Base

db = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db
    try:
        # TODO: Check connection DB
        pass
    except OperationalError as err:
        print("Database connection error: \n", err)
        raise
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        raise
    yield
    if db is not None:
        pass

app = FastAPI(
    title="Support App",
    lifespan=lifespan
)

# Setting up CORS

# origins = ["*"]
origins = [
    "http://localhost:8080",  # Разрешить CORS для этого источника
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create an object to work with HTTP authorization headers
oauth2_schema = OAuth2PasswordBearer(tokenUrl="login")


# Dependency
async def get_db() -> Generator:
    _db = SessionLocal()
    try:
        yield _db
    finally:
        _db.close()


main_api_router = APIRouter()


@main_api_router.get("/", response_class=HTMLResponse)
async def get_hello():
    return f"""
        <html>
            <head>
                <title>Support App</title>
            </head>
            <body>
                <h2>Hi user! Welcome to the Support App server! The swagger with the APi documentation is at
                    <a href="/docs">/docs</a>
                </h2>
            </body>
        </html>
        """


@main_api_router.get("/testdata")
async def get_testdata():
    _data = [
        {
            "id": 1,
            "createDate": "2023-05-01T08:15:50.000",
            "name": "Тикет 1",
            "status": "Закрыт"
        },
        {
            "id": 2,
            "createDate": "2023-05-15T12:10:35.000",
            "name": "Тикет 2",
            "status": "В работе"
        },
        {
            "id": 3,
            "createDate": "2023-05-25T15:05:25.000",
            "name": "Тикет 3",
            "status": "Открыт"
        }
    ]
    return _data


@app.get("/adminsonly", response_model=list[schemas.UserSchema])
async def get_admins(current_user: Annotated[schemas.UserSchema, Depends(auth.check_admin_user)],
                     session_db: Annotated[Session, Depends(get_db)],
                     ):
    await auth.update_list_users(session_db)
    return [user for user in auth.local_users if user.role.value == "admin"]


@main_api_router.post("/login", response_model=schemas.TokenSchema)
async def login_user_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                      session_db: Annotated[Session, Depends(get_db)]):
    try:
        await auth.update_list_users(session_db)
        user = await auth.authenticate_user(form_data.username, form_data.password)
        if not user:
            raise auth.credentials_exception
        token = schemas.TokenSchema(sub=user.user_name)
        access_token = await auth.create_access_token(token=token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="failed to login - " + str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    return access_token


@main_api_router.post("/registration", response_model=schemas.UserSchema)
async def registration_new_user(body: schemas.UserSchemaCreate, session_db: Annotated[Session, Depends(get_db)]):
    try:
        _user = controllers.UserController(session_db)
        user = _user.create(body)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="failed to create user - " + str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# Users
users_router = APIRouter()


@users_router.get("/", response_model=list[schemas.UserSchema])
async def get_users(current_user: Annotated[schemas.UserSchema, Depends(auth.check_admin_user)],
                    session_db: Annotated[Session, Depends(get_db)],
                    ):
    # TODO: Make handlers for Controllers
    _user_control = controllers.UserController(session_db)
    return _user_control.get()


@users_router.post("/", response_model=schemas.UserSchema)
async def add_user(body: schemas.UserSchemaCreate,
                   current_user: Annotated[schemas.UserSchema, Depends(auth.check_admin_user)],
                   session_db: Annotated[Session, Depends(get_db)],
                   ):
    _user_control = controllers.UserController(session_db)
    return _user_control.create(body)


@users_router.patch("/", response_model=schemas.UserSchemaUpdate)
async def update_user(user_name: str,
                      body: schemas.UserSchemaUpdate,
                      current_user: Annotated[schemas.UserSchema, Depends(auth.check_admin_user)],
                      session_db: Annotated[Session, Depends(get_db)],
                      ):
    updated_user_params = body.model_dump()
    if updated_user_params == {}:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="At least one parameter for user update info should be provided")
    _user_control = controllers.UserController(session_db)
    _users = _user_control.get(user_name)
    if _users is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with name {user_name} not found.")
    updated_user_name = _user_control.update(user_name, **updated_user_params)
    return updated_user_name


@users_router.delete("/", response_model=schemas.UserSchema)
async def delete_user(user_name: str,
                      current_user: Annotated[schemas.UserSchema, Depends(auth.check_admin_user)],
                      session_db: Annotated[Session, Depends(get_db)],
                      ):
    _user_control = controllers.UserController(session_db)
    _users = _user_control.get(user_name)
    if _users is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with name {user_name} not found.")
    return _user_control.delete(user_name)


# Reports
reports_router = APIRouter()


@reports_router.get("/", response_model=list[schemas.ReportSchema])
async def get_reports(current_user: Annotated[schemas.UserSchema, Depends(auth.check_active_user)],
                      session_db: Annotated[Session, Depends(get_db)],
                      ):
    # TODO: Make handlers for Controllers
    _report_control = controllers.ReportController(session_db)
    return _report_control.get()


@reports_router.post("/", response_model=schemas.ReportSchema)
async def add_report(body: schemas.ReportSchemaCreate,
                     current_user: Annotated[schemas.UserSchema, Depends(auth.check_active_user)],
                     session_db: Annotated[Session, Depends(get_db)],
                     ):
    _report_control = controllers.ReportController(session_db)
    return _report_control.create(body)


@reports_router.get("/{code_name}", response_model=schemas.ReportSchema)
async def get_report(code_name: str,
                     current_user: Annotated[schemas.UserSchema, Depends(auth.check_active_user)],
                     session_db: Annotated[Session, Depends(get_db)],
                     ):
    _report_control = controllers.ReportController(session_db)
    _reports = _report_control.get(code_name=code_name)
    if _reports is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Report with code_name {code_name} not found.")
    return _reports


@reports_router.patch("/", response_model=schemas.ReportSchema)
async def update_report(_id: int,
                        body: schemas.ReportSchemaUpdate,
                        current_user: Annotated[schemas.UserSchema, Depends(auth.check_active_user)],
                        session_db: Annotated[Session, Depends(get_db)],
                        ):
    updated_report_params = body.model_dump()
    if updated_report_params == {}:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="At least one parameter for report update info should be provided")
    _report_control = controllers.ReportController(session_db)
    _reports = _report_control.get(_id=_id)
    if _reports is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Report with _id {str(_id)} not found.")
    return _report_control.update(_id, **updated_report_params)


@reports_router.delete("/", response_model=schemas.ReportSchema)
async def delete_report(_id: int,
                        current_user: Annotated[schemas.UserSchema, Depends(auth.check_active_user)],
                        session_db: Annotated[Session, Depends(get_db)],
                        ):
    _report_control = controllers.ReportController(session_db)
    _reports = _report_control.get(_id=_id)
    if _reports is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Report with _id {str(_id)} not found.")
    return _report_control.delete(_id=_id)


# Groups
groups_router = APIRouter()


@groups_router.get("/", response_model=list[schemas.GroupSchema])
async def get_groups(current_user: Annotated[schemas.UserSchema, Depends(auth.check_active_user)],
                     session_db: Annotated[Session, Depends(get_db)],
                     ):
    # TODO: Make handlers for Controllers
    _group_control = controllers.GroupController(session_db)
    return _group_control.get()


@groups_router.post("/", response_model=schemas.GroupSchema)
async def add_group(body: schemas.GroupSchemaCreate,
                    current_user: Annotated[schemas.UserSchema, Depends(auth.check_active_user)],
                    session_db: Annotated[Session, Depends(get_db)],
                    ):
    _group_control = controllers.GroupController(session_db)
    return _group_control.create(body)


@groups_router.get("/{code_name}", response_model=schemas.GroupSchema)
async def get_group(code_name: str,
                    current_user: Annotated[schemas.UserSchema, Depends(auth.check_active_user)],
                    session_db: Annotated[Session, Depends(get_db)],
                    ):
    _group_control = controllers.GroupController(session_db)
    _groups = _group_control.get(code_name=code_name)
    if _groups is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Group with code_name {code_name} not found.")
    return _groups


@groups_router.patch("/", response_model=schemas.GroupSchema)
async def update_group(_id: int,
                       body: schemas.GroupSchemaUpdate,
                       current_user: Annotated[schemas.UserSchema, Depends(auth.check_active_user)],
                       session_db: Annotated[Session, Depends(get_db)],
                       ):
    updated_group_params = body.model_dump()
    if updated_group_params == {}:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="At least one parameter for group update info should be provided")
    _group_control = controllers.GroupController(session_db)
    _groups = _group_control.get(_id=_id)
    if _groups is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Group with _id {str(_id)} not found.")
    return _group_control.update(_id, **updated_group_params)


@groups_router.delete("/", response_model=schemas.GroupSchema)
async def delete_group(_id: int,
                        current_user: Annotated[schemas.UserSchema, Depends(auth.check_active_user)],
                        session_db: Annotated[Session, Depends(get_db)],
                        ):
    _group_control = controllers.GroupController(session_db)
    _groups = _group_control.get(_id=_id)
    if _groups is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Group with _id {str(_id)} not found.")
    return _group_control.delete(_id=_id)


# Group_rows
group_rows_router = APIRouter()


@group_rows_router.get("/", response_model=list[schemas.GroupRowSchema])
async def get_group_rows(id_group: int,
                         current_user: Annotated[schemas.UserSchema, Depends(auth.check_active_user)],
                         session_db: Annotated[Session, Depends(get_db)],
                         ):
    # TODO: Make handlers for Controllers
    _group_row_control = controllers.GroupRowController(session_db)
    return _group_row_control.get(id_group=id_group)


@group_rows_router.post("/", response_model=schemas.GroupRowSchema)
async def add_group_row(body: schemas.GroupRowSchemaCreate,
                        current_user: Annotated[schemas.UserSchema, Depends(auth.check_active_user)],
                        session_db: Annotated[Session, Depends(get_db)],
                        ):
    _group_row_control = controllers.GroupRowController(session_db)
    return _group_row_control.create(body)


@group_rows_router.get("/{command_text}", response_model=schemas.GroupRowSchema)
async def get_group_row(command_text: str,
                        current_user: Annotated[schemas.UserSchema, Depends(auth.check_active_user)],
                        session_db: Annotated[Session, Depends(get_db)],
                        ):
    _group_row_control = controllers.GroupRowController(session_db)
    _group_rows = _group_row_control.get(command_text=command_text)
    if _group_rows is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Group with command_text {command_text} not found.")
    return _group_rows


@group_rows_router.patch("/", response_model=schemas.GroupRowSchema)
async def update_group_row(_id: int,
                           body: schemas.GroupRowSchemaUpdate,
                           current_user: Annotated[schemas.UserSchema, Depends(auth.check_active_user)],
                           session_db: Annotated[Session, Depends(get_db)],
                           ):
    updated_group_row_params = body.model_dump()
    if updated_group_row_params == {}:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="At least one parameter for grouprow update info should be provided")
    _group_row_control = controllers.GroupRowController(session_db)
    _group_rows = _group_row_control.get(_id=_id)
    if _group_rows is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Grouprow with _id {str(_id)} not found.")
    return _group_row_control.update(_id, **updated_group_row_params)


@group_rows_router.delete("/", response_model=schemas.GroupRowSchema)
async def delete_group_row(_id: int,
                           current_user: Annotated[schemas.UserSchema, Depends(auth.check_active_user)],
                           session_db: Annotated[Session, Depends(get_db)],
                           ):
    _group_row_control = controllers.GroupRowController(session_db)
    _group_rows = _group_row_control.get(_id=_id)
    if _group_rows is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Grouprow with _id {str(_id)} not found.")
    return _group_row_control.delete(_id=_id)


# Tasks
tasks_router = APIRouter()


@tasks_router.get("/", response_model=list[schemas.TaskSchema])
async def get_tasks(id_employee: int,
                    current_user: Annotated[schemas.UserSchema, Depends(auth.check_active_user)],
                    session_db: Annotated[Session, Depends(get_db)],
                    limit: int = 1, offset: int = 0,
                    ):
    # TODO: Make handlers for Controllers
    _task_control = controllers.TaskController(session_db)
    _tasks = _task_control.get(id_employee=id_employee)
    if _tasks is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Tasks with id_employee {id_employee} not found.")
    return [task for task in _tasks[offset:][:limit]]


@tasks_router.get("/{_id}", response_model=schemas.TaskSchema)
async def get_task(_id: int,
                   current_user: Annotated[schemas.UserSchema, Depends(auth.check_active_user)],
                   session_db: Annotated[Session, Depends(get_db)],
                   ):
    _task_control = controllers.TaskController(session_db)
    _tasks = _task_control.get(_id=_id)
    if _tasks is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Task with _id {_id} not found.")
    return _tasks


main_api_router.include_router(users_router, prefix="/users", tags=["Users"])
main_api_router.include_router(reports_router, prefix="/reports", tags=["Reports"])
main_api_router.include_router(groups_router, prefix="/groups", tags=["Groups"])
main_api_router.include_router(group_rows_router, prefix="/group_rows", tags=["Grouprows"])
main_api_router.include_router(tasks_router, prefix="/tasks", tags=["Tasks"])
app.include_router(main_api_router)

if __name__ == "__main__":
    # run app on the host and port
    uvicorn.run(app, host="127.0.0.1", port=8000)
