import discord
from discord.ext import commands
import datetime
import psutil
import os
import time
import random
import urllib.request
import urllib.parse
import re
import aiohttp
import json

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

    async def request_time(self, location): # Get API key on https://developers.google.com/maps/documentation/timezone/start
        with open('settings.json') as file:
            results = json.load(file)
            key = results['GoogleAPIKey']
            file.close()
        async with aiohttp.ClientSession() as session:
            async with session.get('https://maps.googleapis.com/maps/api/geocode/json?address={}?key={}'.format(location, key)) as r:
                response = await r.json()
                resp = response["results"]
                status = response["status"]
                formatted_address = resp[0]["formatted_address"]
                if status == 'ZERO_RESULTS':
                    output = "No location found."
                    return output
                else:
                    lat = resp[0]["geometry"]["location"]["lat"]
                    lng = resp[0]["geometry"]["location"]["lng"]
                    async with session.get("https://maps.googleapis.com/maps/api/timezone/json?location={},{}&timestamp={}&key={}".format(lat, lng, datetime.datetime.utcnow().timestamp(), key)) as city_info:
                        info = await city_info.json()
                        daylight_saving = info["dstOffset"]
                        offset = info["rawOffset"]
                        time = datetime.datetime.utcnow() + datetime.timedelta(seconds=daylight_saving) + datetime.timedelta(seconds=offset)
                        time = time.strftime('%H:%M')
                        return "It is currently **{}** in **{}**.".format(time, formatted_address)

    @commands.command()
    async def time(self, ctx, *, name):
        await ctx.send(await self.request_time(name))

    @commands.command(aliases=['yt'])
    async def youtube(self, ctx, *, search_terms):
        "Find YouTube video with specified title."
        try:
            query_string = urllib.parse.urlencode({"search_query" : search_terms})
            html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
            search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
            await ctx.send("http://www.youtube.com/watch?v=" + search_results[0])
        except IndexError:
            await ctx.send("No video was found.")

    @commands.command(aliases=['sinfo'])
    @commands.guild_only()
    async def serverinfo(self, ctx):
        "Get current server info."
        guild = ctx.guild
        levels = {
            "None - No criteria set.": discord.VerificationLevel.none,
            "Low - Member must have a verified email on their Discord account.": discord.VerificationLevel.low,
            "Medium - Member must have a verified email and be registered on Discord for more than five minutes.": discord.VerificationLevel.medium,
            "High - Member must have a verified email, be registered on Discord for more than five minutes, and be a member of the guild itself for more than ten minutes.": discord.VerificationLevel.table_flip,
            "Extreme - Member must have a verified phone on their Discord account.": discord.VerificationLevel.double_table_flip
        }
        filters = {
            "Disabled - The guild does not have the content filter enabled.": discord.ContentFilter.disabled,
            "No Role - The guild has the content filter enabled for members without a role.": discord.ContentFilter.no_role,
            "All Members - The guild has the content filter enabled for every member.": discord.ContentFilter.all_members
        }
        regions = {
            "US West": discord.VoiceRegion.us_west,
            "US East": discord.VoiceRegion.us_east,
            "US South": discord.VoiceRegion.us_south,
            "US Central": discord.VoiceRegion.us_central,
            "London": discord.VoiceRegion.london,
            "Sydney": discord.VoiceRegion.sydney,
            "Amsterdam": discord.VoiceRegion.amsterdam,
            "Frankfurt": discord.VoiceRegion.frankfurt,
            "Brazil": discord.VoiceRegion.brazil,
            "Hong Kong": discord.VoiceRegion.hongkong,
            "Russia": discord.VoiceRegion.russia,
            "VIP US East": discord.VoiceRegion.vip_us_east,
            "VIP US West": discord.VoiceRegion.vip_us_west,
            "VIP Amsterdam": discord.VoiceRegion.vip_amsterdam,
            "Singapore": discord.VoiceRegion.singapore,
            "EU Central": discord.VoiceRegion.eu_central,
            "EU West": discord.VoiceRegion.eu_west
        }
        for name, reg in regions.items():
            if reg is guild.region:
                server_region = name
        verif_lvl = 'None'
        for text, dvl in levels.items():
            if dvl is guild.verification_level:
                verif_lvl = text
        for response, filt in filters.items():
            if filt is guild.explicit_content_filter:
                content_fiter = response
        feats = ''
        if guild.features != []:
            for feature in guild.features:
                feats += feature + '\n'
        else:
            feats = 'None'
        if guild.emojis:
            emotes_list = '\n'.join(['{0.name} - <:{0.name}:{0.id}>'.format(emoji) for emoji in guild.emojis[0:10]])
        else:
            emotes_list = "None"
        if guild.roles and len(guild.roles) != 1:
            roles_list = ', '.join(['`{}`'.format(role.name) for role in guild.role_hierarchy if role.name != '@everyone'])
        else:
            roles_list = "None"
        embed = discord.Embed(title='Server info', color = guild.me.color)
        embed.set_author(name='{} - {}'.format(guild.name, guild.id))
        embed.set_image(url=guild.icon_url_as(format='png'))
        embed.add_field(name='Owner', value='{0.name}#{0.discriminator}'.format(guild.owner))
        embed.add_field(name='Owner ID', value=guild.owner.id)
        embed.add_field(name='Members', value=guild.member_count)
        embed.add_field(name='Text Channels', value=len(guild.text_channels))
        embed.add_field(name='Voice Channels', value=len(guild.voice_channels))
        embed.add_field(name='Categories', value=len(guild.categories))
        embed.add_field(name='Region', value=server_region)
        embed.add_field(name='Roles (' + str(len(guild.roles)) + ')', value=roles_list)
        embed.add_field(name='Features (' + str(len(guild.features)) + ')', value=feats)
        embed.add_field(name='Verification Level', value=verif_lvl)
        embed.add_field(name='Content Filter', value=content_fiter)
        embed.add_field(name='Emojis (' + str(len(guild.emojis)) + ')', value=emotes_list)
        await ctx.send(embed=embed)

    @commands.command()
    async def contact(self, ctx, *, msg):
        "Contact the bot owner through the bot."
        app = await self.bot.application_info()
        owner = app.owner
        embed = discord.Embed(title='Sent by {0.name}#{0.discriminator} ({0.id})'.format(ctx.author), description = msg)
        await owner.send('`contact` command used.', embed = embed)

    @commands.command(aliases=['8ball'])
    async def eightball(self, ctx, *, question: str):
        "Ask 8ball a question."
        result = random.choice(self.ball)
        if ctx.guild:
            embed_color = ctx.guild.me.color
        else:
            embed_color = 16753920
        em = discord.Embed(description = question, title = '🎱 8ball', color = embed_color)
        em.add_field(name = 'Answer', value = result)
        await ctx.send(ctx.author.mention, embed = em)

    @commands.command(aliases=['pong'])
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
        "A link that lets you invite this bot your server."
        await ctx.send(
            ctx.author.mention +
            ' **OAuth2 link to invite {} bot to your server:** <https://discordapp.com/oauth2/authorize?client_id={}&permissions=469887047&scope=bot>'.format(self.bot.user.name, self.bot.user.id)
        )

    @commands.command(aliases=['roleperms', 'role_permissions', 'rolepermissions']) # WHY SO MANY ALIASES
    @commands.guild_only()
    async def role_perms(self, ctx, * , role: discord.Role):
        "Get role's permissions."
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
