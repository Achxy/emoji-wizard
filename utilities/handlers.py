import disnake as discord
import asyncio
from disnake.ext import commands
from tools.enum_tools import TableType


class Handler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        await self.bot.tools.increment_usage(ctx, TableType.command)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        # TODO: Make a seperate listener for this for fine grained control
        # This is safe enough to pushed for now
        # Edge case:
        # If a message is edited multiple times, the bot will count all of it
        # we should only count the last edit
        # We will make interim class later, this is okay for now
        if before.content == after.content:
            return

        # See if what is being edited is a actually a command
        # if it is a command then we will react with a retry emoji
        # to provoke the user to resend the command
        # if the user does not respond within 20 minutes then we will timeout
        if not after.content.startswith(
            await self.bot.cache.get_prefix(TableType.guilds, after.guild.id)
        ):
            return
        await after.add_reaction("🔁")
        try:
            await self.bot.wait_for(
                "raw_reaction_add",
                check=lambda p: p.message_id == after.id
                and p.user_id == after.author.id
                and p.emoji.name == "🔁",
                timeout=60 * 20,
            )
        except asyncio.TimeoutError:
            return
        else:
            await self.bot.process_commands(after)


def setup(bot):
    bot.add_cog(Handler(bot))
