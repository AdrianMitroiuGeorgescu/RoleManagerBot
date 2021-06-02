import os

from discord import Member, Embed
from discord.ext.commands import Cog, command
from dotenv import load_dotenv

from entities.abouts import AboutDto
from entities.configs import ConfigDto
from entities.levels import LevelDto
from entities.members import MemberDto

load_dotenv()

GODMODE_ROLE_ID = int(os.getenv('god_mode_role_id'))

class Miscellanies(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(os.path.basename(__file__))

    @command(name='add_member', help='Add member from guild into db', hidden=True)
    async def add_member(self, ctx, member: Member):
        roles = ctx.author.roles
        role_ids = []
        for role in roles:
            role_ids.append(role.id)
        if GODMODE_ROLE_ID not in role_ids:
            await ctx.send('You do not have permission to use this command')
            return
        member_dto = MemberDto()
        member_dto.save_member(member.id)
        member_dto = member_dto.get_member(member.id)
        embed      = Embed(title='Member added!')
        fields     = [(
            self.bot.get_user(member_dto.member_id),
            member_dto.xp,
            member_dto.get_member_level().name,
            False
        )]

        for name, xp, level, inline in fields:
            embed.add_field(name=f'Name: {name}', value=f'XP: {xp} - Level: {level}', inline=inline)

        await ctx.send(embed=embed)

    @command(name='add_level', help='Add level into db. Between command and xp needed will be the name', hidden=True)
    async def add_level(self, ctx, name, amount):
        roles = ctx.author.roles
        role_ids = []
        for role in roles:
            role_ids.append(role.id)
        if GODMODE_ROLE_ID not in role_ids:
            await ctx.send('You do not have permission to use this command')
            return
        level     = {'name': name, 'xp_amount': amount}
        level_dto = LevelDto()
        level_dto.save_level(level)

        embed  = Embed(title='Level added!')
        fields = [(level['name'], level['xp_amount'], False)]

        for name, xp_amount, inline in fields:
            embed.add_field(name=f'Name: {name}', value=f'XP_amount: {xp_amount}', inline=inline)

        await ctx.send(embed=embed)

    @command(name='add_all_members', help='Look for all members in the guild and add them to database', hidden=True)
    async def add_all_members(self, ctx):
        roles = ctx.author.roles
        role_ids = []
        for role in roles:
            role_ids.append(role.id)
        if GODMODE_ROLE_ID not in role_ids:
            await ctx.send('You do not have permission to use this command')
            return
        members = ctx.guild.members
        count   = 0
        for member in members:
            member_dto      = MemberDto()
            check_if_exists = member_dto.get_member(member.id)
            if check_if_exists is None:
                member_dto = MemberDto()
                member_dto.save_member(member.id)
                count += 1
        await ctx.send(f'{count} members have been added to database')

    @command(name='add_about', help='Insert a description about something')
    async def add_about(self, ctx, about, *, description):
        if about is None and description is None:
            await ctx.send('Please provide a name followed by a description')

        about_dto             = AboutDto()
        about_dto.name        = about
        about_dto.description = description
        about_dto.member_id   = ctx.author.id
        about_dto.add_about()

        await ctx.send(f'{about_dto.name} was added into database.')

    @command(name='get_xp', help='Returns ')
    async def get_xp(self, ctx):
        pass
        #await ctx.send(embed=embed)

    @command(name='add_config', help='Add config into configs', hidden=True)
    async def add_config(self, ctx, name, value):
        roles    = ctx.author.roles
        role_ids = []
        for role in roles:
            role_ids.append(role.id)
        if GODMODE_ROLE_ID not in role_ids:
            await ctx.send('You do not have permission to use this command')
            return
        config_dto = ConfigDto()
        config_dto.name  = name
        config_dto.value = value
        config_dto.add_config()

        await ctx.send(f'{config_dto.name} config was added')

    @command(name='get_configs', help='Get all configs by name and value', hidden=True)
    async def get_config(self, ctx):
        roles    = ctx.author.roles
        role_ids = []
        for role in roles:
            role_ids.append(role.id)
        if GODMODE_ROLE_ID not in role_ids:
            await ctx.send('You do not have permission to use this command')
            return
        config_dto = ConfigDto()
        configs    = config_dto.get_configs()
        fields     = []

        table  = ("\n".join(
            f"***{config.name}*** *(Value: {config.value})*"
            for idx, config in enumerate(configs)))
        fields.append((":black_small_square:", table))

        embed = Embed(title="Configs", colour=ctx.author.colour)
        embed.set_thumbnail(url=self.bot.guild.me.avatar_url)
        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)

        await ctx.send(embed=embed)

    @command(name='edit_config', help='Edit config by name', hidden=True)
    async def edit_config(self, ctx, name, value):
        roles    = ctx.author.roles
        role_ids = []
        for role in roles:
            role_ids.append(role.id)
        if GODMODE_ROLE_ID not in role_ids:
            await ctx.send('You do not have permission to use this command')
            return

        config_dto       = ConfigDto()
        config_dto.name  = name
        config_dto.get_config(config_dto)

        if config_dto.value is None:
            await ctx.send(f'No config found with name {name}')
            return

        config_dto.value = value
        config_dto.save()
        await ctx.send(f'{config_dto.name} config has been saved. New value {config_dto.value}')


def setup(bot):
    bot.add_cog(Miscellanies(bot))
