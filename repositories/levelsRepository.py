from main.db.db import Db


class LevelsRepository(Db):
    def get_level_name(self, level_id):
        query      = 'SELECT * FROM levels l where l.id = %s'
        level_name = self.record(query, level_id)
        return level_name

    def add_level(self, level_dto):
        query = 'INSERT INTO levels (name, xp_amount) VALUES (%s, %s)'
        self.execute(query, level_dto['name'], level_dto['xp_amount'])

    def get_next_level(self, member_total_xp):
        query     = 'SELECT * FROM levels l where l.xp_amount >= %s order by l.xp_amount asc limit 1'
        level_dto = self.record(query, member_total_xp)
        return level_dto

    def get_level_up(self, member_total_xp):
        query     = 'SELECT * FROM levels l where l.xp_amount <= %s order by l.xp_amount desc limit 1'
        level_dto = self.record(query, member_total_xp)
        return level_dto

    def get_levels(self):
        query = 'SELECT * FROM levels'
        return self.records(query)
