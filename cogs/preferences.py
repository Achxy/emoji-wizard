import discord
from discord.ext import commands
from typing import Union



class Preferences(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ignore(self, ctx, *channels : Union[discord.TextChannel,int,  str]):
        """
        Ignores a text channel(s)
        This command will work in regardless of whether the channel is ignored.
        """

        for each_channel in channels:
            former = each_channel[:] if not isinstance(each_channel, discord.TextChannel) else None
            if isinstance(each_channel, int):
                each_channel = self.bot.get_channel(each_channel)
                if each_channel is None:
                    await ctx.send(f"Channel with id **{former}** does not exist")
                    continue
            if isinstance(each_channel, str):
                each_channel = discord.utils.get(ctx.guild.text_channels, name=each_channel)
                if each_channel is None:
                    await ctx.send(f"Channel with name **{former}** does not exist")
                    continue

            # At this poit we do have a valid channel
            # Now we need to know if the channel actually exists in the guild
            # This is to prevent anyone from misusing the bot
                
            if each_channel not in ctx.guild.text_channels:
                await ctx.send(f"Channel **{each_channel.name}** does not exist in this guild")
                continue

            # Check if the channel is already ignored
            if not await self.bot.tools.is_preferred_channel(ctx.guild.id, each_channel.id):
                await ctx.send(f"Channel {each_channel.mention} is already ignored")
                continue

            # Now we can safely ignore the channel
            await self.bot.tools.ignore_channel(ctx.guild.id, each_channel.id)
            # Now we can send a message to the channel
            await ctx.send(f"Successfully ignored {each_channel.mention}")


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unignore(self, ctx, *channel : Union[discord.TextChannel, int, str]):
        """
        Unignores a text channel(s)
        This command will work in regardless of whether the channel is ignored.
        """
            
        for each_channel in channel:
            former = each_channel[:] if not isinstance(each_channel, discord.TextChannel) else None
            if isinstance(each_channel, int):
                each_channel = self.bot.get_channel(each_channel)
                if each_channel is None:
                    await ctx.send(f"Channel with id **{former}** does not exist")
                    continue
            if isinstance(each_channel, str):
                each_channel = discord.utils.get(ctx.guild.text_channels, name=each_channel)
                if each_channel is None:
                    await ctx.send(f"Channel with name **{former}** does not exist")
                    continue

            # At this poit we do have a valid channel
            # Now we need to know if the channel actually exists in the guild
            # This is to prevent anyone from misusing the bot
                
            if each_channel not in ctx.guild.text_channels:
                await ctx.send(f"Channel **{each_channel.name}** does not exist in this guild")
                continue

            # Check if the channel is already not ignored
            if await self.bot.tools.is_preferred_channel(ctx.guild.id, each_channel.id):
                await ctx.send(f"Channel {each_channel.mention} is not ignored in the first place")
                continue
            # Now we can safely unignore the channel
            await self.bot.tools.unignore_channel(ctx.guild.id, each_channel.id)
            # Now we can send a message to the channel
            await ctx.send(f"Successfully unignored {each_channel.mention}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def enable(self, ctx, *command : commands.Command):
        """
        Enables a command(s)
        """
        for each_command in command:
            if each_command not in filter(lambda x: not x.hidden, [cmd.name for cmd in self.bot.commands]):
                # The command does not exist
                await ctx.send(f"Command **{each_command}** does not exist")
                continue
            # Check if the command is already enabled
            if await self.bot.tools.is_enabled(ctx.guild.id, each_command.name):
                await ctx.send(f"Command **{each_command}** is already enabled")
                continue
            # Now we can safely enable the command
            await self.bot.tools.enable_command(ctx.guild.id, each_command.name)
            # Now we can send a message to the channel
            await ctx.send(f"Successfully enabled command **{each_command}**")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def disable(self, ctx, *command : commands.Command):
        """
        Disables a command(s)
        """
        for each_command in command:
            if each_command not in filter(lambda x: not x.hidden, [cmd.name for cmd in self.bot.commands]):
                # The command does not exist
                await ctx.send(f"Command **{each_command}** does not exist")
                continue
            # Check if the command is already disabled
            if not await self.bot.tools.is_enabled(ctx.guild.id, each_command.name):
                await ctx.send(f"Command **{each_command}** is already disabled")
                continue
            # Now we can safely disable the command
            await self.bot.tools.disable_command(ctx.guild.id, each_command.name)
            # Now we can send a message to the channel
            await ctx.send(f"Successfully disabled command **{each_command}**")

def setup(bot):
    bot.add_cog(Preferences(bot))