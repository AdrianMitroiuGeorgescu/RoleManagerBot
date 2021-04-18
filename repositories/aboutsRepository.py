from main.db import Db


class AboutsRepository(Db):
    def get_about(self, name):
        query = 'SELECT * FROM abouts a WHERE a.name = %s'
        result = self.record(query, name)
        return result

    def get_abouts(self, name):
        if name is None:
            query = 'SELECT * FROM abouts'
            return self.records(query)
        query   = 'SELECT * FROM abouts a WHERE a.name = %s'
        results = self.records(query, name)
        return results

    def add_about(self, about_dto):
        query = 'INSERT INTO abouts (name, description, member_id) VALUES (%s, %s, %s)'
        self.execute(query, about_dto.name, about_dto.description, about_dto.member_id)
