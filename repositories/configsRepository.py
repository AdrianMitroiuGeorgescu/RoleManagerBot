from main.db import Db


class ConfigRepository(Db):
    def get_config(self, config_dto):
        if config_dto.name:
            query = 'SELECT * FROM configs c WHERE c.name = %s'
            result = self.record(query, str(config_dto.name))
            return result

    def add_config(self, config_dto):
        query = 'INSERT INTO configs (name, description) VALUES (%s, %s, %s)'
        self.execute(query, config_dto.name, config_dto.value)

    def save(self, config_dto):
        query = 'UPDATE configs SET value = %s, modified=NOW(3) WHERE id = "%s"'
        self.execute(query, config_dto.value, config_dto.id)
