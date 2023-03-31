"""
Prototype of new feature. Not ready to use.
"""
import os
import random
import shutil

import discord
from discord.ext import commands
from google_images_download import google_images_download


# responsible for handling all of the image commands
class image_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.download_folder = "downloads"

        self.keywords = "Spongebob"

        self.response = google_images_download.googleimagesdownload()
        self.arguments = {
            "keywords": self.keywords,
            "limit": 20,
            "size": "medium",
            "no_directory": True,
        }

        self.image_names = []
        # get the latest in the folder
        self.update_images()

    @commands.command(name="get")
    async def get(self, ctx):
        """Displays random image from the downloads"""
        img = self.image_names[random.randint(0, len(self.image_names) - 1)]
        await ctx.send(file=discord.File(img))

    def clear_folder(self):
        for filename in os.listdir(self.download_folder):
            file_path = os.path.join(self.download_folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print("Failed to delete %s. Reason: %s" % (file_path, e))

    def update_images(self):
        self.image_names = []
        # store all the names to the files
        for filename in os.listdir(self.download_folder):
            self.image_names.append(os.path.join(self.download_folder, filename))

    @commands.command(name="search")
    async def search(self, ctx, *args):
        """Searches for a message on Google"""
        self.clear_folder()

        # fill the folder with new images
        self.arguments["keywords"] = " ".join(args)
        self.response.download(self.arguments)

        self.update_images()
