import asyncio
import os
import random

from discord import Member, Embed
from discord.ext.commands import Cog, command
from dotenv import load_dotenv

from entities.members import MemberDto
from services.eventsService import games_rewarding

load_dotenv()


class Games(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(os.path.basename(__file__))

    @command(name='barbut', pass_context=True, help='Poți juca barbut cu un membru la alegere')
    async def barbut(self, ctx, member: Member, stake_is: int):

        challenger_member = MemberDto()
        challenger_member.get_member(ctx.author.id)

        invited_member = MemberDto()
        invited_member.get_member(member.id)

        if ctx.author.id == member.id:
            await ctx.send('Jocul ăsta se joacă în doi!')
            return
        elif invited_member.xp < stake_is or challenger_member.xp < stake_is:
            await ctx.send('Nu aveți bani de barbut!')
            return

        reactions = ['🎲', '❌']
        embed = Embed(
            title=f'Joci barbut, {member.display_name}?',
            description=f'Miza este de: {stake_is}'
        )
        embed.set_thumbnail(url='https://i.ibb.co/9hrZBnc/Untitled.jpg')
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.set_footer(text=f':Player one: {ctx.author.id}:\n'
                              f':Player two: {member.id}:')
        react = await ctx.send(embed=embed)
        for reaction in reactions:
            await react.add_reaction(reaction)

        def check(reaction, user):
            return user == member and str(reaction.emoji) == '🎲'
        try:
            await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
            roll = random.randrange(1, 100)
            embed.add_field(name=f'{member.display_name}', value=str(roll), inline=True)
            await react.edit(embed=embed)

            await react.clear_reactions()
            reactions = ['🎲']
            for reaction in reactions:
                await react.add_reaction(reaction)

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) == '🎲'

            try:
                await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
            except asyncio.TimeoutError:
                embed.add_field(name=f'{ctx.author.display_name}', value='Predat', inline=True)
                embed.add_field(name=f':crown: Câștigătorul este {member.display_name}',
                                value=f'A câștigat {stake_is} XP', inline=False)
                print('se face plata catre castigator')
                await games_rewarding(self.bot, member.id, ctx.author.id, stake_is)

                embed.set_footer(text="")
                await react.edit(embed=embed)
                await react.edit(embed=embed)
                await react.clear_reactions()
                return

        except asyncio.TimeoutError:
            embed.add_field(name=f'{member.display_name}', value='Nu a acceptat invitația', inline=True)
            embed.set_footer(text="")

            await react.edit(embed=embed)
            await react.clear_reactions()


def setup(bot):
    bot.add_cog(Games(bot))
