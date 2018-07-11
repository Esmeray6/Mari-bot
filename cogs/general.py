import discord
from discord.ext import commands
import datetime

class General:
    def __init__(self, bot):
        self.bot = bot
        self.ball = [
            "As I see it, yes", "It is certain", "It is decidedly so",
            "Most likely", "Outlook good", ("Signs point to yes"),
            "Without a doubt", "Yes", "Yes – definitely", "You may rely on it",
            "Reply hazy, try again", "Ask again later",
            "Better not tell you now", "Cannot predict now",
            "Concentrate and ask again", "Don't count on it", "My reply is no",
            "My sources say no", "Outlook not so good", "Very doubtful"
        ]

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
        botid = int(self.bot.user.id)
        support_stuff = '[Support server](https://discord.gg/G5PsTEz)\n[Patreon](https://www.patreon.com/shivaco)'
        servers = len(self.bot.guilds)
        if ctx.guild is None:
            embed_color = ctx.author.color
        else:
            embed_color = 16753920
        # messages = len(self.bot.messages)
        embed = discord.Embed(description= '**Uptime:** {}'.format(uptime_time), colour=embed_color)
        #embed.set_author(
            #name='Source Code',
            #url='https://github.com/shivaco/',
            #icon_url=
            #self.bot.user.avatar_url)     Gonna be used soon
        embed.add_field(name='Owner', value=owner)
        embed.add_field(name='Bot ID', value=botid)
        embed.add_field(name='Servers', value=servers)
        # embed.add_field(name='Messages', value=messages)
        embed.add_field(name='Channels', value=channels)
        embed.add_field(name='Users', value=members)
        embed.add_field(name='Additional Info', value=support_stuff)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(General(bot))
