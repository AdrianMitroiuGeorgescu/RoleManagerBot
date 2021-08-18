from discord.ext.commands import Cog, command

from cogs.schedules import Schedules

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
        self.bot = bot

    @command(name='execute_command', help='Triggers a certain method from schedule')
    async def execute_command(self, ctx, command_name: str):
        if command_name not in commands:
            await ctx.send(f'{command_name} is not available. Please use one of those commands: '
                           f'{" ".join([str(elem) for elem in commands])}')
            return
        if ctx.author.id not in admins_ids:
            await ctx.send(f'Only designated admins can run this command')
            return

        class_method  = getattr(Schedules, command_name)
        await class_method()
        await ctx.send('Command executed')


def setup(bot):
    bot.add_cog(Admin(bot))
