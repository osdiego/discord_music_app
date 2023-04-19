import asyncio
import logging

from discord import Intents
from discord.ext.commands import Bot
from main_cog import MainCog
from music_cog import MusicCog
from utils import safe_mkdir

safe_mkdir(folder="playlists")
logging.basicConfig(level=logging.INFO)

bot = Bot(command_prefix=".", intents=Intents.all())


async def main():
    # register the class with the bot
    await bot.add_cog(MainCog(bot))
    # bot.add_cog(image_cog(bot))
    await bot.add_cog(MusicCog(bot))


asyncio.run(main())

# start the bot with our token
TOKEN = "ODgwODgzNTE3NzU0NTk3Mzk3.YSkwtA.c2pCqL-POk6sFxDY0PdHp001Fis"
bot.run(TOKEN)
