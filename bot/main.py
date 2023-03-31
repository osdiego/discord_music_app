import asyncio
import logging

from discord import Intents
from discord.ext import commands

# from image_cog import image_cog
from maincog import MainCog
from musiccog import MusicCog

logging.basicConfig(level=logging.INFO)

bot = commands.Bot(command_prefix=".", intents=Intents.all())


# remove the default help command so that we can write out own
# bot.remove_command('help')
async def main():
    # register the class with the bot
    await bot.add_cog(MainCog(bot))
    # bot.add_cog(image_cog(bot))
    await bot.add_cog(MusicCog(bot))


asyncio.run(main())

# start the bot with our token
token = "ODgwODgzNTE3NzU0NTk3Mzk3.YSkwtA.c2pCqL-POk6sFxDY0PdHp001Fis"
bot.run(token)
# #bot.run(os.getenv("TOKEN"))
