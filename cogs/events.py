import os
import datetime
import random

from apscheduler.triggers.cron import CronTrigger
from discord.ext.commands import Cog
from dotenv import load_dotenv

from entities.configs import ConfigDto
from entities.members import MemberDto, ROLE_NOMAD

load_dotenv()

FIRST_TO_CONNECT_ROLE = os.getenv('first_to_connect_role_id')
AFK_VOICE_CHANNEL     = os.getenv('afk_channel_id')
IGNORE_VOICE_CHANNELS = [
    AFK_VOICE_CHANNEL
]
GENERAL_VOICE_CHANNEL = os.getenv('general_voice_channel')
GENERAL_TEXT_CHANNEL  = os.getenv('general_text_channel')
XP_INTERVAL           = 900
REACTION_COOLDOWN     = 300


class Events(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(os.path.basename(__file__))

    @Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return
        channel = self.bot.get_channel(int(self.bot.channel))
        member_dto = MemberDto()
        member_dto.get_member(member.id)
        config_dto = ConfigDto()
        config_dto.name = config_dto.first_to_connect
        config_dto.get_config(config_dto)
        try:
            if (before.channel is None or (before.channel is not None and before.channel.id in IGNORE_VOICE_CHANNELS)) \
                    and (after.channel is not None and after.channel.id not in IGNORE_VOICE_CHANNELS):
                await self.check_first_to_connect(channel, config_dto, member, member_dto)

                member_dto.joined_voice = datetime.datetime.now()
                await member_dto.save(self.bot)

            if (before.channel is not None and before.channel.id not in IGNORE_VOICE_CHANNELS) \
                    and (after.channel is None or after.channel.id in IGNORE_VOICE_CHANNELS):
                await self.calculate_voice_time(member_dto)
        except Exception as e:
            print(f'Timestamp: {datetime.datetime.now()}')
            print(f'Exception type: {type(e)}')
            print(f'Arguments: {e.args}')
            print(f'Exception: {e}')

    async def check_first_to_connect(self, channel, config_dto, member, member_dto):
        if not config_dto.value:
            member_dto.xp += 10
            member_dto.first_to_voice_channel = 1
            config_dto.value = 1
            config_dto.save()
            role = self.bot.guild.get_role(int(FIRST_TO_CONNECT_ROLE))
            await member.add_roles(role)
            await channel.send(f'{member.mention}'
                               f' because you were the first one to connect in voice channel,'
                               f' you got an award')

    async def calculate_voice_time(self, member_dto):
        member_dto.left_voice = datetime.datetime.now()
        left = datetime.datetime.timestamp(member_dto.left_voice)
        join = datetime.datetime.timestamp(member_dto.joined_voice)
        member_dto.time_spent += left - join
        xp = member_dto.time_spent // XP_INTERVAL
        crumbs = member_dto.time_spent - (xp * XP_INTERVAL)
        member_dto.xp += xp
        member_dto.joined_voice = None
        member_dto.left_voice = None
        member_dto.time_spent = crumbs
        await member_dto.save(self.bot)

    def run_schedules(self, scheduler):
        config_dto = ConfigDto()
        config_dto.name = config_dto.daily_reset
        config_dto.get_config(config_dto)
        scheduler.add_job(self.reset_day, CronTrigger(hour=config_dto.value,
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

    async def reset_day(self):
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

    @Cog.listener()
    async def on_member_update(self, before, after):
        pass

    async def check_web_status(self):
        voice_channels = self.bot.guild.voice_channels
        members = []
        for voice_channel in voice_channels:
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
            members_found = voice_channel.members
            for member_found in members_found:
                members.append(member_found)
        for member in members:
            if member.voice.self_stream:
                member_dto = MemberDto()
                member_dto.get_member(member.id)
                member_dto.share_xp += 1
                await member_dto.save(self.bot)

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if not payload.member.bot:
            member_dto        = MemberDto()
            member_dto.get_member(payload.member.id)
            member_extend_dto = member_dto.get_reaction_extend()

            if member_extend_dto.name is None:
                member_dto.emojis_xp += 1
                await member_dto.save(self.bot)

                member_dto.set_reaction_extend()

            if member_extend_dto.name is not None:
                time_elapsed = datetime.datetime.now() - member_extend_dto.modified
                if time_elapsed.seconds > REACTION_COOLDOWN:
                    member_dto.emojis_xp += 1
                    await member_dto.save(self.bot)
                    member_extend_dto.update_extend()

            channel = self.bot.guild.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)

            message_send = (datetime.datetime.now() - message.created_at).seconds
            if message_send > REACTION_COOLDOWN:
                await message.clear_reactions()

            if len(message.embeds) > 0:
                for embed in message.embeds:
                    if 'Kick' in embed.title:
                        description  = embed.description.split(':')
                        votes_needed = int(description[1])
                        footer       = embed.footer.text.split(':')
                        member_id    = int(footer[1])

                        for reaction in message.reactions:
                            if reaction.emoji == '❌' and payload.member.id == member_id:
                                await message.clear_reactions()
                            if reaction.emoji == '✅' and reaction.count >= votes_needed:
                                afk_channel = self.bot.get_channel(AFK_VOICE_CHANNEL)
                                guild_member = self.bot.guild.get_member(member_id)
                                await guild_member.move_to(afk_channel)
                                await message.clear_reactions()

    @Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        user = self.bot.get_user(payload.user_id)
        if not user.bot:
            member_dto = MemberDto()
            member_dto.get_member(payload.user_id)
            if member_dto.emojis_xp < 1:
                pass
            member_dto.emojis_xp += -1
            await member_dto.save(self.bot)

    @Cog.listener()
    async def on_member_join(self, member):
        if not member.bot:
            member_dto = MemberDto()
            member_dto.member_id = member.id
            member = self.bot.guild.get_member(member.id)
            await member.add_role(ROLE_NOMAD)
            await member_dto.save(self.bot)
            channel = self.bot.get_channel(int(self.bot.channel))
            await channel.send(f'{member.mention}, bun venit in Romania!')


def setup(bot):
    bot.add_cog(Events(bot))
