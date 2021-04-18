FIRST_TO_CONNECT_ID = 'FIRST_TO_CONNECT'
DAILY_RESET         = 'DAILY_RESET'


class ConfigTrait:
    def __init__(self):
        self.first_to_connect = FIRST_TO_CONNECT_ID
        self.daily_reset      = DAILY_RESET


configTrait = ConfigTrait()
