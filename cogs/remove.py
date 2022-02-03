import discord
from discord.ext import commands
from typing import Union


class Remove(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_emojis=True)
    async def remove(self, ctx, *emotes: Union[discord.Emoji, str]):

        cmd_type = "cmd_remove"
        successful_removals = 0

        for index, i in enumerate(emotes):

            if not isinstance(i, discord.Emoji):
                embed = discord.Embed(
                    title="That is not an custom emoji",
                    description=f"You need to give me an custom discord emoji (Make sure the emoji that you give is actually in your server)\nYou passed in : {i}",
                )
                await ctx.send(embed=embed)
                continue

            # For security reasons, we need to check if the emoji origin's is the same as ctx.guild
            if not i.guild.id == ctx.guild.id:
                embed = discord.Embed(
                    title="That is not an emoji from this server",
                    description=f"You need to give me an emoji that is actually in your server!",
                )
                await ctx.send(embed=embed)
                continue

            embed = discord.Embed(
                title=f"Removed {i.name}",
                description="Successfully removed the emoji from the server",
            )
            embed.set_footer(
                text=f"{index + 1} of {len(emotes)} to remove {'' if not (index + 1) == len(emotes) else '(over)'}"
            )

            successful_removals += 1
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Remove(bot))
