import discord
from discord.ext import commands
import datetime

class OwnerCog:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def hiddeninfo(self, ctx, user_id: int=None):
        if user_id == None:
            user_id = ctx.author.id
        now = datetime.datetime.now()
        user = await self.bot.get_user_info(user_id)
        em = discord.Embed(title=user.id,color=ctx.author.color)
        em.set_author(name=user)
        since_created = (now - user.created_at).days
        user_created = user.created_at.strftime("%d %b %Y %H:%M")
        created_on = "{}\n({} days ago)".format(user_created, since_created)
        em.add_field(name='Joined Discord',value=created_on)
        em.set_image(url=user.avatar_url)
        if not user.bot:
            em.add_field(name='Account Type',value="User")
        else:
            em.add_field(name='Account Type',value="Bot")
        await ctx.send(embed=em)

    @commands.group()
    async def cog(self, ctx):
        '''Manage cogs.'''
        if ctx.invoked_subcommand is None:
            pref = '```\n'
            postf = '\n```'
            result = ctx.command.name + ':\n'
            cmds = list(ctx.command.commands)
           # result += ' '.join(cmd.name for cmd in cmds)
            result += '    '.join('\n    {} - {}\n'.format(c.name, c.help) for c in cmds) + '\n'
            await ctx.send(pref + result + postf)

    # Hidden means it won't show up on the default help.
    @cog.command(name='load', hidden=True)
    @commands.is_owner()
    async def cog_load(self, ctx, *, cog_name: str):
        """Command which loads a cog."""
        cog = 'cogs.' + cog_name.lower()

        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('Done.')

    @cog.command(name='unload', hidden=True)
    @commands.is_owner()
    async def cog_unload(self, ctx, *, cog_name: str):
        """Command which unloads a cog."""
        cog = 'cogs.' + cog_name.lower()

        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('Done.')

    @cog.command(name='reload', hidden=True)
    @commands.is_owner()
    async def cog_reload(self, ctx, *, cog_name: str):
        """Command which reloads a cog."""
        cog = 'cogs.' + cog_name.lower()

        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('Done.')

def setup(bot):
    bot.add_cog(OwnerCog(bot))
