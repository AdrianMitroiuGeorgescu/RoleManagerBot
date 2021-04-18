from main.db import Db


class MemberExtendsRepository(Db):
    def get_extend(self, name, member_id):
        query = 'SELECT * FROM member_extends me WHERE me.name LIKE %s and me.member_id = %s'
        result = self.record(query, name, member_id)
        return result

    def add_extend(self, name, member_id):
        query = 'INSERT INTO member_extends (name, member_id) VALUES (%s, %s)'
        self.execute(query, name, member_id)

    def update_extend(self, member_extend_dto):
        query = 'UPDATE member_extends ' \
                'SET increment = %s ' \
                'WHERE name = %s and member_id = %s'
        self.execute(query,
                     member_extend_dto.increment+1,
                     member_extend_dto.name,
                     member_extend_dto.member_id)
