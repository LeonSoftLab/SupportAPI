from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import APIRouter
from typing import List
from datetime import datetime, timedelta
import jwt
import config
import mssqlworker
import models
import auth

app = FastAPI(
    title="Support App"
)

# Создаём обьект для работы с базой данных
db = mssqlworker.MssqlWorker()

# Создаем объект для работы с HTTP-заголовками авторизации
bearer_scheme = HTTPBearer()

@app.get("/")
def get_hello():
    return "Hello world!"


# Аутентификация пользователя
@app.post("/login")
def login(login_request: models.LoginRequestModel):
    user = auth.authenticate_user(login_request.username, login_request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token_data = models.TokenDataModel(username=user["username"], exp=datetime.utcnow() + timedelta(minutes=config.JWT_EXPIRATION_TIME_MINUTES))
    access_token = auth.create_jwt_token(token_data)
    return {"access_token": access_token, "token_type": "bearer"}


# Reports
router_reports = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


@router_reports.get("/{report_code}", response_model=List[models.ReportModel])
def get_report(token: HTTPAuthorizationCredentials = Depends(bearer_scheme), report_code: str = ""):
    username = check_auth(token)
    if username is not None:
        reports = db.get_reports(codename=report_code)
        return [report for report in reports]


@router_reports.post("/{report_code}")
def change_report_name(report_code: str, new_name: str):
    current_report = db.get_reports(codename=report_code)[0]
    current_report["name"] = new_name
    return {"status": 200, "data": current_report}


@router_reports.get("/", response_model=List[models.ReportModel])
def get_reports(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    username = check_auth(token)
    if username is not None:
        reports = db.get_reports()
        return [report for report in reports]


@router_reports.post("/reports")
def add_reports(reports: List[models.ReportModel]):
    return {"status": 200, "data": reports}


# Groups
router_groups = APIRouter(
    prefix="/groups",
    tags=["Groups"]
)


@router_groups.get("/{group_code}", response_model=List[models.GroupModel])
def get_group(token: HTTPAuthorizationCredentials = Depends(bearer_scheme), group_code: str = ""):
    username = check_auth(token)
    if username is not None:
        groups = db.get_groups(codename=group_code)
        return [group for group in groups]


@router_groups.get("/", response_model=List[models.GroupModel])
def get_groups(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    username = check_auth(token)
    if username is not None:
        groups = db.get_groups()
        return [group for group in groups]


@router_groups.post("/")
def add_groups(groups: List[models.GroupModel]):
    return {"status": 200, "data": groups}


# Grouprows
router_grouprows = APIRouter(
    prefix="/grouprows",
    tags=["Grouprows"]
)


@router_grouprows.get("/{group_id}", response_model=List[models.GrouprowModel])
def get_grouprows_by_group(token: HTTPAuthorizationCredentials = Depends(bearer_scheme), group_id: int = -1):
    username = check_auth(token)
    if username is not None:
        grouprows = db.get_grouprows(idgroup=group_id)
        return [grouprow for grouprow in grouprows]


@router_grouprows.get("/", response_model=List[models.GrouprowModel])
def get_grouprows_by_code(token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
                          codename: str = ""):
    username = check_auth(token)
    if username is not None:
        grouprows = db.get_grouprows_by_split_codename(codename=codename)
        return [grouprow for grouprow in grouprows]


@router_grouprows.post("/")
def add_groups(groups: List[models.GroupModel]):
    return {"status": 200, "data": groups}


# Tasks
router_tasks = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


@router_tasks.get("/", response_model=List[models.TaskModel])
def get_tasks(token: HTTPAuthorizationCredentials = Depends(bearer_scheme), limit: int = 1, offset: int = 0):
    username = check_auth(token)
    if username is not None:
        tasks = db.get_dhtasks(username)
        return [task for task in tasks[offset:][:limit]]


@router_tasks.get("/{task_id}", response_model=List[models.TaskModel])
def get_task(token: HTTPAuthorizationCredentials = Depends(bearer_scheme), task_id: int = 0):
    username = check_auth(token)
    current_task = None
    if username is not None:
        tasks = db.get_dhtasks(username)
        current_task = list(filter(lambda task: task.get("id") == task_id, tasks))[0]
    return current_task


# Logevents
router_logevents = APIRouter(
    prefix="/logevents",
    tags=["Logevents"]
)


@router_logevents.get("/", response_model=List[models.LogeventModel])
def get_logevents(token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
                  limit: int = 1, offset: int = 0,
                  startdate: datetime = datetime.now(),
                  enddate: datetime = datetime.now()
                  ):
    username = check_auth(token)
    if username is not None:
        logevents = db.get_logevents(username, start_date=startdate, end_date=enddate)
        return [logevent for logevent in logevents[offset:][:limit]]


def check_auth(token):
    try:
        payload = jwt.decode(token.credentials, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        token_data = models.TokenDataModel(username=username, exp=datetime.fromtimestamp(payload.get("exp")))
        if datetime.utcnow() >= token_data.exp:
            raise HTTPException(status_code=401, detail="Token has expired")
    except (jwt.InvalidTokenError, Exception):
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return username


app.include_router(router_reports)
app.include_router(router_groups)
app.include_router(router_grouprows)
app.include_router(router_tasks)
app.include_router(router_logevents)
