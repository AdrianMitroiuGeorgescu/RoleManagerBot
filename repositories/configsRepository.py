from main.db import Db


class ConfigRepository(Db):
    def get_config(self, config_dto):
        if config_dto.name:
            query = 'SELECT * FROM configs c WHERE c.name = %s'
            result = self.record(query, str(config_dto.name))
            return result

    def get_config_by_id(self, config_id):
        query = 'SELECT * FROM configs c WHERE c.id = %s'
        result = self.record(query, int(config_id))
        return result

    def add_config(self, config_dto):
        query = 'INSERT INTO configs (name, value) VALUES (%s, %s)'
        self.execute(query, config_dto.name, config_dto.value)

    def get_configs(self):
        query  = 'SELECT * FROM configs c'
        results = self.records(query)
        return results

    def save(self, config_dto):
        print(config_dto)
        query = 'UPDATE configs SET value = %s, modified=NOW(3) WHERE id = "%s"'
        self.execute(query, config_dto.value, config_dto.id)
