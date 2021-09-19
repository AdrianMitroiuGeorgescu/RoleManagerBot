import os

from entities.configs import ConfigDto
from entities.members import MemberDto
from main.bot import Bot

FIRST_TO_CONNECT_ROLE = int(os.getenv('first_to_connect_role_id'))


async def execute_reset_day(bot: Bot):
    config_dto       = ConfigDto()
    config_dto.name  = config_dto.first_to_connect
    config_dto.get_config(config_dto)
    config_dto.value = '0'
    config_dto.save()

    member_dto = MemberDto()
    filters = [('first_to_voice_channel', 1)]
    member_dto.get_member_by_filters(filters)
    member_dto.first_to_voice_channel = 0
    await member_dto.save(bot)
    member = bot.guild.get_member(member_dto.member_id)
    role   = bot.guild.get_role(int(FIRST_TO_CONNECT_ROLE))
    await member.remove_roles(role)


async def parse_command(command_name: str, bot: Bot):
    executables = {
        'execute_reset_day': await execute_reset_day(bot),
        'retire_members'   : ''
    }
    result = executables[command_name]
