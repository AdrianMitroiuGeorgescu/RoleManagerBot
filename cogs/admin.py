from discord import Member
from discord.ext.commands import Cog, command

import services.schedulesService as ScheduleService
import services.adminService as AdminService
from entities.members import MemberDto

commands = [
    'execute_reset_day',
    'retire_members'
]
admins_ids = [
    202021695685394433,
    267805388542443521
]


class Admin(Cog):
    def __init__(self, bot):
        self.bot              = bot
        self.schedule_service = ScheduleService
        self.admin_service    = AdminService

    @command(name='execute_command', help='Triggers a certain method from schedule')
    async def execute_command(self, ctx, command_name: str):
        if command_name not in commands:
            await ctx.send(f'{command_name} is not available. Please use one of those commands: '
                           f'{" ".join([str(elem) for elem in commands])}')
            return
        if ctx.author.id not in admins_ids:
            await ctx.send(f'Only designated admins can run this command')
            return

        await self.schedule_service.parse_command(command_name, self.bot)
        await ctx.send('Command executed')

    @command(name='xp_police', help='Recovers a certain amount of xp from a member to another')
    async def xp_police(self, ctx, from_member: Member, to_member: Member, amount: int):
        if ctx.author.id not in admins_ids:
            await ctx.send(f'Only designated admins can run this command')
            return

        from_member_dto = MemberDto()
        from_member_dto.get_member(int(from_member.id))
        to_member_dto   = MemberDto()
        to_member_dto.get_member(int(to_member.id))

        if from_member_dto.xp < amount:
            ctx.send(f'There is a mistake. {from_member.mention} does not have {amount} amount of xp')
            return

        await self.admin_service.transfer_xp(self.bot, from_member_dto, to_member_dto, amount)
        await ctx.send('Command executed')

    @command(name='move_message_xp_to_xp', help='Temporary command that moves all xp from messages to xp as currency')
    async def move_message_xp_to_xp(self, ctx):
        if ctx.author.id not in admins_ids:
            await ctx.send(f'Only designated admins can run this command')
            return

        member_dto = MemberDto()
        members    = member_dto.get_leaderboard()

        for member in members:
            if isinstance(member, MemberDto):
                member.xp += member.messages_xp
                await member.save(self.bot)
                discord_member = self.bot.guild.get_member(int(member.member_id))
                await ctx.send(f'{discord_member.mention} message xp was converted into currency')


def setup(bot):
    bot.add_cog(Admin(bot))
