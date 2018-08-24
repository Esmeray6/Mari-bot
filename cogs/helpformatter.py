import discord
from discord.ext import commands

class Help:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help', aliases=['h'])
    async def _help(self, ctx, *, command: str=None):
        """Get help on a specified cog or command.
        Don't put any arguments to get a list of available commands."""
        pref = '```\n'
        postf = f'Get info on a command group, category or just a command with @{self.bot.user.name}#{self.bot.user.discriminator} help <Category>/<Command>/<Command group> or *help <Category>/<Command>/<Command group>'
        result = ''
        postfix = '\n```'
        paginator = commands.Paginator()
        if not command:
            li = [cog[0] for cog in self.bot.cogs.items()]
            for smth in li:
                if smth != 'Help':
                    s = list(self.bot.get_cog_commands(smth))
                    if s:
                        paginator.add_line(f"{s[0].cog_name}:")
                        for c in s:
                            if ctx.guild:
                                if c.name == "mute" and not ctx.author.guild_permissions.mute_members or c.name == "unmute" and not ctx.author.guild_permissions.mute_members:
                                    continue
                            else:
                                pass
                            if not c.hidden:
                                try:
                                    await c.can_run(ctx)
                                    paginator.add_line(f'    {c.name} - {c.short_doc}')
                                except:
                                    pass
            paginator.add_line(postf)
            for page in paginator.pages:
                await ctx.send(page)
        else:
            if command not in self.bot.all_commands:
                if command not in self.bot.cogs:
                    cmd = self.bot.get_command(command.replace('*', '').replace(self.bot.user.mention, ''))
                    if cmd:
                        paginator.add_line(f"{ctx.prefix.replace(self.bot.user.mention, f'@{self.bot.user.name}#{self.bot.user.discriminator} ')}{cmd.signature}\n\n    {cmd.help}")
                        for page in paginator.pages:
                            await ctx.send(page)
                    else:
                        result = 'That command/category/command group does not exist!'
                        await ctx.send(result)
                else:
                    the_cog = list(self.bot.get_cog_commands(command))
                    paginator.add_line(f"{the_cog[0].cog_name}:") 
                    for cmd in the_cog:
                        if not cmd.hidden:
                            paginator.add_line(''.join(f'    {cmd.name} - {cmd.help}'))
                    paginator.add_line(postf)
                    for page in paginator.pages:
                        await ctx.send(page)
            else:
                cmd = self.bot.get_command(command.replace('*', '').replace(self.bot.user.mention, ''))
                result += f"{ctx.prefix.replace(self.bot.user.mention, f'@{self.bot.user.name}#{self.bot.user.discriminator} ')}{cmd.signature}\n\n    {cmd.help}"
                await ctx.send(pref + result + postfix)

def setup(bot):
    bot.add_cog(Help(bot))
