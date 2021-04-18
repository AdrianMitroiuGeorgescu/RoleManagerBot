from repositories.aboutsRepository import AboutsRepository


class AboutDto:
    def __init__(self):
        self.id          = 0
        self.name        = ''
        self.description = ''
        self.member_id   = None
        self.repository  = AboutsRepository()

    def get_about(self, name):
        db_about = self.repository.get_about(name)
        if db_about is None:
            return None
        self.setup_about(db_about)
        return self

    def get_abouts(self, name):
        db_abouts = self.repository.get_abouts(name)
        if db_abouts is None:
            return None

        abouts = []
        for db_about in db_abouts:
            about_dto = AboutDto()
            about_dto.setup_about(db_about)
            abouts.append(about_dto)

        return abouts

    def setup_about(self, db_about):
        self.id          = db_about['id']
        self.name        = db_about['name']
        self.description = db_about['description']
        self.member_id   = db_about['member_id']

    def add_about(self):
        self.repository.add_about(self)

