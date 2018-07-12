import discord
import asyncio

class Status:

    def __init__(self, bot):
        self.bot = bot

    async def display_status(self):
        while self == self.bot.get_cog('Status'):
            try:
                status = 'in {} servers'.format(len(self.bot.guilds))
                await self.bot.change_presence(activity=discord.Game(status))
            except:
                return
            await asyncio.sleep(60)

### ---------------------------- Setup ---------------------------------- ###
def setup(bot):
    n = Status(bot)
    loop = asyncio.get_event_loop()
    loop.create_task(n.display_status())
    bot.add_cog(n)