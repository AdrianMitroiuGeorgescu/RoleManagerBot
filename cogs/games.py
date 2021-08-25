import asyncio
import os
import random
import services.memberService as memberService
import services.gameService as gameService

from discord import Member, Embed
from discord.ext.commands import Cog, command
from dotenv import load_dotenv

load_dotenv()


class Games(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.memberService = memberService
        self.gameService = gameService

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(os.path.basename(__file__))

    @command(name='barbut', pass_context=True, help='Poți juca barbut cu un membru la alegere')
    async def barbut(self, ctx, member: Member, stake_is: int):

        if ctx.author.id == member.id:
            await ctx.send('Jocul ăsta se joacă în doi!')
            return
        elif not self.memberService.check_minimum_xp(ctx.author.id, stake_is) \
                or not self.memberService.check_minimum_xp(member.id, stake_is):
            await ctx.send('Nu aveți bani de barbut!')
            return

        reactions = ['🎲', '❌']
        embed = Embed(
            title=f'Joci barbut, {member.display_name}?',
            description=f'Miza este de: {stake_is}'
        )
        embed.set_thumbnail(url='https://i.ibb.co/9hrZBnc/Untitled.jpg')
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        react = await ctx.send(embed=embed)
        for reaction in reactions:
            await react.add_reaction(reaction)

        def check(reaction, user):
            return user == member and str(reaction.emoji) in ['🎲', '❌']

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)

            if str(reaction) == '❌':
                embed.add_field(name=f'{member.display_name}', value='Nu a acceptat invitația', inline=True)
                await react.edit(embed=embed)
                await react.clear_reactions()
                return

            invited_roll = random.randrange(1, 100)
            embed.add_field(name=f'{member.display_name}', value=str(invited_roll), inline=True)
            await react.edit(embed=embed)

            await react.clear_reactions()
            reactions = ['🎲']
            for reaction in reactions:
                await react.add_reaction(reaction)

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) == '🎲'
            try:
                await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
                challenger_roll = random.randrange(1, 100)
                embed.add_field(name=f'{ctx.author.display_name}', value=str(challenger_roll), inline=True)
                await react.edit(embed=embed)

                if invited_roll > challenger_roll:
                    name  = ':crown: Câștigătorul este %s' % (member.display_name)
                    value = 'A câștigat %d XP' % (stake_is)
                    await self.gameService.games_rewarding(self.bot, member.id, ctx.author.id, stake_is)
                elif invited_roll < challenger_roll:
                    name  = ':crown: Câștigătorul este %s' % (ctx.author.display_name)
                    value = 'A câștigat %d XP' % (stake_is)
                    await self.gameService.games_rewarding(self.bot, ctx.author.id, member.id, stake_is)
                else:
                    name  = ':crown: Egalitate'
                    value = 'Nimeni nu a câștigat'

                embed.add_field(name=name, value=value, inline=False)
                await react.edit(embed=embed)
                await react.clear_reactions()
                return

            except asyncio.TimeoutError:
                embed.add_field(name=f'{ctx.author.display_name}', value='Predat', inline=True)
                embed.add_field(name=f':crown: Câștigătorul este {member.display_name}',
                                value=f'A câștigat {stake_is} XP', inline=False)
                await self.gameService.games_rewarding(self.bot, member.id, ctx.author.id, stake_is)
                await react.edit(embed=embed)
                await react.clear_reactions()
                return

        except asyncio.TimeoutError:
            embed.add_field(name=f'{member.display_name}', value='Nu a acceptat invitația', inline=True)
            await react.edit(embed=embed)
            await react.clear_reactions()


def setup(bot):
    bot.add_cog(Games(bot))
