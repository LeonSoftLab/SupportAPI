import os
from sqlalchemy import update, delete, and_, select, literal

import auth
import models
import schemas


class UserController:
    """Data Access Layer and business logic for operating user"""
    def __init__(self, db_session):
        self.db_session = db_session

    def create(self, user: schemas.UserSchemaCreate) -> schemas.UserSchema:
        hashed_password = auth.pwd_context.hash(user.password)

        new_user = models.UserModel(
            user_name=user.user_name,
            id_employee=0,
            disabled=False,
            password=hashed_password,
            role="user",
        )
        self.db_session.add(new_user)
        self.db_session.commit()
        self.db_session.refresh(new_user)
        return schemas.UserSchema(
            user_name=new_user.user_name,
            disabled=new_user.disabled,
            role=new_user.role,
            hashed_password=new_user.password,
        )

    def get(self, user_name: str = "") -> list[schemas.UserSchema]:
        if user_name != "":
            users = self.db_session.query(models.UserModel).filter(models.UserModel.user_name == user_name).all()
        else:
            users = self.db_session.query(models.UserModel).order_by(models.UserModel.user_name).all()

        if users is not None:
            return [schemas.UserSchema(user_name=user.user_name,
                                       disabled=user.disabled,
                                       role=user.role,
                                       hashed_password=user.password,
                                       )
                    for user in users]

    def delete(self, user_name: str) -> schemas.UserSchema | None:
        query = update(models.UserModel).\
            where(models.UserModel.user_name == user_name).\
            values(disabled=True).\
            returning(models.UserModel)
        deleted_user_name_rec = self.db_session.execute(query).fetchone()
        self.db_session.commit()
        if deleted_user_name_rec is not None:
            return schemas.UserSchema(user_name=str(deleted_user_name_rec[0].user_name),
                                      disabled=str(deleted_user_name_rec[0].disabled),
                                      role=str(deleted_user_name_rec[0].role),
                                      hashed_password=str(deleted_user_name_rec[0].hashed_password),
                                      )

    def update(self, user_name: str, **kwargs) -> schemas.UserSchemaUpdate | None:
        kwargs['password'] = auth.pwd_context.hash(kwargs['password'])

        query = update(models.UserModel). \
            where(models.UserModel.user_name == user_name). \
            values(kwargs). \
            returning(models.UserModel)
        update_user_name_rec = self.db_session.execute(query).fetchone()
        self.db_session.commit()
        if update_user_name_rec is not None:
            return schemas.UserSchemaUpdate(id_employee=update_user_name_rec[0].id_employee,
                                            disabled=update_user_name_rec[0].disabled,
                                            role=update_user_name_rec[0].role,
                                            hashed_password=update_user_name_rec[0].password,
                                            )


class ReportController:
    """Data Access Layer and business logic for operating report"""
    def __init__(self, db_session):
        self.db_session = db_session

    def create(self, report: schemas.ReportSchemaCreate) -> schemas.ReportSchema:
        new_report = models.ReportModel(
            name=report.name,
            description=report.description,
            code_name=report.code_name,
            file_name=report.file_name,
        )
        self.db_session.add(new_report)
        self.db_session.commit()
        self.db_session.refresh(new_report)
        return schemas.ReportSchema(id=new_report.id,
                                    name=new_report.name,
                                    description=new_report.description,
                                    code_name=new_report.code_name,
                                    file_name=new_report.file_name,
                                    )

    def get(self, code_name: str = "", _id: int = 0) -> list[schemas.ReportSchema]:
        if code_name:
            reports = self.db_session.query(models.ReportModel).\
                filter(models.ReportModel.code_name == code_name).\
                all()
        elif _id:
            reports = self.db_session.query(models.ReportModel).\
                filter(models.ReportModel.id == _id).\
                all()
        else:
            reports = self.db_session.query(models.ReportModel).\
                order_by(models.ReportModel.id).\
                all()

        if reports is not None:
            return [schemas.ReportSchema(id=report.id,
                                         name=report.name,
                                         description=report.description,
                                         code_name=report.code_name,
                                         file_name=report.file_name,
                                         )
                    for report in reports]

    def delete(self, _id: int) -> schemas.ReportSchema | None:
        query = delete(models.ReportModel).\
            where(models.ReportModel.id == _id).\
            returning(models.ReportModel)
        deleted_report_rec = self.db_session.execute(query).fetchone()
        self.db_session.commit()
        if deleted_report_rec is not None:
            return schemas.ReportSchema(id=deleted_report_rec.id,
                                        name=deleted_report_rec.name,
                                        description=deleted_report_rec.description,
                                        code_name=deleted_report_rec.code_name,
                                        file_name=deleted_report_rec.file_name,
                                        )

    def update(self, _id: int, **kwargs) -> schemas.ReportSchema | None:
        query = update(models.ReportModel). \
            where(models.ReportModel.id == _id). \
            values(kwargs). \
            returning(models.ReportModel)
        update_report_rec = self.db_session.execute(query).fetchone()
        self.db_session.commit()
        if update_report_rec is not None:
            return schemas.ReportSchema(id=update_report_rec[0].id,
                                        name=update_report_rec[0].name,
                                        description=update_report_rec[0].description,
                                        code_name=update_report_rec[0].code_name,
                                        file_name=update_report_rec[0].file_name,
                                        )


class GroupController:
    """Data Access Layer and business logic for operating groups"""
    def __init__(self, db_session):
        self.db_session = db_session

    def create(self, group: schemas.GroupSchemaCreate) -> schemas.GroupSchema:
        new_group = models.GroupModel(
            name=group.name,
            description=group.description,
            code_name=group.code_name,
        )
        self.db_session.add(new_group)
        self.db_session.commit()
        self.db_session.refresh(new_group)
        return schemas.GroupSchema(id=new_group.id,
                                   name=new_group.name,
                                   description=new_group.description,
                                   code_name=new_group.code_name,
                                   )

    def get(self, code_name: str = "", _id: int = 0) -> list[schemas.GroupSchema]:
        if code_name:
            groups = self.db_session.query(models.GroupModel).\
                filter(models.GroupModel.code_name == code_name).\
                all()
        elif _id:
            groups = self.db_session.query(models.GroupModel).\
                filter(models.GroupModel.id == _id).\
                all()
        else:
            groups = self.db_session.query(models.GroupModel).\
                order_by(models.GroupModel.id).\
                all()

        if groups is not None:
            return [schemas.GroupSchema(id=group.id,
                                        name=group.name,
                                        description=group.description,
                                        code_name=group.code_name,
                                        )
                    for group in groups]

    def delete(self, _id: int) -> schemas.GroupSchema | None:
        query = delete(models.GroupModel).\
            where(models.GroupModel.id == _id).\
            returning(models.GroupModel)
        deleted_group = self.db_session.execute(query).fetchone()
        self.db_session.commit()
        if deleted_group is not None:
            return schemas.GroupSchema(id=deleted_group.id,
                                       name=deleted_group.name,
                                       description=deleted_group.description,
                                       code_name=deleted_group.code_name,
                                       )

    def update(self, _id: int, **kwargs) -> schemas.GroupSchema | None:
        query = update(models.GroupModel). \
            where(models.GroupModel.id == _id). \
            values(kwargs). \
            returning(models.GroupModel)
        update_group_rec = self.db_session.execute(query).fetchone()
        self.db_session.commit()
        if update_group_rec is not None:
            return schemas.GroupSchema(id=update_group_rec[0].id,
                                       name=update_group_rec[0].name,
                                       description=update_group_rec[0].description,
                                       code_name=update_group_rec[0].code_name,
                                       )


class GroupRowController:
    """Data Access Layer and business logic for operating group rows"""
    def __init__(self, db_session):
        self.db_session = db_session

    def create(self, group_row: schemas.GroupRowSchemaCreate) -> schemas.GroupRowSchema:
        new_group_row = models.GroupRowModel(
            id_group=group_row.id_group,
            name=group_row.name,
            command_text=group_row.command_text,
            file_name=group_row.file_name,
        )
        self.db_session.add(new_group_row)
        self.db_session.commit()
        self.db_session.refresh(new_group_row)
        return schemas.GroupRowSchema(id=new_group_row.id,
                                      id_group=new_group_row.id_group,
                                      name=new_group_row.name,
                                      command_text=new_group_row.command_text,
                                      file_name=new_group_row.file_name,
                                      )

    def get(self, id_group: int = 0, command_text: str = "", _id: int = 0) -> list[schemas.GroupRowSchema]:
        if id_group:
            group_rows = self.db_session.query(models.GroupRowModel).\
                filter(models.GroupRowModel.id_group == id_group).\
                all()
        elif command_text:
            group_rows = self.db_session.query(models.GroupRowModel).\
                filter(models.GroupRowModel.command_text == command_text).\
                all()
        elif _id:
            group_rows = self.db_session.query(models.GroupRowModel).\
                filter(models.GroupRowModel.id == _id).\
                all()
        else:
            group_rows = self.db_session.query(models.GroupRowModel).\
                order_by(models.GroupRowModel.id).\
                all()

        if group_rows is not None:
            return [schemas.GroupRowSchema(id=group_row.id,
                                           id_group=group_row.id_group,
                                           name=group_row.name,
                                           command_text=group_row.command_text,
                                           file_name=group_row.file_name,
                                           )
                    for group_row in group_rows]

    def delete(self, id_group: int = 0, _id: int = 0) -> schemas.GroupRowSchema | None:
        if id_group:
            query = delete(models.GroupRowModel). \
                where(models.GroupRowModel.id_group == id_group). \
                returning(models.GroupRowModel)
        elif _id:
            query = delete(models.GroupRowModel). \
                where(models.GroupRowModel.id == _id). \
                returning(models.GroupRowModel)

        deleted_group_row_rec = self.db_session.execute(query).fetchone()
        self.db_session.commit()
        if deleted_group_row_rec is not None:
            return schemas.GroupRowSchema(id=deleted_group_row_rec.id,
                                          id_group=deleted_group_row_rec.id_group,
                                          name=deleted_group_row_rec.name,
                                          command_text=deleted_group_row_rec.command_text,
                                          file_name=deleted_group_row_rec.file_name,
                                          )

    def update(self, _id: int, **kwargs) -> schemas.GroupRowSchema | None:
        query = update(models.GroupRowModel). \
            where(models.GroupRowModel.id == _id). \
            values(kwargs). \
            returning(models.GroupRowModel)
        update_group_row_rec = self.db_session.execute(query).fetchone()
        self.db_session.commit()
        if update_group_row_rec is not None:
            return schemas.GroupRowSchema(id=update_group_row_rec[0].id,
                                          id_group=update_group_row_rec[0].id_group,
                                          name=update_group_row_rec[0].name,
                                          command_text=update_group_row_rec[0].command_text,
                                          file_name=update_group_row_rec[0].file_name,
                                          )


class TaskController:
    """Data Access Layer and business logic for operating tasks"""
    def __init__(self, db_session):
        self.db_session = db_session

    def create(self, task: schemas.TaskSchemaCreate) -> schemas.TaskSchema:
        new_task = models.TaskModel(
            id_employee=task.id_employee,
            last_context=task.last_context,
            message_text=task.message_text,
        )
        self.db_session.add(new_task)
        self.db_session.commit()
        self.db_session.refresh(new_task)
        return schemas.TaskSchema(id=new_task.id,
                                  id_employee=new_task.id_employee,
                                  last_context=new_task.last_context,
                                  message_text=new_task.message_text,
                                  )

    def get(self, id_employee: int = 0, _id: int = 0) -> list[schemas.TaskSchema]:
        if id_employee:
            tasks = self.db_session.query(models.TaskModel).\
                filter(models.TaskModel.id_employee == id_employee).\
                all()
        elif _id:
            tasks = self.db_session.query(models.TaskModel).\
                filter(models.TaskModel.id == _id).\
                all()
        else:
            tasks = self.db_session.query(models.TaskModel).\
                order_by(models.TaskModel.id).\
                all()

        if tasks is not None:
            return [schemas.TaskSchema(id=task.id,
                                       id_employee=task.id_employee,
                                       last_context=task.last_context,
                                       message_text=task.message_text,
                                       )
                    for task in tasks]

    def delete(self, id_employee: int = 0, _id: int = 0) -> schemas.TaskSchema | None:
        if id_employee:
            query = delete(models.TaskModel). \
                where(models.TaskModel.id_employee == id_employee). \
                returning(models.TaskModel)
        elif _id:
            query = delete(models.TaskModel). \
                where(models.TaskModel.id == _id). \
                returning(models.TaskModel)

        deleted_task_rec = self.db_session.execute(query).fetchone()
        self.db_session.commit()
        if deleted_task_rec is not None:
            return schemas.TaskSchema(id=deleted_task_rec.id,
                                      id_employee=deleted_task_rec.id_employee,
                                      last_context=deleted_task_rec.last_context,
                                      message_text=deleted_task_rec.message_text,
                                      )

    def update(self, _id: int, **kwargs) -> schemas.TaskSchema | None:
        query = update(models.TaskModel). \
            where(models.TaskModel.id == _id). \
            values(kwargs). \
            returning(models.TaskModel)
        update_task_rec = self.db_session.execute(query).fetchone()
        self.db_session.commit()
        if update_task_rec is not None:
            return schemas.TaskSchema(id=update_task_rec[0].id,
                                      id_employee=update_task_rec[0].id_employee,
                                      last_context=update_task_rec[0].last_context,
                                      message_text=update_task_rec[0].message_text,
                                      )
