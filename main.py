from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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
@app.get("/reports/{report_code}", response_model=List[models.ReportModel])
def get_report(report_code: str):
    reports = db.get_reports(codename=report_code)
    return [report for report in reports]


@app.post("/reports/{report_code}")
def change_report_name(report_code: str, new_name: str):
    current_report = db.get_reports(codename=report_code)[0]
    current_report["name"] = new_name
    return {"status": 200, "data": current_report}


@app.get("/reports", response_model=List[models.ReportModel])
def get_reports():
    reports = db.get_reports()
    return [report for report in reports]


@app.post("/reports")
def add_reports(reports: List[models.ReportModel]):
    return {"status": 200, "data": reports}


# Groups
@app.get("/groups/{group_code}", response_model=List[models.GroupModel])
def get_group(group_code: str):
    groups = db.get_groups(codename=group_code)
    return [group for group in groups]


@app.get("/groups", response_model=List[models.GroupModel])
def get_groups():
    groups = db.get_groups()
    return [group for group in groups]


@app.post("/groups")
def add_groups(groups: List[models.GroupModel]):
    return {"status": 200, "data": groups}


# Tasks
@app.get("/tasks", response_model=List[models.TaskModel])
def get_tasks(limit: int = 1, offset: int = 0):
    tasks = db.get_dhtasks(user_id=-1)
    return [task for task in tasks[offset:][:limit]]


@app.get("/tasks/{task_id}", response_model=List[models.TaskModel])
def get_task(task_id: int):
    tasks = db.get_dhtasks(user_id=-1)
    current_task = list(filter(lambda task: task.get("id") == task_id, tasks))[0]
    return current_task


# Logevents
@app.get("/logevents", response_model=List[models.LogeventModel])
def get_logevents(token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
                  limit: int = 1, offset: int = 0,
                  startdate: datetime = datetime.now(),
                  enddate: datetime = datetime.now()
                  ):
    username = check_auth(token)
    if username is not None:
        logevents = db.get_logevents(user_id=-1, start_date=startdate, end_date=enddate)
        return [logevent for logevent in logevents[offset:][:limit]]


@app.get("/protected")
def protected_route(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    username = check_auth(token)
    if username is not None:
        return {"message": username+", you have access to protected route"}


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