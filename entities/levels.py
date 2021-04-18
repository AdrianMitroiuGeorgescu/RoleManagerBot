from repositories.levelsRepository import LevelsRepository


class LevelDto:
    def __init__(self):
        self.repository = LevelsRepository()
        self.id         = 0
        self.name       = 'None'
        self.xp_amount  = 0
        self.role_id    = 0

    def get_level(self, level_id):
        db_level = self.repository.get_level_name(level_id)
        if db_level is None:
            return None
        self.hydrated_object(db_level)
        return self

    def hydrated_object(self, db_level):
        self.id         = db_level['id']
        self.name       = db_level['name']
        self.xp_amount  = db_level['xp_amount']
        self.role_id    = db_level['role_id']

    def setup_level(self, level_details):
        self.name      = level_details['name']
        self.xp_amount = level_details['xp_amount']

    def save_level(self, level_details):
        self.repository.add_level(level_details)

    def get_next_level(self, member_total_xp):
        db_level = self.repository.get_next_level(member_total_xp)
        if db_level is None:
            return None
        self.hydrated_object(db_level)
        return self

    def get_level_up(self, member_total_xp):
        db_level = self.repository.get_level_up(member_total_xp)
        if db_level is None:
            return None
        self.hydrated_object(db_level)
        return self

    def get_levels(self):
        db_levels = self.repository.get_levels()
        levels    = []
        if db_levels is None:
            return None
        for db_level in db_levels:
            level_dto = LevelDto()
            level_dto.hydrated_object(db_level)
            levels.append(level_dto)
        return levels


level = LevelDto()
