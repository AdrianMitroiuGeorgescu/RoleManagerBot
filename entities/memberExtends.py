from repositories.memberExtendsRepository import MemberExtendsRepository

REACTION_EXTEND_NAME = 'reaction'


class MemberExtendDto:
    def __init__(self):
        self.member_id  = 0
        self.name       = None
        self.increment  = 0
        self.modified   = 0
        self.repository = MemberExtendsRepository()

    def get_member_reaction_extend(self, member_id):
        db_member_extend = self.repository.get_extend(str('%' + REACTION_EXTEND_NAME + '%'), member_id)
        if db_member_extend is None:
            return None
        self.setup_dto(db_member_extend)
        return self

    def setup_dto(self, db_extend):
        self.member_id = db_extend['member_id']
        self.name      = db_extend['name']
        self.increment = db_extend['increment']
        self.modified  = db_extend['modified']

    def add_reaction_extend(self, member_id):
        self.repository.add_extend(REACTION_EXTEND_NAME, member_id)

    def update_extend(self):
        self.repository.update_extend(self)
