import random

from entities.members import MemberDto


class EventsServices:

    async def check_barbut_command(self, bot, embed, message, payload):
        description = embed.description.split(':')
        stake_is = int(description[1])
        footer = embed.footer.text.split(':')
        player_one = int(footer[2])
        player_two = int(footer[5])
        allready_rolled = []
        player_name = None
        player_value = None
        last_player_id = player_one

        if payload.emoji.name == '❌' and payload.member.id in [player_one, player_two]:
            await message.clear_reactions()
            return

        if payload.emoji.name == '✅' and payload.member.id == player_two:
            await message.clear_reactions()
            reactions = ['🎲']
            for reaction in reactions:
                await message.add_reaction(reaction)
            return

        if embed.fields:
            for field in embed.fields:
                allready_rolled.append(field.name)
                player_name = field.name
                player_value = int(field.value)

        if payload.member.id == player_one:
            last_player_id = player_two

        if payload.emoji.name == '🎲' and payload.member.id in [player_one,
                                                                player_two] and payload.member.display_name not in allready_rolled:
            discord_member = bot.guild.get_member(payload.member.id)
            roll = random.randrange(1, 100)
            embed.add_field(name=f'{discord_member.display_name}', value=roll, inline=True)
            await message.edit(embed=embed)
            if 1 <= len(allready_rolled):

                if player_value > roll:
                    embed.add_field(name=f':crown: Câștigătorul este {player_name}', value=f'A câștigat {stake_is} XP',
                                    inline=False)
                    await self.games_rewarding(bot, last_player_id, payload.member.id, stake_is)
                elif player_value < roll:
                    embed.add_field(name=f':crown: Câștigătorul este {payload.member.display_name}',
                                    value=f'A câștigat {stake_is} XP', inline=False)
                    await self.games_rewarding(bot, payload.member.id, last_player_id, stake_is)
                elif player_value == roll:
                    embed.add_field(name=':crown: Egalitate', value='Nimeni nu a câștigat', inline=False)

                await message.edit(embed=embed)
                await message.clear_reactions()
            return

    async def games_rewarding(self, bot, winner: int, loser: int, stake: int):
        member_winner = MemberDto()
        member_loser = MemberDto()

        member_winner.get_member(winner)
        member_winner.xp += stake
        await member_winner.save(bot)

        member_loser.get_member(loser)
        member_loser.xp += -stake
        await member_loser.save(bot)
