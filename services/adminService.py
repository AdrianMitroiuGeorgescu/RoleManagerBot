from entities.members import MemberDto
from main.bot import Bot


async def transfer_xp(bot: Bot, from_member: MemberDto, to_member: MemberDto, amount: int):
    from_member.xp += -amount
    await from_member.save(bot)

    to_member.xp += amount
    await to_member.save(bot)
