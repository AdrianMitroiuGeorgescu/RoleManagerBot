from entities.members import MemberDto
from main.bot import Bot


async def games_rewarding(bot: Bot, winner: int, loser: int, stake: int):
    member_winner = MemberDto()
    member_loser  = MemberDto()

    member_winner.get_member(winner)
    member_winner.xp += stake
    await member_winner.save(bot)

    member_loser.get_member(loser)
    member_loser.xp += -stake
    await member_loser.save(bot)
    return


