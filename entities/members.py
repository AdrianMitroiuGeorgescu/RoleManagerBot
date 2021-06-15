import os

from dotenv import load_dotenv

from entities.levels import LevelDto
from entities.memberExtends import MemberExtendDto
from repositories.membersRepository import MembersRepository

load_dotenv()

ROLE_NOMAD     = int(os.getenv('nomad'))
ROLE_TARAN     = int(os.getenv('taran'))
ROLE_PAHARNIC  = int(os.getenv('paharnic'))
ROLE_BOIER     = int(os.getenv('boier'))
ROLE_ISPRAVNIC = int(os.getenv('ispravnic'))
ROLE_VOIEVOD   = int(os.getenv('voievod'))
ROLE_DOMNITOR  = int(os.getenv('domnitor'))
ROLE_PENSIONAR = int(os.getenv('retired_role_id'))

ROLES = [
    ROLE_NOMAD,
    ROLE_TARAN,
    ROLE_PAHARNIC,
    ROLE_BOIER,
    ROLE_ISPRAVNIC,
    ROLE_VOIEVOD,
    ROLE_DOMNITOR
]


class MemberDto:
    def __init__(self):
        self.member_id              = 0
        self.xp                     = 0
        self.level_id               = 0
        self.first_to_voice_channel = 0
        self.joined_voice           = None
        self.left_voice             = None
        self.time_spent             = 0
        self.steal_flag             = 0
        self.steal_time             = 0
        self.messages_xp            = 0
        self.emojis_xp              = 0
        self.web_xp                 = 0
        self.share_xp               = 0
        self.total_xp               = 0
        self.repository             = MembersRepository()

    def get_member(self, member_id):
        db_member = self.repository.get_member(member_id)
        if db_member is None:
            self.save_member(member_id)
            return self.get_member(member_id)
        self.setup_member(db_member)
        return self

    def setup_member(self, db_member):
        self.member_id              = db_member['member_id']
        self.xp                     = db_member['xp']
        self.level_id               = db_member['level_id']
        self.first_to_voice_channel = db_member['first_to_voice_channel']
        self.joined_voice           = db_member['joined_voice']
        self.left_voice             = db_member['left_voice']
        self.time_spent             = db_member['time_spent']
        self.steal_flag             = db_member['steal_flag']
        self.steal_time             = db_member['modified']
        self.messages_xp            = db_member['messages_xp']
        self.emojis_xp              = db_member['emojis_xp']
        self.web_xp                 = db_member['web_xp']
        self.share_xp               = db_member['share_xp']
        self.total_xp               = db_member['total_xp']

    def set_member(self, member_id):
        db_member = self.repository.get_member(member_id)
        self.setup_member(db_member)

    def save_member(self, member_id):
        self.repository.add_member(member_id)

    def get_member_level(self):
        level      = LevelDto()
        level.get_level(self.level_id)
        return level

    async def save(self, bot):
        await self.update_member_level(bot)
        self.repository.save(self)

    def get_member_by_filters(self, filters):
        db_member = self.repository.get_member_by_filters(filters)
        if db_member is None:
            return None
        self.setup_member(db_member)

    def get_leaderboard(self):
        db_members = self.repository.get_leaderboard()

        if db_members is None:
            return None

        members = []
        for db_member in db_members:
            member_dto = MemberDto()
            member_dto.setup_member(db_member)
            members.append(member_dto)

        return members

    def get_leader(self):
        db_member = self.repository.get_leader()
        if db_member is None:
            return None
        self.setup_member(db_member)
        return self

    def get_thieves(self, member_dto):
        db_members = self.repository.get_participants_without_leader(member_dto)

        if db_members is None:
            return None

        thieves = []
        for db_member in db_members:
            member_dto = MemberDto()
            member_dto.setup_member(db_member)
            thieves.append(member_dto)

        return thieves

    def get_thief(self):
        db_member = self.repository.get_thief()
        if db_member is None:
            return None
        self.setup_member(db_member)
        return self

    def reset_heist(self):
        self.repository.reset_heist()

    async def update_member_level(self, bot):
        self.total_xp = self.xp + self.messages_xp + self.emojis_xp + self.web_xp + self.share_xp

        level_dto = LevelDto()
        level_dto.get_level_up(self.total_xp)
        if level_dto is not None:
            if level_dto.xp_amount <= self.total_xp and level_dto.id != self.level_id:
                self.level_id = level_dto.id
                await bot.get_channel(int(bot.channel)).send(
                    f'{bot.guild.get_member(self.member_id).mention}, you have reached: {level_dto.name}!'
                )
            guild_member = bot.guild.get_member(self.member_id)
            roles        = guild_member.roles
            role_to_get  = bot.guild.get_role(int(self.get_member_level().role_id))
            if role_to_get not in roles:
                for role in roles:
                    if int(role.id) not in ROLES:
                        continue
                    remove_role = bot.guild.get_role(int(role.id))
                    await guild_member.remove_roles(remove_role)

                await guild_member.add_roles(role_to_get)
            pensionar = bot.guild.get_role(ROLE_PENSIONAR)
            if pensionar in roles:
                await guild_member.remove_roles(pensionar)

    def get_reaction_extend(self):
        member_extend_dto = MemberExtendDto()
        member_extend_dto.get_member_reaction_extend(self.member_id)
        return member_extend_dto

    def set_reaction_extend(self):
        member_extend_dto = MemberExtendDto()
        member_extend_dto.add_reaction_extend(self.member_id)

    def get_inactive_members(self):
        db_members = self.repository.get_inactive_members()

        if db_members is None:
            return None

        inactive_members = []
        for db_member in db_members:
            member_dto = MemberDto()
            member_dto.setup_member(db_member)
            inactive_members.append(member_dto)

        return inactive_members


member = MemberDto()
