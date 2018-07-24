import discord
import asyncio

class Status:

    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.display_status())

    async def display_status(self):
        while True:
            try:
                status = 'in {} servers'.format(len(self.bot.guilds))
                await self.bot.change_presence(activity=discord.Game(status))
            except:
                return
        await asyncio.sleep(60)

### ---------------------------- Setup ---------------------------------- ###
def setup(bot):
    n = Status(bot)
    bot.add_cog(n)