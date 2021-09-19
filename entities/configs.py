from entities.traits.configTrait import ConfigTrait
from repositories.configsRepository import ConfigRepository


class ConfigDto(ConfigTrait):
    def __init__(self):
        super().__init__()
        self.id         = None
        self.name       = None
        self.value      = None
        self.modified   = None
        self.repository = ConfigRepository()

    def get_config(self, config_dto):
        db_config = self.repository.get_config(config_dto)
        print(db_config)
        if db_config is None:
            return None
        self.setup_config(db_config)
        return self

    def get_config_by_id(self, config_id):
        db_config = self.repository.get_config_by_id(config_id)
        if db_config is None:
            return None
        self.setup_config(db_config)
        return self

    def setup_config(self, db_config):
        self.id       = db_config['id']
        self.name     = db_config['name']
        self.value    = db_config['value']
        self.modified = db_config['modified']

    def add_config(self):
        self.repository.add_config(self)

    def get_configs(self):
        db_configs = self.repository.get_configs()
        if db_configs is None:
            return None

        configs = []
        for db_config in db_configs:
            config_dto = ConfigDto()
            config_dto.setup_config(db_config)
            configs.append(config_dto)

        return configs

    def save(self):
        self.repository.save(self)


config = ConfigDto()
