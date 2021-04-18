from entities.traits.configTrait import ConfigTrait
from repositories.configsRepository import ConfigRepository


class ConfigDto(ConfigTrait):
    def __init__(self):
        super().__init__()
        self.id         = None
        self.name       = None
        self.value      = None
        self.repository = ConfigRepository()

    def get_config(self, config_dto):
        db_config = self.repository.get_config(config_dto)
        if db_config is None:
            return None
        self.setup_config(db_config)
        return self

    def setup_config(self, db_config):
        self.id    = db_config['id']
        self.name  = db_config['name']
        self.value = db_config['value']

    def add_config(self):
        self.repository.add_config(self)

    def save(self):
        self.repository.save(self)


config = ConfigDto()
