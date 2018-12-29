import discord
from discord.ext import commands
from cogs.utils import converters

class Mod:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def setprefix(self, ctx, *, prefix = None):
        """Set bot prefix for current server."""
        info = self.bot.db.prefixes.find_one({'guild_id': ctx.guild.id})
        if not prefix:
            if info:
                prefix = info['prefix']
            else:
                prefix = "*"
            await ctx.send(f"{ctx.author.mention} Prefix for this server is `{prefix}`.")
        else:
            if info:
                if prefix == info['prefix']:
                    await ctx.send(f"{ctx.author.mention} This server current prefix is already set to `{prefix}`!")
                else:
                    self.bot.db.prefixes.update_one({'guild_id': ctx.guild.id}, {'$set': {'prefix': prefix}})
                    self.bot.prefixes[ctx.guild.id] = prefix
                    await ctx.send(f"{ctx.author.mention} Prefix has been changed from `{info['prefix']}`to `{prefix}`.")
            else:
                self.bot.db.prefixes.insert_one({'guild_id': ctx.guild.id, 'prefix': prefix})
                self.bot.prefixes[ctx.guild.id] = prefix
                await ctx.send(f"{ctx.author.mention} Prefix has been changed to `{prefix}`.")

    @commands.command(aliases=['menro'])
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def mentionrole(self, ctx, *, role: converters.Role):
        """Mention the role through the bot.
        If the role is not mentionable, bot will make it mentionable for a second."""
        if role > ctx.guild.me.top_role:
            await ctx.send(f"Role **{role}** is higher than my highest role. I can't let you use this command.")
        elif role == ctx.guild.me.top_role:
            await ctx.send(f"Role **{role}** is my highest role. I can't let you use this command.")
        else:
            if role.name == "@everyone":
                await ctx.send(f"Too bad, {ctx.author.mention} tried to mention everyone. :^)")
                return
            if role.mentionable:
                await ctx.send(f"Role {role.mention} has been mentioned by {ctx.author.mention}.")
            else:
                await role.edit(mentionable=True, reason="Command mentionrole usage.")
                await ctx.send(f"Role {role.mention} has been mentioned by {ctx.author.mention}.")
                await role.edit(mentionable=False, reason="Command mentionrole usage.")

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
            await ctx.send(f"{user} is banned already.")
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
            await ctx.send(f"{user} was banned from the server.")

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
            await ctx.send(f"{user} is not banned.")
            return
        await ctx.guild.unban(user, reason=f"Unbanned by {ctx.author}")
        await ctx.send(f"Unbanned {user}.")

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
            await ctx.send(f"Deleted {amount} {'message' if len(msgs) == 2 else 'messages'} in {channel.mention}.", delete_after=5)
        except discord.ClientException:
            await ctx.send("The number of messages to delete is more than 100.")
        except discord.HTTPException:
            await ctx.send("Failed to delete messages, somehow.")

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(manage_channels=True)
    async def unmute(self, ctx, member: converters.Member, *, reason = None):
        """Mute the user in voice and text channels."""
        if not ctx.author.guild_permissions.mute_members:
            await ctx.send("You are missing following permissions:\nMute Members") # Because @commands.has_permissions() returns channel permissions or something.
            return
        reason = reason or "Reason was not specified."
        chans = 0
        if member == ctx.author:
            await ctx.send(f"You are not allowed to unmute {ctx.author.mention}.")
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
        await ctx.send(f"Unmuted {member} in all ({chans}) channels\nReason: {reason}")

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(manage_channels=True)
    async def mute(self, ctx, member: converters.Member, *, reason = None):
        """Mute the user in voice and text channels."""
        if not ctx.author.guild_permissions.mute_members:
            await ctx.send("You are missing following permissions:\nMute Members") # Because @commands.has_permissions() returns channel permissions or something.
            return
        reason = reason or "Reason was not specified."
        chans = 0
        if member == ctx.author:
            await ctx.send(f"You are not allowed to mute {ctx.author.mention}.")
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
        await ctx.send(f"Muted {member} in all ({chans}) channels\nReason: {reason}")

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: converters.Member, *, reason = None):
        """Kick specified user from the server"""
        if member == ctx.author:
            await ctx.send(f"You are not allowed to kick {ctx.author.mention}.")
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
            await member.kick(reason=f"{reason} -{ctx.author}")
        except discord.Forbidden:
            await ctx.send("Couldn't kick the user.") # Because full error handling is important. :^)
            return
        await ctx.send(f"Kicked {member}.")

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, days, member = None, *, reason = None):
        """Ban member from current server and delete their messages from the server for X days.
        If you specify a member in "days" argument, the member will be banned and their messages for 1 day will be deleted."""
        if days.isdigit():
            days = int(days)
            user = self.bot.get_user(days)
            if user is None:
                try:
                    user = await self.bot.get_user_info(days)
                except discord.NotFound:
                    try:
                        member = await converters.Member().convert(ctx, member)
                        reason = reason or "Reason was not specified."
                        await member.ban(delete_message_days=days, reason=f"{reason} -{ctx.author}")
                        await ctx.send(f"Banned {member}.")
                    except commands.CommandError:
                        await ctx.send("No member found.")
            else:
                days = await converters.Member().convert(ctx, str(user))
                member = days
                reason = reason or "Reason was not specified."
                await member.ban(delete_message_days=1, reason=f"{reason} -{ctx.author}")
                await ctx.send(f"Banned {member}.")
        else:
            try:
                days = await converters.Member().convert(ctx, days)
                member = days
                if member is None:
                    await ctx.send("No member found.")
                else:
                    reason = reason or "Reason was not specified."
                    await member.ban(delete_message_days=1, reason=f"{reason} -{ctx.author}")
                    await ctx.send(f"Banned {member}.")
            except commands.CommandError:
                await ctx.send("No member found.")

def setup(bot):
    bot.add_cog(Mod(bot))