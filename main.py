import discord
from discord.ext import commands
import json
import datetime
import traceback
import sys
import json
from typing import Iterable, List

path = 'settings.json'
cogs_path = 'cog_settings.json'

# async def get_prefix(bot, message):
#     if message.guild:
#         return commands.when_mentioned_or('*')(bot, message)
#     else:
#         return commands.when_mentioned_or('.')(bot, message)

# bot = commands.Bot(command_prefix=get_prefix)
bot = commands.Bot(command_prefix=commands.when_mentioned_or('*'))
bot.remove_command('help')
bot.uptime = datetime.datetime.utcnow()

initial_extensions = json.load(open(cogs_path, 'r'))["enabled_cogs"]
for extension in initial_extensions:
    try:
        bot.load_extension(extension)
    except Exception as e:
        print('Failed to load extension {}.'.format(extension), file=sys.stderr)
        traceback.print_exc()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await missing_argument(ctx)
    elif isinstance(error, commands.BadArgument):
        await bad_argument(ctx)
    elif isinstance(error, commands.DisabledCommand):
        await ctx.send(f"Command {ctx.command} is disabled.")
    elif isinstance(error, commands.NotOwner):
        await ctx.send("You are not bot owner.")
    elif isinstance(error, commands.MissingPermissions):
        if error.missing_perms:
            await ctx.send("You are missing following permissions:\n" + '\n'.join(perm for perm in error.missing_perms).replace('_', ' ').title())
    elif isinstance(error, commands.BotMissingPermissions):
        if error.missing_perms:
            await ctx.send("The bot is missing following permissions:\n" + '\n'.join(perm for perm in error.missing_perms).replace('_', ' ').title())
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.author.send("Command `{}` cannot be used in private messages.".format(ctx.command))
    elif not isinstance(error, commands.CommandNotFound):
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
        await ctx.send('Ignoring exception in command `{}` - `{}: {}`'.format(ctx.command, type(error.original).__name__, str(error.original)))

async def missing_argument(ctx) -> List[discord.Message]:
    """Send the command help message.
    Returns
    -------
    `list` of `discord.Message`
        A list of help messages which were sent to the user.
    """
    command = ctx.command

    ret = []
    destination = ctx
    f = commands.HelpFormatter()
    msgs = await f.format_help_for(ctx, command)
    for msg in msgs:
        m = await destination.send("You are missing the required argument.\n{}".format(msg))
    ret.append(m)
    return ret

async def bad_argument(ctx) -> List[discord.Message]:
    """Send the command help message.
    Returns
    -------
    `list` of `discord.Message`
        A list of help messages which were sent to the user.
    """
    command = ctx.command

    ret = []
    destination = ctx
    f = commands.HelpFormatter()
    msgs = await f.format_help_for(ctx, command)
    for msg in msgs:
        m = await destination.send("Your argument is invalid.\n{}".format(msg))
    ret.append(m)
    return ret

#Both missing_argument() and bad_argument() are edited versions of send_help() that is used in Red bot.

@bot.event
async def on_ready():
    print('{0}\nUser ID: {0.id}'.format(bot.user))
    status = '*help or @{} help'.format(bot.user)
    await bot.wait_until_ready()
    bot.owner = (await bot.application_info()).owner
    await bot.change_presence(activity=discord.Game(status))

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    else:
        if message.content == bot.user.mention:
            prefixes = message.author.mention + ' My prefix is `@Mari#4343` or `*`!'
            await message.channel.send(prefixes)
        else:
            await bot.process_commands(message)

with open(path, 'r') as settings:
    sets = json.load(settings)
    token = sets["token"]
    if not token:
        print("-----\n"
              "You don't have bot token setup in settings.json!\n"
              "-----\n")
    else:
        bot.run(token, bot=True, reconnect=True)
