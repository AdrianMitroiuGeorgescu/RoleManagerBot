import asyncio
import random

from discord import Embed, Message

from entities.members import MemberDto
from main.bot import Bot


async def check_barbut_command(bot: Bot, embed: Embed, message: Message, payload):
    description        = embed.description.split(':')
    stake_is           = int(description[1])
    footer             = embed.footer.text.split(':')
    player_one         = int(footer[2])
    player_name        = None
    rolled_first_value = None

    if payload.member.id != player_one:
        return

    if payload.emoji.name == '❌':
        embed.add_field(name=f'{payload.member.display_name}', value='Nu a acceptat invitația', inline=True)
        embed.set_footer(text="")
        await message.edit(embed=embed)
        await message.clear_reactions()
        return

    if payload.emoji.name == '🎲' and payload.member.id == player_one and 0 != len(embed.fields):

        if embed.fields:
            for field in embed.fields:
                player_name        = field.name
                rolled_first_value = int(field.value)
        else:
            return

        discord_member = bot.guild.get_member(payload.member.id)
        roll           = random.randrange(1, 100)
        embed.add_field(name=f'{discord_member.display_name}', value=str(roll), inline=True)
        await message.edit(embed=embed)

        if rolled_first_value > roll:
            embed.add_field(name=f':crown: Câștigătorul este {player_name}',
                            value=f'A câștigat {stake_is} XP',
                            inline=False)
            await games_rewarding(bot, player_one, payload.member.id, stake_is)
        elif rolled_first_value < roll:
            embed.add_field(name=f':crown: Câștigătorul este {payload.member.display_name}',
                            value=f'A câștigat {stake_is} XP',
                            inline=False)
            await games_rewarding(bot, payload.member.id, player_one, stake_is)
        elif rolled_first_value == roll:
            embed.add_field(name=':crown: Egalitate', value='Nimeni nu a câștigat', inline=False)

        embed.set_footer(text="")
        await message.edit(embed=embed)
        await message.clear_reactions()
        return


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
