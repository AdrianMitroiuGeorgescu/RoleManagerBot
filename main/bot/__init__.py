import os
from asyncio import sleep
from datetime import datetime
from glob import glob

from discord import Embed, Intents, Forbidden
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext.commands import Context, CommandNotFound, CommandOnCooldown, MissingRequiredArgument, MemberNotFound
from dotenv import load_dotenv

from entities.members import MemberDto
from main.bot.readyCogs import Ready
from main.db import Db

load_dotenv()

PREFIX      = '!'
COGS_PREFIX = os.getenv('cogs_prefix')
COGS        = [path.split(COGS_PREFIX)[-1][:-3] for path in glob("cogs/*.py")]


class Bot(commands.Bot):
    def __init__(self):
        self.prefix     = PREFIX
        self.version    = ''
        self.owner_id   = None
        self.guild      = None
        self.token      = None
        self.channel    = None
        self.banlist    = []
        self.ready      = False
        self.cogs_ready = Ready()
        self.scheduler  = AsyncIOScheduler()

        db = Db()
        db.autosave(self.scheduler)

        with open("./lib/bot/owner.token", "r", encoding="utf-8") as ot:
            self.owner_id = list(ot.read())
        super().__init__(
            command_prefix=PREFIX,
            owner_ids=self.owner_id,
            intents=Intents.all()
        )

    # setup
    def setup(self):
        print(COGS)
        for cog in COGS:
            self.load_extension(f"cogs.{cog}")
            print(f"{cog} cog loaded")
        print("Setup complete")

    # run
    def run(self, version):
        self.version = version
        print("Setup starts...")
        self.setup()

        with open("./lib/bot/bot.token", "r", encoding="utf-8") as bt:
            self.token = bt.read()
        print("Running...")
        super().run(self.token, reconnect=False)

    # connect
    async def on_connect(self):
        print("Connected")

    # disconnect
    async def on_disconnect(self):
        print("Disconnected")

    # error
    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("Something went wrong.")
        raise

    # command_error
    async def on_command_error(self, ctx, exc):
        if isinstance(exc, CommandNotFound):
            await ctx.send('This command I do not know')
        elif isinstance(exc, CommandOnCooldown):
            await ctx.send(f'This command is in cooldown for you. Try again in {exc.retry_after:,.2f} secs.')
        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send('Missing required arguments. Please consult !help')
        elif hasattr(exc, 'original'):
            if isinstance(exc.original, Forbidden):
                await ctx.send('I do not have permissions to do that.')
            else:
                raise exc.original
        elif isinstance(exc, MemberNotFound):
            await ctx.send(f'{exc}')
        else:
            raise exc

    # ready
    async def on_ready(self):
        if not self.ready:
            with open("./lib/bot/guild.token", "r", encoding="utf-8") as gt:
                guild = gt.read()
            self.guild = self.get_guild(int(guild))
            self.scheduler.start()

            with open("./lib/bot/channel.token", "r", encoding="utf-8") as ct:
                channel_token = ct.read()
            self.channel = channel_token
            channel      = self.get_channel(int(self.channel))
            embed        = Embed(title="Now online!", description="Your role overlord.")
            await channel.send(embed=embed)

            self.ready = True
            while not self.cogs_ready.allReady:
                await sleep(0.5)
            await self.events_scheduled()
            print("Ready")
        else:
            print("Reconnected")

    # process commands
    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)

        if ctx.command is not None and ctx.guild is not None:
            if int(message.channel.id) != int(self.channel):
                await message.channel.send(f'{message.author.mention}, I can only talk to you here: '
                                           f'{self.get_channel(int(self.channel)).mention}!')
                return

            if message.author.id in self.banlist:
                await ctx.send("You are banned from using commands.")

            elif not self.ready:
                await ctx.send("I'm not ready to receive commands. Please wait a few seconds.")

            else:
                await self.invoke(ctx)

        try:
            if ctx.guild is not None:
                content = message.content
                if len(content) > 1:
                    if content[0] != '!' or content[0] == content[1]:
                        member_dto = MemberDto()
                        member_dto.get_member(message.author.id)
                        member_dto.messages_xp += 1
                        await member_dto.save(self)
        except Exception as e:
            print(f'Timestamp: {datetime.now()}')
            print(f'Exception type: {type(e)}')
            print(f'Message: {message.content}')
            print(f'Exception: {e}\n')

    # message
    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)

    # events_scheduled
    async def events_scheduled(self):
        events = self.get_cog('Schedules')
        events.run_schedules(self.scheduler)


bot = Bot()
