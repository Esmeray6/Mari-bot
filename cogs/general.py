import discord
from discord.ext import commands
import datetime
import psutil
import os
import time
import random

class General:
    def __init__(self, bot):
        self.bot = bot
        self.ball = [
            "As I see it, yes.", "It is certain.", "It is decidedly so.",
            "Most likely.", "Outlook good.", "Signs point to yes.",
            "Without a doubt.", "Yes.", "Yes – definitely.", "You may rely on it.",
            "Reply hazy, try again.", "Ask again later.",
            "Better not tell you now.", "Cannot predict now.",
            "Concentrate and ask again.", "Don't count on it.", "My reply is no.",
            "My sources say no.", "Outlook not so good.", "Very doubtful."
        ]

    @commands.command()
    async def ping(self, ctx):
        "Bot's connection to Discord."
        t1 = time.perf_counter()
        await ctx.channel.trigger_typing()
        t2 = time.perf_counter()
        thedata = (' 🏓 **Pong.**\nTime: ' + str(round((t2 - t1) * 1000))) + ' ms'
        if ctx.guild:
            embed_color = ctx.guild.me.color
        else:
            embed_color = discord.Color.default()
        data = discord.Embed(description=thedata, color=embed_color)
        await ctx.send(embed=data)

    @commands.command(aliases=['av'])
    @commands.guild_only()
    async def avatar(self, ctx, *, user: discord.Member = None):
        "User's avatar."
        author = ctx.author
        if user is None:
            user = ctx.author
        retard = "{}#{}'s avatar"
        embed = discord.Embed(color=user.colour)
        embed.set_author(name=retard.format(user.name, user.discriminator))
        embed.set_image(url=user.avatar_url.replace('.webp', '.png').replace('size=1024', 'size=2048'))
        await ctx.send(embed=embed)

    @commands.command()
    async def roles(self, ctx, *, user: discord.Member = None):
        "Check the user's roles. Provide no arguments to check your roles."
        if not user:
            user = ctx.author
        desc = '\n'.join((r.name for r in user.roles if r.name != '@everyone'))
        if desc == "":
            await ctx.send('{0.name}#{0.discriminator} has no roles!'.format(user))
        elif len(user.roles[1:]) >= 1:
            embed = discord.Embed(
                title="{}'s roles".format(user.name),
                description=desc,
                colour=user.colour)
            await ctx.send(ctx.author.mention, embed=embed)

    @commands.command()
    async def invite(self, ctx):
        'A link that lets you invite this bot your server.'
        await ctx.send(
            ctx.author.mention +
            ' **OAuth2 link to invite {} bot to your server:** <https://discordapp.com/oauth2/authorize?client_id={}&permissions=469887047&scope=bot>'.format(self.bot.user.name, self.bot.user.id)
        )

    @commands.command(aliases=['roleperms', 'role_permissions', 'rolepermissions']) # WHY SO MANY ALIASES
    @commands.guild_only()
    async def role_perms(self, ctx, * , role: discord.Role):
        '''Get role's permissions.'''
        s = []
        for perm, value in role.permissions:
            uh = perm.replace('_', ' ')
            uhh = uh.replace('Tts', 'TTS')
            if not value:
                s.append('{}: {}'.format(uhh.title(), '❌'))
            else:
                s.append('{}: {}'.format(uhh.title(), '✅'))
        await ctx.send('```\n{}\n```'.format('\n'.join(s)))

    def get_bot_uptime(self):
        # Courtesy of Danny
        now = datetime.datetime.utcnow()
        delta = now - self.bot.uptime
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        if days:
            fmt = '{d} days, {h} hours, {m} minutes, and {s} seconds'
        else:
            fmt = '{h} hours, {m} minutes, and {s} seconds'

        return fmt.format(d=days, h=hours, m=minutes, s=seconds)

    @commands.command()
    async def stats(self, ctx):
        "Bot's uptime and stuff."
        channels = 0
        members = 0
        for guild in self.bot.guilds:
            channels += len(guild.channels)
            members += len(guild.members)
        app = await self.bot.application_info()
        owner = app.owner
        author = ctx.author
        uptime_time = self.get_bot_uptime()
        if self.bot.user.id == 458607948755763200:
            support_stuff = '[Support server](https://discord.gg/f5nDpp6)\n[Patreon](https://www.patreon.com/shivaco)\n[Vote for {0.name} on discordbots.org](https://discordbots.org/bot/{0.id})'.format(self.bot.user)
        else:
            support_stuff = '[Support server](https://discord.gg/f5nDpp6)\n[Patreon](https://www.patreon.com/shivaco)'
        servers = len(self.bot.guilds)
        process = psutil.Process(os.getpid())
        mem = round(process.memory_info()[0] / float(2 ** 20), 2)
        if ctx.guild is None:
            embed_color = ctx.guild.me.color
        else:
            embed_color = 16753920
        embed = discord.Embed(description = '**Uptime:** {}\n**Memory**: {} MB'.format(uptime_time, mem), color = embed_color)
        embed.set_author(
            name = 'Source Code',
            url = 'https://github.com/shivaco/Mari-bot',
            icon_url = self.bot.user.avatar_url)
        embed.add_field(name='Owner', value=owner)
        embed.add_field(name='Bot ID', value=self.bot.user.id)
        embed.add_field(name='Servers', value=servers)
        embed.add_field(name='Channels', value=channels)
        embed.add_field(name='Users', value=members)
        embed.add_field(name='Additional Info', value=support_stuff)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(General(bot))
