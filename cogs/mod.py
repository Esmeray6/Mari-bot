import discord
from discord.ext import commands

class Mod:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['purge'])
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
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

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason = None):
        if member == ctx.author:
            await ctx.send(" You are not allowed to kick " + ctx.author.mention + '.')
            return
        if ctx.author.top_role < member.top_role:
            await ctx.send("Your highest role is lower than the member's one. I can't let you kick them.")
            return
        elif ctx.author.top_role == member.top_role:
            await ctx.send("Your highest role is the same as the member's one. I can't let you kick them.")
            return
        elif ctx.guild.me.top_role < member.top_role:
            await ctx.send("My highest role is lower than the member's one. I can't kick them.")
            return
        elif ctx.guild.me.top_role == member.top_role:
            await ctx.send("My highest role is the same as the member's one. I can't kick them.")
        if reason == None:
            reason = "Reason was not specified."
        try:
            await member.kick(reason=reason + ' -' + '{0.name}#{0.discriminator}'.format(ctx.author))
            await ctx.send("Kicked {0.name}#{0.discriminator}".format(member))
        except discord.Forbidden:
            await ctx.send("Couldn't kick the user.") # Because full error handling is important. :^)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, days: str, member: str = None, *, reason = None):
        """Ban member from current server and delete their messages from the server for X days. If you specify a member in "days" argument, the member will be banned and their messages for 1 day will be deleted."""
        if days.isdigit():
            days = int(days)
            try:
                member = await commands.MemberConverter().convert(ctx, member)
            except commands.CommandError:
                await ctx.send("No member found.")
            if reason == None:
                reason = 'Reason was not specified.'
            await member.ban(delete_message_days=days, reason=str(reason) + ' -' + '{0.name}#{0.discriminator}'.format(ctx.author))
            await ctx.send("Banned {0.name}#{0.discriminator}.".format(member))
        else:
            try:
                days = await commands.MemberConverter().convert(ctx, days)
                member = days
                if reason == None:
                    reason = 'Reason was not specified.'
                await member.ban(delete_message_days=1, reason=str(reason) + ' -' + '{0.name}#{0.discriminator}'.format(ctx.author))
                await ctx.send("Banned {0.name}#{0.discriminator}.".format(member))
            except commands.CommandError:
                await ctx.send("No member found.")


def setup(bot):
    bot.add_cog(Mod(bot))