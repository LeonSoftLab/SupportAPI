import pyodbc
from datetime import datetime
from config import CONNECT_STRING


class MssqlWorker:
    def __init__(self):
        self.connection = pyodbc.connect(CONNECT_STRING, autocommit=True)
        self.cursor = self.connection.cursor()

    def get_groups(self, codename=None):
        """
        Получает из базы группы вопросов (проекты)
        """
        if codename is not None:
            rows = self.cursor.execute("SELECT * FROM [dbo].[groups] with(nolock) WHERE [codename]=?", (str(codename))).fetchone()
        else:
            rows = self.cursor.execute('SELECT * FROM [dbo].[groups] with(nolock)').fetchall()
        columns = [column[0] for column in self.cursor.description]
        result: list = []
        for row in rows:
            result.append(dict(zip(columns, row)))
        return result

    def get_grouprows(self, idgroup, codename=None):
        """ Получаем все строки по группе """
        if codename is not None:
            rows = self.cursor.execute("SELECT * FROM [dbo].[grouprows] with(nolock) WHERE [idgroup]=? and [commandtext]=?", (int(idgroup), str(codename))).fetchone()
        else:
            rows = self.cursor.execute('SELECT * FROM [dbo].[grouprows] with(nolock) WHERE [idgroup]=?', (int(idgroup))).fetchall()
        columns = [column[0] for column in self.cursor.description]
        result: list = []
        for row in rows:
            result.append(dict(zip(columns, row)))
        return result

    def get_grouprows_by_split_codename(self, codename):
        """ Получаем все строки по кодовому имени группы и строки """
        splitted_codename = codename.split("_")
        rows = self.cursor.execute("SELECT distinct gr.* "
        "  FROM [dbo].[groups] g with(nolock) "
        "    inner join [dbo].[grouprows] gr with(nolock) on gr.idgroup = g.id "
        "  WHERE g.codename = ? and gr.[commandtext] = ?", (splitted_codename[0], splitted_codename[1])).fetchone()
        columns = [column[0] for column in self.cursor.description]
        result: list = []
        for row in rows:
            result.append(dict(zip(columns, row)))
        return result

    def get_reports(self, user_id=-1, codename=None):
        """ Получает из базы доступные отчёты """
        if codename is not None:
            rows = self.cursor.execute("SELECT * FROM [dbo].[reports] with(nolock) WHERE [codename]=?", (str(codename))).fetchone()
        else:
            rows = self.cursor.execute('SELECT * FROM [dbo].[reports] with(nolock)').fetchall()
        columns = [column[0] for column in self.cursor.description]
        result: list = []
        for row in rows:
            result.append(dict(zip(columns, row)))
        return result

    def get_dhtasks(self, user_id=-1):
        """ Получает из базы сообщения/задачи пользователя """
        rows = self.cursor.execute("EXECUTE [dbo].[w_GetDhTasks] @iduser =?", (int(user_id))).fetchall()
        columns = [column[0] for column in self.cursor.description]
        result: list = []
        for row in rows:
            result.append(dict(zip(columns, row)))
        return result

    def get_logevents(self, user_id=-1, start_date=datetime.now(), end_date=datetime.now()):
        """ Получает из базы логи бота """
        rows = self.cursor.execute("SELECT * FROM [dbo].[logevents] where [iduser] =? and [datetimestamp] between ? and ?",
                                   (int(user_id), start_date, end_date)
                                   ).fetchall()
        columns = [column[0] for column in self.cursor.description]
        result: list = []
        for row in rows:
            result.append(dict(zip(columns, row)))
        return result

    def get_user(self, tel):
        """ Получаем из базы сотрудников """
        rows = self.cursor.execute("SELECT * FROM [dbo].[users] with(nolock) WHERE [tel]=? or '+'+[tel]=?", (tel, tel)).fetchone()
        columns = [column[0] for column in self.cursor.description]
        result: list = []
        for row in rows:
            result.append(dict(zip(columns, row)))
        return result

    def add_logevent(self, iduser, chat_id, event, status, description):
        """ Делаем запись в лог событий """
        self.cursor.execute("INSERT INTO [dbo].[logevents] \n"
        "           ([iduser] \n"
        "           ,[chat_id] \n"
        "           ,[datetimestamp] \n"
        "           ,[event] \n"
        "           ,[status] \n"
        "           ,[description]) \n"
        "     VALUES \n"
        "           (? \n"
        "           ,? \n"
        "           ,getdate() \n"
        "           ,? \n"
        "           ,? \n"
        "           ,?) ", (iduser, chat_id, event, status, description))
        self.connection.commit()

    def add_task(self, iduser, last_context, message_text):
        """ Делаем запись в задачи пользователя """
        self.cursor.execute("INSERT INTO [dbo].[dh_tasks] \n"
        "           ([iduser] \n"
        "           ,[last_context] \n"
        "           ,[message_text]) \n"
        "     VALUES \n"
        "           (? \n"
        "           ,? \n"
        "           ,? )", (iduser, last_context, message_text))
        self.connection.commit()

    def close(self):
        """ Закрываем текущее соединение с БД """
        self.connection.close()

if __name__ == '__main__':
    db = MssqlWorker(CONNECT_STRING)
    tasks = db.get_dhtasks(user_id=-1)
    result = tasks is not None
    if result:
        columns = [column[0] for column in db.cursor.description]
        results = []
        for row in tasks:
            results.append(dict(zip(columns, row)))
        print(results)
        # print(columns)
        # print([[col for col in task] for task in tasks[0:][:2]])
        # print(list([task for task in list(tasks[0:][:20])]))
    db.close
