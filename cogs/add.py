import discord
from typing import Union, Callable
from discord.ext import commands
from tools.bot_tools import static_vacancy, animated_vacancy, page_index, find_all_emojis
from tools.enum_tools import TableType


class Add(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # TODO: Add error handling to this.
    @commands.command()
    @commands.has_permissions(manage_emojis=True)
    async def add(self, ctx, *emojis: Union[discord.PartialEmoji, str]):

        # We want to log how many emotes were successfully added to the guild
        # We make an success count and increment it on success

        successful_additions: int = 0
        footer_enumer: Callable[[int], str] = page_index("add", len(emojis))

        # It has been found out in a profiling that calling static_vacancy and animated_vacancy
        # is the slowest part of this function, so we will only call them once and store the values of it
        # then decrement them as we go through the loop
        static_vacancy_value: int = static_vacancy(ctx.guild)
        animated_vacancy_value: int = animated_vacancy(ctx.guild)

        # We want to get the bytes-like object of the emojis that is within the strings that may hold emoji IDs
        parsed_emojis: bytes = find_all_emojis("".join(filter(lambda x: isinstance(x, str), emojis)))
        emojis = list(filter(lambda x: isinstance(x, discord.PartialEmoji), emojis))
        # Add these parsed stuff into emojis and we'll handle it along with the Partials
        # It is to be noted that parsed_emojis is NOT an instance of str or discord.PartialEmoji
        emojis: Union[discord.PartialEmoji, bytes] = list(emojis) + await parsed_emojis

        for index, each_emoji in enumerate(emojis):

            # At this point we know that the user has given us a custom emoji or we have an bytes-like object
            # Now we need to check if the guild can accept this emoji
            # To do that we'll check if either vacancy is 0 and if it is then we'll send a message to the user
            if (static_vacancy_value <= 0 and not each_emoji.animated) or (animated_vacancy_value <= 0 and each_emoji.animated):
                # Send a message indicating that the guild cannot accept any more emotes

                # bytes-like objects are caught later on
                # If both vacancy values are 0 then we'll terminate the function definition
                if static_vacancy_value == 0 and animated_vacancy_value == 0:
                    termination = True
                    description = "Your guild is full of emotes, it cannot accept any more of either static or animated emotes, please remove some emotes before trying again"
                else:
                    # The guild isn't full, but it can't accept this emoji
                    # We'll send a message to the user indicating that it can't accept this emoji
                    termination = False
                    description = f"Your guild cannot accept any more of **{'animated' if each_emoji.animated else 'static'}** emotes"

                embed = discord.Embed(
                    title=f"Guild is full",
                    description=description,
                )
                await ctx.send(embed=embed)

                if termination:
                    return
                continue

            # Everything is good to go, persumably anyways
            try:
                reason=f"This emoji was added by {ctx.author} ({ctx.author.id})"
                if isinstance(each_emoji, discord.PartialEmoji):
                    # is a partial emoji
                    image = await each_emoji.read()
                    name = each_emoji.name
                else:
                    # is a bytes-like object
                    image = each_emoji
                    name = "no_name_provided" # Can't get the name of the emoji if it's a bytes-like object
                    reason += "\nThat emoji is unamed btw, you may rename it using this bot :D"
                added_emoji = await ctx.guild.create_custom_emoji(
                    name=name,
                    image=image,
                    reason=reason,
                    
                )
            except (discord.HTTPException, discord.Forbidden):
                return # TODO: Error handling
            else:
                # Success
                # Display the success message.
                embed = discord.Embed(
                    title=f"Successfully added {added_emoji.name}",
                    description=f"Successfully added {added_emoji} to the guild.",
                )
                embed.set_footer(text=footer_enumer(index))
                await ctx.send(embed=embed)

                # Increment success counter
                successful_additions += 1

        await self.bot.tools.increment_usage(ctx, TableType.command)
        await self.bot.tools.increment_usage(
            ctx,
            TableType.rubric,
            successful_additions,
        )


def setup(bot):
    bot.add_cog(Add(bot))
