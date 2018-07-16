import discord
from discord.ext import commands

class Help:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help', aliases=['h'])
    async def _help(self, ctx, *, command: str=None):
        pref = '```\n'
        postf = f'Get info on a command group, category or just a command with @{self.bot.user.name}#{self.bot.user.discriminator} help <Category>/<Command>/<Command group> or *help <Category>/<Command>/<Command group>'
        result = ''
        postfix = '\n```'
        paginator = commands.Paginator()
        if command is None:
            li = [cog[0] for cog in self.bot.cogs.items()]
            for smth in li:
                if smth != 'Help':
                    s = list(self.bot.get_cog_commands(smth))
                    if s:
                        paginator.add_line('\n' + s[0].cog_name + ':')
                        paginator.add_line('    ')
                        for c in s:
                            if not c.hidden:
                                paginator.add_line('    {} - {}\n'.format(str(c.name), str(c.help)))
            paginator.add_line(postf)
            for page in paginator.pages:
                await ctx.send(page)
        else:
            if command not in self.bot.all_commands:
                if command not in self.bot.cogs:
                    cmd = self.bot.get_command(command.replace('*', '').replace(self.bot.user.mention, ''))
                    if cmd:
                        paginator.add_line(ctx.prefix.replace(self.bot.user.mention, '@{}#{}'.format(self.bot.user.name, self.bot.user.discriminator)) + str(cmd.signature) + '\n\n    ' + str(cmd.help))
                        for page in paginator.pages:
                            await ctx.send(page)
                    else:
                        result = 'That command/category/command group does not exist!'
                        await ctx.send(result)
                else:
                    the_cog = list(self.bot.get_cog_commands(command))
                    paginator.add_line(the_cog[0].cog_name + ':\n')
                    for cmd in the_cog:
                        if not cmd.hidden:
                            paginator.add_line(''.join('    {} - {}\n'.format(cmd.name, str(cmd.help))))
                    paginator.add_line(postf)
                    for page in paginator.pages:
                        await ctx.send(page)
            else:
                cmd = self.bot.get_command(command.replace('*', '').replace(self.bot.user.mention, ''))
                result += ctx.prefix.replace(self.bot.user.mention, '@{}#{}'.format(self.bot.user.name, self.bot.user.discriminator)) + str(cmd.signature) + '\n\n    ' + str(cmd.help)
                await ctx.send(pref + result + postfix)

def setup(bot):
    bot.add_cog(Help(bot))
