import discord
from discord.ext import commands
import json
import datetime
import traceback
import sys
import json

path = 'settings.json'

bot = commands.Bot(command_prefix=commands.when_mentioned_or('*'), activity=discord.Game(name='*help'))
bot.remove_command('help')
bot.uptime = datetime.datetime.utcnow()
initial_extensions = json.load(open(path, 'r'))["enabled_cogs"]
if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send_help()
    elif isinstance(error, commands.BadArgument):
        await ctx.send_help()
    elif isinstance(error, commands.DisabledCommand):
        await ctx.send("That command is disabled.")
    elif isinstance(error, commands.NotOwner):
        await ctx.send("You are not bot owner.")
    elif isinstance(error, commands.MissingPermissions):
        if error.missing_perms:
            await ctx.send("You are missing following permissions:\n" + '\n'.join(perm for perm in error.missing_perms).replace('_', ' ').title())
    elif isinstance(error, commands.BotMissingPermissions):
        if error.missing_perms:
            await ctx.send("The bot is missing following permissions:\n" + '\n'.join(perm for perm in error.missing_perms).replace('_', ' ').title())
    elif not isinstance(error, commands.CommandNotFound):
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
        await ctx.send('Ignoring exception in command `{}`: `{}`'.format(ctx.command, error))

@bot.event
async def on_ready():
    print('{0}\nUser ID: {0.id}'.format(bot.user))
    game = discord.Game(name='ready in {} servers'.format(len(bot.guilds)))
    await bot.change_presence(activity=game, status=discord.Status.online)
    if bot.user.id == 424582831637790730:
        import requests
        response = requests.get('https://cdn.discordapp.com/avatars/458607948755763200/e3e4fedba01aa021ef05ca1f37bc151f.png?size=1024')
        await bot.user.edit(avatar=response.content, username='Beta Mari')

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
bot.run(token, bot=True, reconnect=True)
