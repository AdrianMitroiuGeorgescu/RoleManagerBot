import datetime
import os
from random import randrange
from typing import Optional

from discord import Embed, Member
from discord.ext.commands import Cog, command
from discord.ext.menus import ListPageSource, MenuPages

from entities.levels import LevelDto
from entities.members import MemberDto


class HelpMenu(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx

        super().__init__(data, per_page=10)

    async def write_page(self, menu, offset, fields=[]):
        len_data = len(self.entries)

        embed = Embed(title="XP Leaderboard",
                      colour=self.ctx.author.colour)
        embed.set_thumbnail(url=self.ctx.guild.me.avatar_url)
        embed.set_footer(text=f"{offset:,} - {min(len_data, offset + self.per_page - 1):,} of {len_data:,} members.")

        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, entries):
        offset = (menu.current_page * self.per_page) + 1
        fields = []
        for idx, entry in enumerate(entries):
            if self.ctx.bot.guild.get_member(entry.member_id) is None:
                continue
            display_name = self.ctx.bot.guild.get_member(entry.member_id).display_name
            level_dto    = LevelDto()
            level_dto.get_level(entry.level_id)
            table        = f'{entry.total_xp} XP » :lips: {entry.xp // 4} h' \
                           f':black_small_square: :pencil: {entry.messages_xp} ' \
                           f':black_small_square: :joy: {entry.emojis_xp // 2} ' \
                           f':black_small_square: :cinema: {entry.web_xp // 4} h' \
                           f':black_small_square: :desktop: {entry.share_xp // 4} h\n'
            fields.append((f"{idx + offset}. {display_name} *[{level_dto.name}]*", table))

        return await self.write_page(menu, offset, fields)


class Xp(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(os.path.basename(__file__))

    @command(name="leaderboard", aliases=['top'])
    async def leaderboard(self, ctx):
        member_dto = MemberDto()
        results    = member_dto.get_leaderboard()
        menu       = MenuPages(source=HelpMenu(ctx, results),
                               clear_reactions_after=True,
                               timeout=60.0)
        await menu.start(ctx)

    @command(name='steal')
    async def steal(self, ctx):
        member_dto = MemberDto()
        member_dto.get_member(ctx.author.id)

        if member_dto.steal_flag != 1:
            await ctx.send(f'{ctx.author.mention}, You were not prepared to steal any xp!')
            return

        time = datetime.datetime.now() - member_dto.steal_time
        if time.seconds > 15:
            member_dto.steal_flag = 0
            await member_dto.save(self.bot)
            await ctx.send(f'{ctx.author.mention}, You were caught stealing xp and lost 2 xp!')
            return

        xp_stolen = randrange(50)
        member_dto.steal_flag = 0
        await member_dto.save(self.bot)

        leader = MemberDto()
        leader.get_leader()
        await member_dto.save(self.bot)
        await ctx.send(f'{ctx.author.mention} stole {xp_stolen} xp from {self.bot.get_user(leader.member_id).mention}!')

    @command(name='stop_the_heist')
    async def stop_the_heist(self, ctx):
        member_dto = MemberDto()
        member_dto.get_member(ctx.author.id)
        leader = MemberDto()
        leader.get_leader()
        thief = MemberDto()
        thief.get_thief()

        if member_dto.member_id != leader.member_id:
            await ctx.send(f'{ctx.author.mention}, Only the leader can defend the xp!')
            return

        time = datetime.datetime.now() - thief.steal_time
        if time.seconds > 10:
            await ctx.send(f'{ctx.author.mention}, You were too late to stop the thief!')
            return

        thief.steal_flag = 0
        await thief.save(self.bot)
        await ctx.send(f'{ctx.author.mention} got home in time to stop the heist! '
                       f'{self.bot.get_user(thief.member_id).mention}, you can`t steal xp anymore!')

    @command(name='get_xp', help='Returns xp and total xp of a member or of the requester if no member is given')
    async def get_xp(self, ctx, member: Optional[Member] = None):
        member_dto = MemberDto()

        if member is None:
            member_dto.get_member(ctx.author.id)
            message = f'You have {member_dto.xp} amount of xp (currency) and a total of {member_dto.total_xp} xp'
        else:
            member_dto.get_member(member.id)
            message = f'{member.mention} has {member_dto.xp} amount of xp  (currency) ' \
                      f'and a total of {member_dto.total_xp} xp'
        await ctx.send(message)


def setup(bot):
    bot.add_cog(Xp(bot))
