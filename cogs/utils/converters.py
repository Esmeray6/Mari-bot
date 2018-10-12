import discord
from discord.ext import commands
import re

class IDConverter(commands.Converter):
    def __init__(self):
        self._id_regex = re.compile(r'([0-9]{15,21})$')
        super().__init__()

    def _get_id_match(self, argument):
        return self._id_regex.match(argument)

def _get_from_guilds(bot, getter, argument):
    result = None
    for guild in bot.guilds:
        result = getattr(guild, getter)(argument)
        if result:
            return result
    return result

class Role(IDConverter):
    async def convert(self, ctx, argument):
        guild = ctx.message.guild
        if not guild:
            raise commands.NoPrivateMessage()

        match = self._get_id_match(argument) or re.match(r'<@&([0-9]+)>$', argument)
        params = dict(id=int(match.group(1))) if match else dict(name=argument)
        if "name" in params.keys():
            result = discord.utils.find(lambda r: r.name.lower() == params['name'].lower(), guild.roles)
        else:
            result = discord.utils.get(guild.roles, **params)
        if result is None:
            raise commands.BadArgument(f'Role "{argument}" not found.')
        return result

class Member(IDConverter):
    async def convert(self, ctx, argument):
        message = ctx.message
        bot = ctx.bot
        match = self._get_id_match(argument) or re.match(r'<@!?([0-9]+)>$', argument)
        guild = message.guild
        result = None
        if match is None:
            # not a mention...
            if guild:
                #result = guild.get_member_named(argument)
                if len(argument) > 5 and argument[-5] != '#':
                    result = discord.utils.find(lambda m: m.display_name.lower() == argument.lower() or m.name.lower() == argument.lower(), guild.members)
                elif len(argument) > 5 and argument[-5] == '#':
                    result = discord.utils.find(lambda m: str(m).lower() == argument.lower(), guild.members)
                elif len(argument) < 5:
                    def pred(m):
                        if m.nick is not None:
                            return m.nick.lower() == argument.lower() or m.name.lower() == argument.lower()
                        else:
                            return m.name.lower() == argument.lower()
                    return discord.utils.find(pred, guild.members)
            else:
                for guild2 in bot.guilds:
                    if len(argument) > 5 and argument[-5] != '#':
                        result = discord.utils.find(lambda m: m.display_name.lower() == argument.lower() or m.name.lower() == argument.lower(), guild.members)
                    elif len(argument) > 5 and argument[-5] == '#':
                        #result = _get_from_guilds(bot, 'get_member_named', argument)
                        result = discord.utils.find(lambda m: str(m).lower() == argument.lower(), guild.members)
                    elif len(argument) < 5:
                        def pred(m):
                            if m.nick is not None:
                                return m.nick.lower() == argument.lower() or m.name.lower() == argument.lower()
                            else:
                                return m.name.lower() == argument.lower()
                        return discord.utils.find(pred, guild.members)

        else:
            user_id = int(match.group(1))
            if guild:
                result = guild.get_member(user_id)
            else:
                result = _get_from_guilds(bot, 'get_member', user_id)

        if result is None:
            raise commands.BadArgument(f'Member "{argument}" not found.')

        return result

    def _get_id_match(self, argument):
        return self._id_regex.match(argument)

class User(IDConverter):
    async def convert(self, ctx, argument):
        match = self._get_id_match(argument) or re.match(r'<@!?([0-9]+)>$', argument)
        result = None
        state = ctx._state

        if match is not None:
            user_id = int(match.group(1))
            result = ctx.bot.get_user(user_id)
        else:
            arg = argument
            # check for discriminator if it exists
            if len(arg) > 5 and arg[-5] == '#':
                discrim = arg[-4:]
                name = arg[:-5]
                predicate = lambda u: u.name.lower() == name.lower() and u.discriminator == discrim
                result = discord.utils.find(predicate, state._users.values())
                if result is not None:
                    return result

            predicate = lambda u: u.name.lower() == arg.lower()
            result = discord.utils.find(predicate, state._users.values())

        if result is None:
            raise commands.BadArgument(f'User "{argument}" not found.')

        return result
