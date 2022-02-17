import disnake as discord
from datetime import datetime
from disnake.ext import commands
from tools.enum_tools import TableType


class PatchedContext(commands.Context):
    def _get_patch_message(self, content):
        msg = "This command was invoked by an edit"
        return msg if content is None else f"{msg}\n{content}"

    def send(self, content=None, **kwargs):
        return super().send(self._get_patch_message(content), **kwargs)

    def reply(self, content=None, **kwargs):
        return self.send(self._get_patch_message(content), **kwargs)


class Handler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        await self.bot.tools.increment_usage(ctx, TableType.command)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        # If a message is edited multiple times,
        # we should only count the last edit
        delta_sec = datetime.now().timestamp() - before.created_at.timestamp()
        if before.content == after.content or delta_sec > 35:
            # We won't take any actions if previous message is same as new
            # or if the the time elapsed from the initial message is greater than 35 seconds
            return
        # See if what is being edited is a actually a command
        # if it is a command then we will react with a retry emoji
        # to provoke the user to resend the command
        # if the user does not respond within 35 seconds, the bot will time this out
        if not after.content.startswith(
            await self.bot.cache.get_prefix(TableType.guilds, after.guild.id)
        ):
            return
        await after.add_reaction("🔁")
        self.bot.interim.add(after, 35)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        for i in self.bot.interim.get_list()[::-1]:
            # Traversing through the reversed heap means that
            # the first match will be the last edit made to the message
            if (
                i.id == payload.message_id
                and payload.emoji.name == "🔁"
                and payload.user_id == i.author.id
            ):
                ctx = await self.bot.get_context(i, cls=PatchedContext)
                await self.bot.invoke(ctx)
                # We are done with processing the last edit made
                # We would now end the function definition
                return


def setup(bot):
    bot.add_cog(Handler(bot))
