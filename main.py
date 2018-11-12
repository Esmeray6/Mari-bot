import discord
from discord.ext import commands
import json
import datetime
import traceback
import sys
import json
from typing import Iterable, List
from pymongo import MongoClient

path = 'settings.json'
cogs_path = 'cog_settings.json'

async def get_prefix(bot, message):
    if message.guild:
        try:
            return commands.when_mentioned_or(bot.prefixes[message.guild.id])(bot, message)
        except KeyError:
            return commands.when_mentioned_or('*')(bot, message)
    else:
        return commands.when_mentioned_or('*')(bot, message)

bot = commands.Bot(command_prefix=get_prefix)
#bot = commands.Bot(command_prefix=commands.when_mentioned_or('*'))
bot.remove_command('help')
bot.uptime = datetime.datetime.utcnow()
conn = MongoClient()
bot.db = conn.mari

initial_extensions = json.load(open(cogs_path, 'r'))["enabled_cogs"]
for extension in initial_extensions:
    try:
        bot.load_extension(extension)
    except Exception as e:
        print(f'Failed to load extension {extension}.', file=sys.stderr)
        traceback.print_exc()

@bot.event
async def on_member_update(before, after):
    if after.id == bot.owner.id:
        bot.owner = bot.get_user(after.id)

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
        try:
            await ctx.author.send(f"Command `{ctx.command}` cannot be used in private messages.")
        except:
            pass
    elif isinstance(error, commands.BadUnionArgument):
        convs = []
        for conv in error.converters:
            convs.append(f"`{conv.__name__}`")
        converts = " or ".join(convs)
        await ctx.send(f"Parameter `{error.param.name}` in command `{ctx.invoked_with}` failed to convert into {converts}.")
    elif not isinstance(error, commands.CommandNotFound):
        print(f'Ignoring exception in command {ctx.command}:', file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
        await ctx.send('Ignoring exception in command `{}` - `{}: {}`'.format(ctx.command, type(error).__name__, str(error)))

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
        m = await destination.send(f"You are missing the required argument.\n{msg}")
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
        m = await destination.send(f"Your argument is invalid.\n{msg}")
    ret.append(m)
    return ret

#Both missing_argument() and bad_argument() are edited versions of send_help() that is used in Red bot.

@bot.event
async def on_ready():
    await bot.wait_until_ready()
    print(f'{bot.user}\nUser ID: {bot.user.id}')
    status = f'*help or @{bot.user} help'
    bot.owner = (await bot.application_info()).owner
    await bot.change_presence(activity=discord.Game(status))
    bot.prefixes = {}
    if bot.db.prefixes.find_one():
        for data in bot.db.prefixes.find():
            bot.prefixes[data['guild_id']] = data['prefix']

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    else:
        if message.content == bot.user.mention:
            try:
                prefix = bot.prefixes[message.guild.id]
            except KeyError:
                prefix = "*"
            prefixes = f"{message.author.mention} My global prefix is `@{bot.user}`. This server prefix is `{prefix}`!"
            await message.channel.send(prefixes)
        else:
            await bot.process_commands(message)

with open(path, 'r') as settings:
    sets = json.load(settings)
    token = sets["token"]
    settings.close()
if not token:
    print("-----\n"
          "You don't have bot token setup in settings.json!\n"
          "-----\n")
else:
    bot.run(token, bot=True, reconnect=True)
    conn.close()
