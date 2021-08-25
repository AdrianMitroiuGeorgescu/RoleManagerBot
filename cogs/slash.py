from discord.ext.commands import Cog
from discord_slash import cog_ext, SlashContext

with open("./lib/bot/guild.token", "r", encoding="utf-8") as gt:
    guild = gt.read()
GUILD_ID = [int(guild)]


class Slash(Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="ceva", guild_ids=GUILD_ID)
    async def ceva(self, ctx: SlashContext):
        await ctx.send(content="test")

    @cog_ext.cog_slash(name="ping", guild_ids=GUILD_ID)
    async def ping(self, ctx: SlashContext):
        await ctx.send(content="Pong")


def setup(bot):
    bot.add_cog(Slash(bot))
