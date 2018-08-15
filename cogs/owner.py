import discord
from discord.ext import commands
import datetime
import time
import textwrap
import re
from io import StringIO
import io
import traceback
from contextlib import redirect_stdout
from enum import Enum
from random import randint, choice
from urllib.parse import quote_plus
import aiohttp

class Owner:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def dm(self, ctx, user_id: int, *, text: str):
        "DM the user through using their user ID."
        user = await self.bot.get_user_info(user_id)
        app = await self.bot.application_info()
        owner = app.owner
        embed = discord.Embed(title='Sent by {0} ({0.id}'.format(owner), description=text)
        try:
            await user.send('A message from bot owner.', embed=embed)
        except discord.Forbidden:
            await ctx.send("{} does not allow server members to send direct messages.".format(user))
        await ctx.send("Sent the message to {}.".format(user))

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    async def interpreter(self, env, code, ctx):
        body = self.cleanup_code(code)
        stdout = io.StringIO()

        to_compile = 'async def func():\n{}'.format(textwrap.indent(body, "  "))

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send('```\n{}: {}\n```'.format(e.__class__.__name__, e))

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send('```\n{}{}\n```'.format(value, traceback.format_exc()))
        else:
            value = stdout.getvalue()

            result = None
            if not ret:
                if value:
                    result = '```\n{}\n```'.format(value)
                else:
                    try:
                        result = '```\n{}\n```'.format(repr(eval(body, env)))
                    except:
                        pass
            else:
                self._last_result = ret
                result = '```\n{}{}\n```'.format(value, ret)

            if result:
                if len(str(result)) > 1950:
                    await ctx.send(result[0:1950])
                    await ctx.send(result[1951:-1]) # Feel free to fix this. I am lazy.

                else:
                    await ctx.send(result)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def py(self, ctx, *, msg):
        """Python interpreter."""

        env = {
            'bot': self.bot,
            'self': self,
            'client': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'server': ctx.guild,
            'message': ctx.message,
            'msg': ctx.message
        }

        env.update(globals())

        await self.interpreter(env, msg, ctx)

    @commands.command()
    @commands.is_owner()
    async def hiddeninfo(self, ctx, user_id: int=None):
        "Get user info through user ID."
        if not user_id:
            user_id = ctx.author.id
        now = datetime.datetime.now()
        user = await self.bot.get_user_info(user_id)
        if ctx.guild:
            em = discord.Embed(title=user.id,color=ctx.author.color)
        else:
            em = discord.Embed(title=user.id,color=discord.Color.default())
        em.set_author(name=user)
        since_created = (now - user.created_at).days
        user_created = user.created_at.strftime("%d %b %Y %H:%M")
        created_on = "{}\n({} days ago)".format(user_created, since_created)
        em.add_field(name='Joined Discord',value=created_on)
        em.set_image(url=user.avatar_url.replace('.webp', '.png'))
        em.add_field(name='Account Type',value="User" if not user.bot else "Bot")
        await ctx.send(embed=em)

    @commands.group(hidden=True)
    async def cog(self, ctx):
        "Manage cogs."
        if not ctx.invoked_subcommand:
            pref = '```\n'
            postf = '\n```'
            result = ctx.command.name + ':\n'
            cmds = list(ctx.command.commands)
           # result += ' '.join(cmd.name for cmd in cmds)
            result += '    '.join('\n    {} - {}\n'.format(c.name, c.help) for c in cmds) + '\n'
            await ctx.send(pref + result + postf)

    @cog.command(name='load', hidden=True)
    @commands.is_owner()
    async def cog_load(self, ctx, *, cog_name: str):
        "Command which loads a cog."
        cog = 'cogs.' + cog_name.lower()

        self.bot.load_extension(cog)
        await ctx.send('Done.')

    @cog.command(name='unload', hidden=True)
    @commands.is_owner()
    async def cog_unload(self, ctx, *, cog_name: str):
        "Command which unloads a cog."
        cog = 'cogs.' + cog_name.lower()

        self.bot.unload_extension(cog)
        await ctx.send('Done.')

    @cog.command(name='reload', hidden=True)
    @commands.is_owner()
    async def cog_reload(self, ctx, *, cog_name: str):
        "Command which reloads a cog."
        cog = 'cogs.' + cog_name.lower()

        self.bot.unload_extension(cog)
        self.bot.load_extension(cog)
        await ctx.send('Done.')

def setup(bot):
    bot.add_cog(Owner(bot))
