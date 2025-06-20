import asyncio
import logging
import os

from discord import Intents
from discord.ext.commands import Bot
from dotenv import load_dotenv
from main_cog import MainCog
from music_cog import MusicCog
from utils import safe_mkdir

# Load environment variables from .env file
load_dotenv()

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
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
