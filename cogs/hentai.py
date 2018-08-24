import discord
from discord.ext import commands
import aiohttp

class Hentai:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def hentai(self, ctx):
        """Random hentai picture."""
        guild = ctx.guild
        author = ctx.author
        channel = ctx.channel
        try:
            if channel.is_nsfw():
                async with aiohttp.ClientSession() as session:
                    async with session.get("https://api.computerfreaker.cf/v1/hentai") as r:
                        original = await r.json()
                        pic = original["url"]
                        embed = discord.Embed(description = f"[Link]({pic})", color = author.color)
                        embed.set_image(url = pic)
                        await ctx.send(content = author.mention, embed = embed)
            else:
                await ctx.send("This channel is not marked as NSFW.")
        except Exception as e:
            await ctx.send('An error occured. Check the console for more details.')
            print(e)

def setup(bot):
    bot.add_cog(Hentai(bot))