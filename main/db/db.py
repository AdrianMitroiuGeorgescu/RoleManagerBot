import os
from os.path import isfile

from dotenv import load_dotenv
from mysql import connector
from apscheduler.triggers.cron import CronTrigger

load_dotenv()

DROP_PATH  = "./data/db/drop.sql"
BUILD_PATH = "./data/db/build.sql"


class Db:
    def __init__(self):
        self.cxn = connector.connect(
          host=os.getenv('host'),
          user=os.getenv('user'),
          password=os.getenv('password'),
          database=os.getenv('database')
        )
        self.cur = self.cxn.cursor(buffered=True)

    def build(self):
        if isfile(BUILD_PATH):
            self.scriptexec(BUILD_PATH)

    def commit(self):
        self.cxn.commit()
        self.close()

    def autosave(self, scheduler):
        pass

    def close(self):
        self.cxn.close()

    def field(self, command, *values):
        self.cur.execute(command, tuple(values))

        if (fetch := self.cur.fetchone()) is not None:
            return fetch[0]

    def record(self, command, *values):
        self.cur.execute(command, tuple(values))
        columns = self.cur.column_names
        value   = self.cur.fetchone()
        if value is None:
            return None
        row     = dict(zip(columns, value))
        return row

    def records(self, command, *values):
        self.cur.execute(command, tuple(values))
        rows = []
        head_rows = self.cur.column_names
        remaining_rows = self.cur.fetchall()

        for row in remaining_rows:
            rows.append(dict(zip(head_rows, row)))
        return rows

    def column(self, command, *values):
        self.cur.execute(command, tuple(values))

        return [item[0] for item in self.cur.fetchall()]

    def execute(self, command, *values):
        self.cur.execute(command, values)
        self.commit()

    def multiexec(self, command, valueset):
        self.cur.executemany(command, valueset)

    def scriptexec(self, path):
        with open(path, "r", encoding="utf-8") as script:
            self.cur.executescript(script.read())


db = Db()
