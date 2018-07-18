import discord
from discord.ext import commands

class Mod:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases['purge'])
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def prune(self, ctx, amount: int, channel: discord.TextChannel = None):
        """Delete X messages in specified channel.
        Defaults to current channel if none was specified."""
        if channel == None:
            channel = ctx.channel
        msgs = []
        async for msg in channel.history(limit=amount + 1):
            msgs.append(msg)
        try:
            await channel.delete_messages(msgs)
            await ctx.send("Deleted {} {} in {}.".format(amount, "message" if len(msgs) == 2 else "messages", channel.mention))
        except discord.ClientException:
            await ctx.send("The number of messages to delete is more than 100.")
        except discord.HTTPException:
            await ctx.send("Failed to delete messages, somehow.")

def setup(bot):
    bot.add_cog(Mod(bot))