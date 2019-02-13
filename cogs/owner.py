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
import typing
from cogs.utils import converters

class Owner:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def dm(self, ctx, user: typing.Union[converters.User, int], *, text):
        "DM the user through using their user ID. If the user is stored in cache, specifying their username or username#discriminator will work."
        if isinstance(user, discord.User):
            pass
        elif isinstance(user, int):
            user = await self.bot.get_user_info(user_id)
        owner = self.bot.owner
        embed = discord.Embed(title=f'Sent by {owner} ({owner.id}', description=text)
        try:
            await user.send(f'A message from bot owner.', embed=embed)
        except discord.Forbidden:
            await ctx.send(f"{user} does not allow server members to send direct messages.")
        else:
            await ctx.send(f"Sent the message to {user}.")

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

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()

            result = None
            if not ret:
                if value:
                    result = f'```\n{value}\n```'
                else:
                    try:
                        result = f'```\n{repr(eval(body, env))}\n```'
                    except:
                        pass
            else:
                self._last_result = ret
                result = f'```\n{value}{ret}\n```'

            if result:
                if len(result) > 2000:
                    # await ctx.send(result[0:1950])
                    # await ctx.send(result[1951:-1]) # Feel free to fix this. I am lazy.
                    print(result)
                    await ctx.send("Output has been displayed in the console because its length was more than 2000 characters.")
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
    async def hiddeninfo(self, ctx, user_id: int = None):
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
        created_on = f"{user_created}\n({since_created} days ago)"
        em.add_field(name='Joined Discord',value=created_on)
        em.set_image(url=user.avatar_url.replace('.webp', '.png'))
        em.add_field(name='Account Type',value="User" if user.bot is Falses else "Bot")
        await ctx.send(embed=em)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def cogs(self, ctx):
        "Check currently loaded cogs."
        cogs = list(self.bot.cogs)
        embed = discord.Embed(title=f"{len(cogs)} loaded cogs", description=", ".join([cog for cog in cogs]))
        await ctx.send(embed=embed)

    @commands.group(hidden=True)
    async def cog(self, ctx):
        "Manage cogs."
        if not ctx.invoked_subcommand:
            pref = '```\n'
            postf = '\n```'
            result = f'{ctx.command.name}:\n'
            cmds = list(ctx.command.commands)
           # result += ' '.join(cmd.name for cmd in cmds)
            result += '    '.join(f'\n    {c.name} - {c.help}\n' for c in cmds) + '\n'
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
