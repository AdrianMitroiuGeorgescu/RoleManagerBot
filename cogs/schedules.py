import datetime
import os
import random

from apscheduler.triggers.cron import CronTrigger
from discord.ext.commands import Cog
from dotenv import load_dotenv

from entities.configs import ConfigDto
from entities.members import MemberDto

load_dotenv()

FIRST_TO_CONNECT_ROLE = int(os.getenv('first_to_connect_role_id'))

RETIRE_ROLE    = int(os.getenv('retired_role_id'))
ROLE_NOMAD     = int(os.getenv('nomad'))
ROLE_TARAN     = int(os.getenv('taran'))
ROLE_PAHARNIC  = int(os.getenv('paharnic'))
ROLE_BOIER     = int(os.getenv('boier'))
ROLE_ISPRAVNIC = int(os.getenv('ispravnic'))
ROLE_VOIEVOD   = int(os.getenv('voievod'))
ROLE_DOMNITOR  = int(os.getenv('domnitor'))

ROLES = [
    ROLE_NOMAD,
    ROLE_TARAN,
    ROLE_PAHARNIC,
    ROLE_BOIER,
    ROLE_ISPRAVNIC,
    ROLE_VOIEVOD,
    ROLE_DOMNITOR,
    RETIRE_ROLE
]

class Schedules(Cog):
    def __init__(self, bot):
        self.bot = bot

    def run_schedules(self, scheduler):
        scheduler.add_job(self.reset_day, CronTrigger(hour='0-23',
                                                      minute=0,
                                                      second=0,
                                                      timezone='Europe/Bucharest'))

        # scheduler.add_job(self.steal_xp, CronTrigger(hour='8, 10, 12, 14, 16 , 18 , 20, 22 , 0',
        #                                              minute=0,
        #                                              second=0,
        #                                              timezone='Europe/Bucharest'))

        scheduler.add_job(self.check_web_status, CronTrigger(minute='0, 15, 30, 45',
                                                             second=0,
                                                             timezone='Europe/Bucharest'))
        scheduler.add_job(self.check_share_status, CronTrigger(minute='0, 15, 30, 45',
                                                               second=0,
                                                               timezone='Europe/Bucharest'))
        scheduler.add_job(self.retire_members, CronTrigger(hour=4, minute=0, second=0, timezone='Europe/Bucharest'))

    async def reset_day(self):
        config_dto = ConfigDto()
        config_dto.name = config_dto.daily_reset
        config_dto.get_config(config_dto)
        this_hour = datetime.datetime.now().hour
        if config_dto.value != this_hour:
            return

        config_dto = ConfigDto()
        config_dto.name = config_dto.first_to_connect
        config_dto.get_config(config_dto)
        config_dto.value = '0'
        config_dto.save()

        member_dto = MemberDto()
        filters = [('first_to_voice_channel', 1)]
        member_dto.get_member_by_filters(filters)
        member_dto.first_to_voice_channel = 0
        await member_dto.save(self.bot)
        member = self.bot.guild.get_member(member_dto.member_id)
        role = self.bot.guild.get_role(int(FIRST_TO_CONNECT_ROLE))
        await member.remove_roles(role)

    async def steal_xp(self):
        member_dto = MemberDto()
        member_dto.reset_heist()
        leader_member_dto = member_dto.get_leader()
        thieves = member_dto.get_thieves(leader_member_dto)
        member_dto = random.choice(thieves)
        member_dto.steal_flag = 1
        await member_dto.save(self.bot)

        channel = self.bot.get_channel(int(self.bot.channel))
        await channel.send(f'{self.bot.get_user(member_dto.member_id).mention} '
                           f'you have 15 seconds to steal from the leader! Use !steal')
        await channel.send(f'{self.bot.get_user(leader_member_dto.member_id).mention} '
                           f'you have 10 seconds to defend your xp! Use !stop_the_heist')

    async def check_web_status(self):
        voice_channels = self.bot.guild.voice_channels
        members = []
        for voice_channel in voice_channels:
            if len(voice_channel.members) < 2:
                return
            members_found = voice_channel.members
            for member_found in members_found:
                members.append(member_found)
        for member in members:
            if member.voice.self_video:
                member_dto = MemberDto()
                member_dto.get_member(member.id)
                member_dto.web_xp += 1
                await member_dto.save(self.bot)

    async def check_share_status(self):
        voice_channels = self.bot.guild.voice_channels
        members = []
        for voice_channel in voice_channels:
            if len(voice_channel.members) < 2:
                return
            members_found = voice_channel.members
            for member_found in members_found:
                members.append(member_found)
        for member in members:
            if member.voice.self_stream:
                member_dto = MemberDto()
                member_dto.get_member(member.id)
                member_dto.share_xp += 1
                await member_dto.save(self.bot)

    async def retire_members(self):
        member_dto       = MemberDto()
        inactive_members = member_dto.get_inactive_members()

        for member in inactive_members:
            guild_member = self.bot.guild.get_member(int(member.member_id))
            if guild_member is None:
                continue
            inactive_role = self.bot.guild.get_role(RETIRE_ROLE)
            await guild_member.add_roles(inactive_role)

        members = self.bot.guild.members
        for member in members:
            role_ids = []
            for role in member.roles:
                if role.id in ROLES:
                    role_ids.append(role.id)
            if len(role_ids) > 0 or member.bot:
                continue
            guild_member = self.bot.guild.get_member(int(member.id))
            if guild_member is None:
                continue
            inactive_role = self.bot.guild.get_role(RETIRE_ROLE)
            await guild_member.add_roles(inactive_role)
            return True


def setup(bot):
    bot.add_cog(Schedules(bot))
