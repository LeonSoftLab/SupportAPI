from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import APIRouter
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
from pyodbc import OperationalError
import jwt
from config import Config
import mssqlworker
import models
import auth

app = FastAPI(
    title="Support App"
)

# Настройка CORS

#origins = ["*"]
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

db = None

# Создаем объект для работы с HTTP-заголовками авторизации
oauth2_schema = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(token: Annotated[str, Depends(oauth2_schema)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = models.TokenDataModel(username=username)
    except Exception as e:
        raise credentials_exception
    user = auth.get_user(mssqlworker.fakeusers, username=token_data.username)
    if not user:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[models.UserModel, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.on_event("startup")
def startup():
    global db
    try:
        # Создаём обьект для работы с базой данных
        db = mssqlworker.MssqlWorker()
    except OperationalError as err:
        print("Database connection error: \n", err)
        raise
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        raise


@app.get("/")
def get_hello():
    return 'Hi user! Welcome to the Support App server! The swagger with the APi documentation is at "/docs"'


@app.get("/testdata")
def get_testdata():
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


# Аутентификация пользователя
@app.post("/login")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = auth.authenticate_user(mssqlworker.fakeusers, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Reports
router_reports = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


@router_reports.get("/", response_model=list[models.ReportModel])
async def get_reports(current_user: Annotated[models.UserModel, Depends(get_current_active_user)]):
    reports = db.get_reports(username=current_user.username)
    return [report for report in reports]


@router_reports.post("/")
def add_reports(current_user: Annotated[models.UserModel, Depends(get_current_active_user)],
                reports: list[models.ReportModel]):
    return {"status": 200, "data": reports}


@router_reports.get("/{report_code}", response_model=models.ReportModel)
async def get_report(current_user: Annotated[models.UserModel, Depends(get_current_active_user)],
                     report_code: str):
    reports = db.get_reports(username=current_user.username, codename=report_code)
    return [report for report in reports]


@router_reports.put("/{report_code}", response_model=models.ReportModel)
async def change_report(current_user: Annotated[models.UserModel, Depends(get_current_active_user)],
                        report_code: str,
                        report: models.ReportModel):
    current_report = db.get_reports(username=current_user.username, codename=report_code)[0]
    # TODO: update to db report
    return {"status": 200, "data": current_report}


@router_reports.delete("/{report_code}", response_model=models.ReportModel)
async def delete_report(current_user: Annotated[models.UserModel, Depends(get_current_active_user)],
                        report_code: str):
    current_report = db.get_reports(username=current_user.username, codename=report_code)[0]
    # TODO: delete
    return {"status": 200, "data": current_report}

# Groups
router_groups = APIRouter(
    prefix="/groups",
    tags=["Groups"]
)


@router_groups.get("/", response_model=list[models.GroupModel])
def get_groups(current_user: Annotated[models.UserModel, Depends(get_current_active_user)]):
    groups = db.get_groups()
    return [group for group in groups]


@router_groups.post("/", response_model=list[models.GroupModel])
def add_groups(current_user: Annotated[models.UserModel, Depends(get_current_active_user)],
               groups: list[models.GroupModel]):
    # TODO: add new groups
    return {"status": 200, "data": groups}


@router_groups.get("/{group_id}", response_model=models.GroupModel)
def get_group(current_user: Annotated[models.UserModel, Depends(get_current_active_user)],
              group_id: int):
    groups = db.get_groups()
    return [group for group in groups if group[0] == group_id]


@router_groups.put("/{group_id}", response_model=models.GroupModel)
def change_group(current_user: Annotated[models.UserModel, Depends(get_current_active_user)],
                 group_id: int,
                 group: models.GroupModel):
    groups = db.get_groups()
    group_curr = [group for group in groups if group[0] == group_id]
    # TODO: update to db group
    return group_curr


@router_groups.delete("/{group_id}", response_model=models.GroupModel)
def delete_group(current_user: Annotated[models.UserModel, Depends(get_current_active_user)],
                 group_id: int):
    groups = db.get_groups()
    group_curr = [group for group in groups if group[0] == group_id]
    # TODO: delete
    return group_curr


# Grouprows
router_grouprows = APIRouter(
    prefix="/grouprows",
    tags=["Grouprows"]
)


@router_grouprows.get("/", response_model=list[models.GrouprowModel])
def get_grouprows(current_user: Annotated[models.UserModel, Depends(get_current_active_user)],
                  idgroup: int):
    grouprows = db.get_grouprows(idgroup=idgroup)
    return [grouprow for grouprow in grouprows]


@router_grouprows.post("/", response_model=list[models.GrouprowModel])
def add_grouprows(current_user: Annotated[models.UserModel, Depends(get_current_active_user)],
                  idgroup: int,
                  grouprows: list[models.GrouprowModel]):
    # TODO: add to db
    return {"status": 200, "data": grouprows}


@router_grouprows.put("/{grouprow_id}", response_model=models.GrouprowModel)
def change_grouprow(current_user: Annotated[models.UserModel, Depends(get_current_active_user)],
                    grouprow_id: int,
                    grouprow: models.GrouprowModel):
    # TODO update in db
    return {"status": 200, "data": grouprow}


@router_grouprows.delete("/{grouprow_id}", response_model=models.GrouprowModel)
def delete_grouprow(current_user: Annotated[models.UserModel, Depends(get_current_active_user)],
                    grouprow_id: int):
    # TODO: delete to db
    return {"status": 200, "data": grouprow_id}


# Tasks
router_tasks = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


@router_tasks.get("/", response_model=list[models.TaskModel])
def get_tasks(current_user: Annotated[models.UserModel, Depends(get_current_active_user)],
              limit: int = 1, offset: int = 0
              ):
    tasks = db.get_dhtasks(current_user.username)
    return [task for task in tasks[offset:][:limit]]


@router_tasks.get("/{task_id}", response_model=models.TaskModel)
def get_task(current_user: Annotated[models.UserModel, Depends(get_current_active_user)],
             task_id: int):
    tasks = db.get_dhtasks(current_user.username)
    current_task = list(filter(lambda task: task.get("id") == task_id, tasks))[0]
    return current_task


# Logevents
router_logevents = APIRouter(
    prefix="/logevents",
    tags=["Logevents"]
)


@router_logevents.get("/", response_model=list[models.LogeventModel])
def get_logevents(current_user: Annotated[models.UserModel, Depends(get_current_active_user)],
                  limit: int = 1, offset: int = 0,
                  startdate: datetime = datetime.now(),
                  enddate: datetime = datetime.now()
                  ):
    logevents = db.get_logevents(current_user.username, start_date=startdate, end_date=enddate)
    return [logevent for logevent in logevents[offset:][:limit]]


app.include_router(router_reports)
app.include_router(router_groups)
app.include_router(router_grouprows)
app.include_router(router_tasks)
app.include_router(router_logevents)
