import discord
from discord.ext import commands

class Mod:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def hackban(self, ctx, user_id: int, *, reason = None):
        """Ban the user that is not in the current server."""
        reason = reason or "Reason was not specified."
        try:
            user = await self.bot.get_user_info(user_id)
        except discord.NotFound:
            await ctx.send("No user with that user ID was found.")
            return
        try:
            ban_status = await ctx.guild.get_ban(user)
            await ctx.send("{} is banned already.".format(user))
            return
        except discord.NotFound:
            pass
        if user.id == self.bot.user.id:
            await ctx.send("Why are you trying to hackban me?")
            return
        elif user.id == ctx.author.id:
            await ctx.send("Why are you trying to hackban yourself?")
            return
        else:
            await ctx.guild.ban(user, reason = reason, delete_message_days = 0)
            await ctx.send("{} was banned from the server.".format(user))

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        """Unban the banned user."""
        try:
            user = await self.bot.get_user_info(user_id)
        except discord.NotFound:
            await ctx.send("No user with that user ID was found.")
            return
        try:
            ban_status = await ctx.guild.get_ban(user)
        except discord.NotFound:
            await ctx.send("{} is not banned.".format(user))
            return
        await ctx.guild.unban(user, reason="Unbanned by {}".format(ctx.author))
        await ctx.send("Unbanned {}.".format(user))

    @commands.command(aliases=['purge'])
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def prune(self, ctx, amount: int, channel: discord.TextChannel = None):
        """Delete X messages in specified channel.
        Defaults to current channel if none was specified."""
        channel = channel or ctx.channel
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
    @commands.bot_has_permissions(manage_channels=True)
    async def unmute(self, ctx, member: discord.Member, *, reason = None):
        """Mute the user in voice and text channels."""
        if not ctx.author.guild_permissions.mute_members:
            await ctx.send("You are missing following permissions:\nMute Members") # Because @commands.has_permissions() returns channel permissions or something.
            return
        reason = reason or "Reason was not specified."
        chans = 0
        if member == ctx.author:
            await ctx.send("You are not allowed to unmute " + ctx.author.mention + '.')
            return
        if ctx.author.top_role < member.top_role:
            await ctx.send("Your highest role is lower than the member's one. I can't let you unmute them.")
            return
        elif ctx.author.top_role == member.top_role:
            await ctx.send("Your highest role is the same as the member's one. I can't let you unmute them.")
            return
        elif ctx.guild.me.top_role < member.top_role:
            await ctx.send("My highest role is lower than the member's one. I can't unmute them.")
            return
        elif ctx.guild.me.top_role == member.top_role:
            await ctx.send("My highest role is the same as the member's one. I can't unmute them.")
            return
        for ch in ctx.guild.channels:
            overwrite = discord.PermissionOverwrite()
            if isinstance(ch, discord.TextChannel):
                await ch.set_permissions(member, overwrite=None)
                chans += 1
            elif isinstance(ch, discord.VoiceChannel):
                await ch.set_permissions(member, overwrite=None)
                chans += 1
        await ctx.send("Unmuted {0} in all ({1}) channels\nReason: {2}".format(member, chans, reason))

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(manage_channels=True)
    async def mute(self, ctx, member: discord.Member, *, reason = None):
        """Mute the user in voice and text channels."""
        if not ctx.author.guild_permissions.mute_members:
            await ctx.send("You are missing following permissions:\nMute Members") # Because @commands.has_permissions() returns channel permissions or something.
            return
        reason = reason or "Reason was not specified."
        chans = 0
        if member == ctx.author:
            await ctx.send("You are not allowed to mute " + ctx.author.mention + '.')
            return
        if ctx.author.top_role < member.top_role:
            await ctx.send("Your highest role is lower than the member's one. I can't let you mute them.")
            return
        elif ctx.author.top_role == member.top_role:
            await ctx.send("Your highest role is the same as the member's one. I can't let you mute them.")
            return
        elif ctx.guild.me.top_role < member.top_role:
            await ctx.send("My highest role is lower than the member's one. I can't mute them.")
            return
        elif ctx.guild.me.top_role == member.top_role:
            await ctx.send("My highest role is the same as the member's one. I can't mute them.")
            return
        for ch in ctx.guild.channels:
            overwrite = discord.PermissionOverwrite()
            if isinstance(ch, discord.TextChannel):
                overwrite.send_messages = False
                overwrite.add_reactions = False
                await ch.set_permissions(member, overwrite=overwrite)
                chans += 1
            elif isinstance(ch, discord.VoiceChannel):
                overwrite.connect = False
                overwrite.speak = False
                await ch.set_permissions(member, overwrite=overwrite)
                chans += 1
        await ctx.send("Muted {0.name}#{0.discriminator} in all ({1}) channels\nReason: {2}".format(member, chans, reason))

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason = None):
        """Kick specified user from the server"""
        if member == ctx.author:
            await ctx.send("You are not allowed to kick " + ctx.author.mention + '.')
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
            return
        reason = reason or "Reason was not specified."
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
            reason = reason or "Reason was not specified."
            await member.ban(delete_message_days=days, reason=str(reason) + ' -' + '{0.name}#{0.discriminator}'.format(ctx.author))
            await ctx.send("Banned {0.name}#{0.discriminator}.".format(member))
        else:
            try:
                days = await commands.MemberConverter().convert(ctx, days)
                member = days
                reason = reason or "Reason was not specified."
                await member.ban(delete_message_days=1, reason=str(reason) + ' -' + '{0.name}#{0.discriminator}'.format(ctx.author))
                await ctx.send("Banned {0.name}#{0.discriminator}.".format(member))
            except commands.CommandError:
                await ctx.send("No member found.")


def setup(bot):
    bot.add_cog(Mod(bot))