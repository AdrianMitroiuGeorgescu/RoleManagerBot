import asyncio
import random

import discord
from discord import Member
from discord.ext import commands
from typing import Optional
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option

from entities.members import MemberDto
from services import memberService, gameService


class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.memberService = memberService
        self.gameService = gameService

    @cog_ext.cog_slash(name="fmm", description='okbine')
    async def fmm(self, ctx: SlashContext):
        await ctx.send(content="dada")

    @cog_ext.cog_slash(name="fmm2", description='okbine2')
    async def fmm(self, ctx: SlashContext):
        await ctx.send(content="dada2")

    @cog_ext.cog_slash(name='get_xp2',
                       description='Returns xp and total xp of a member or of the requester if no member is given',
                       options=[
                           create_option(
                               name="member",
                               description="Userul de la care vrei sa vezi xp",
                               required=False,
                               option_type=6,
                           )
                       ])
    async def get_xp2(self, ctx: SlashContext, member: Optional[Member] = None):
        member_dto = MemberDto()

        if member is None:
            member_dto.get_member(ctx.author.id)
            message = f'You have {member_dto.xp} amount of xp (currency) and a total of {member_dto.total_xp} xp'
        else:
            member_dto.get_member(member.id)
            message = f'{member.mention} has {member_dto.xp} amount of xp  (currency) ' \
                      f'and a total of {member_dto.total_xp} xp'
        await ctx.send(message)

    @cog_ext.cog_slash(name='barbut2',
                       description='Returns xp and total xp of a member or of the requester if no member is given',
                       options=[
                           create_option(
                               name="member",
                               description="Userul de la care vrei sa vezi xp",
                               required=True,
                               option_type=6,
                           ),
                           create_option(
                               name="stake_is",
                               description="Pe cât xp vrei să joci?",
                               required=True,
                               option_type=4,
                           )
                       ])
    async def barbut(self, ctx: SlashContext, member: Member, stake_is: int):

        if ctx.author.id == member.id:
            await ctx.send('Jocul ăsta se joacă în doi!')
            return
        elif not self.memberService.check_minimum_xp(ctx.author.id, stake_is) \
                or not self.memberService.check_minimum_xp(member.id, stake_is):
            await ctx.send('Nu aveți bani de barbut!')
            return

        reactions = ['🎲', '❌']
        embed = discord.Embed(
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
    bot.add_cog(Slash(bot))
