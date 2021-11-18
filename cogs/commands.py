import asyncio
import os
import random
from math import ceil
from typing import Optional
from aiohttp import request
from discord import Member, Embed
from discord.ext.commands import Cog, command, BadArgument, cooldown, BucketType

from entities.abouts import AboutDto
from entities.levels import LevelDto
from entities.members import MemberDto

AFK_VOICE_CHANNEL      = int(os.getenv('afk_channel_id'))

class Commands(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(os.path.basename(__file__))

    @command(name='about', help='Useful information about something. Cooldown: 10s')
    @cooldown(1, 10, BucketType.user)
    async def about(self, ctx, message: Optional[str] = None):
        about_dto = AboutDto()
        results   = about_dto.get_abouts(message)

        if results is None or not results:
            await ctx.send(f"I know nothing about {message}")
            return
        member_dto = MemberDto()
        member_dto.get_member(ctx.author.id)
        about_dto = random.choice(results)

        embed = Embed(title=f'{about_dto.name}',
                      description=f"{about_dto.description}",
                      colour=ctx.author.color)
        embed.set_footer(text=f'Author - {self.bot.get_user(about_dto.member_id).display_name}',
                         icon_url=self.bot.get_user(about_dto.member_id).avatar_url)
        await ctx.send(embed=embed)

    @command(name='slap', help='Spend points to slap a member. Cooldown: 10s')
    @cooldown(1, 10, BucketType.user)
    async def slap(self, ctx, member: Member, slab_counter: Optional[int] = 1, *, reason: Optional[str] = 'None'):
        await ctx.message.delete()

        member_slapped = MemberDto()
        db_member      = member_slapped.get_member(member.id)
        if db_member is None:
            await ctx.send(f'Member {member.mention} not yet in bot database.')
            return

        slapping_member = MemberDto()
        slapping_member.get_member(ctx.author.id)

        await ctx.send(f'{ctx.author.display_name} slapped {member.mention} {slab_counter} times. Reason: {reason}')

    @command(name='fact', help='Get a random fact. Cooldown: 10s')
    @cooldown(1, 10, BucketType.user)
    async def fact(self, ctx):
        facts  = ['dog', 'cat', 'panda', 'fox', 'bird', 'koala']
        choice = random.choice(facts)
        url    = f'https://some-random-api.ml/facts/{choice}'
        async with request('GET', url, headers={}) as response:
            if response.status == 200:
                data  = await response.json()
                embed = Embed(title=f'{choice}', description=f"{data['fact']}")
                await ctx.send(embed=embed)
            else:
                ctx.send(f'API returned a {response.status} status.')

    @slap.error
    async def slap_error(self, ctx, exc):
        if isinstance(exc, BadArgument):
            await ctx.send('I can`t find that member')

    @command(name='xp', aliases=['level'], help='Returns your level and current xp')
    async def xp(self, ctx):
        member_dto   = MemberDto()
        member_dto.set_member(ctx.author.id)
        member_level = member_dto.get_member_level()
        level_name   = member_level.name
        next_level   = LevelDto()
        next_level   = next_level.get_next_level(member_dto.total_xp)
        xp_needed    = int(next_level.xp_amount - member_dto.total_xp)
        embed = Embed(title=f'{ctx.message.author.display_name}',
                      description=f'Your level is: {level_name} and you have {member_dto.total_xp} XP. \n'
                                  f' XP needed until next level: {xp_needed}')
        await ctx.send(embed=embed)

    @command(name='levels', help='Returns all levels in this guild')
    async def levels(self, ctx):
        level_dto = LevelDto()
        levels    = level_dto.get_levels()
        fields    = []

        table = ("\n".join(
            f"***{level.name}*** *(XP: {level.xp_amount})*"
            for idx, level in enumerate(levels)))
        fields.append((":black_small_square:", table))

        embed = Embed(title="Levels", colour=ctx.author.colour)
        embed.set_thumbnail(url=self.bot.guild.me.avatar_url)
        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)

        await ctx.send(embed=embed)

    @command(name='kick', pass_context=True)
    async def kick(self, ctx, member: Member):
        if ctx.author.voice is None:
            await ctx.send('You must be in the same voice channel as the member you want to kick!')
            return

        votes_received = 0
        voice_channel  = ctx.author.voice.channel
        members_found  = voice_channel.members

        members_id = []
        for member_found in members_found:
            members_id.append(member_found.id)

        if member.id not in members_id:
            await ctx.send('You must be in the same voice channel as the member you want to kick!')
            return

        votes_needed = ceil(0.4 * len(members_id))
        embed        = Embed(
            title=f'Kick {member.display_name}',
            description=f'Votes needed: {votes_needed + 1}'
        )
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        react = await ctx.send(embed=embed)
        for reaction in ['✅']:
            await react.add_reaction(reaction)

        try:
            while votes_received < votes_needed:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=10, check=check_vote)
                if str(reaction) == '✅':
                    votes_received += 1
            if votes_received >= votes_needed:
                await react.clear_reactions()
                for reaction in ['❌']:
                    await react.add_reaction(reaction)
                await ctx.send(f'{member.mention} the kick proposal has passed. If you are active please react!')
                try:
                    def check_present(reaction, user):
                        return user == member and str(reaction.emoji) in ['✅', '❌']
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=10, check=check_present)
                    if str(reaction) == '❌':
                        embed.add_field(name=f'{member.display_name}', value='Is still here', inline=True)
                        await react.edit(embed=embed)
                        await react.clear_reactions()
                except asyncio.TimeoutError:
                    afk_channel = self.bot.get_channel(AFK_VOICE_CHANNEL)
                    guild_member = self.bot.guild.get_member(member.id)
                    if guild_member.voice is None:
                        await react.clear_reactions()
                        return
                    await guild_member.edit(voice_channel=afk_channel)
                    embed.add_field(name=f'{member.display_name}', value='Has been send to afk channel', inline=True)
                    await react.edit(embed=embed)
                    await react.clear_reactions()
        except asyncio.TimeoutError:
            embed.add_field(name=f'{member.display_name}', value='Kick vote did not passed', inline=True)
            await react.edit(embed=embed)
            await react.clear_reactions()


def check_vote(reaction, user):
    return str(reaction.emoji) in ['✅', '❌']


def setup(bot):
    bot.add_cog(Commands(bot))
