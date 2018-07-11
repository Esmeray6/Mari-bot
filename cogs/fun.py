import discord
from discord.ext import commands
import aiohttp

class Fun:
    def __init__(self, bot):
        self.bot = bot

    # hug kiss slap etc.

    @commands.command()
    async def anime(self, ctx):
        """A random anime picture."""
        author = ctx.author
        guild = ctx.guild
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.computerfreaker.cf/v1/anime") as r:
                original = await r.json()
                pic = original["url"].replace("\\", '/')
                if guild is None:
                    colour = discord.Colour.default()
                else:
                    colour = author.colour
                embed = discord.Embed(description = "[Link]({})".format(pic),colour = colour)
                embed.set_image(url = pic)
                await ctx.send(content=author.mention, embed = embed)

def setup(bot):
    n = Fun(bot)
    bot.add_cog(n)
