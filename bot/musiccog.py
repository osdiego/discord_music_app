import asyncio

import discord
from discord.ext import commands
from yt_dlp import YoutubeDL


class MusicCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # all the music related stuff
        self.is_playing = False

        # 2d array containing [song, channel]
        self.music_queue = []
        # self.YDL_OPTIONS = {
        #     "format": "bestaudio/best",
        #     "restrictfilenames": True,
        #     "noplaylist": True,
        #     "nocheckcertificate": True,
        #     "ignoreerrors": False,
        #     "logtostderr": False,
        #     "quiet": True,
        #     "no_warnings": True,
        #     "default_search": "auto",
        #     "source_address": True,
        # }
        self.YDL_OPTIONS = {
            "format": "bestaudio",
            "noplaylist": True,
        }
        self.FFMPEG_OPTIONS = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }

        self.voice_channel = ""

    def search_yt(self, item):
        """
        Searching the item on youtube.
        """
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download=False)[
                    "entries"
                ][0]
            except Exception as error:
                print(error)
                print(type(error))
                return False

        return {
            "source": info["formats"][0]["url"],
            "title": info["title"],
            "duration": info["duration"],
        }

    def play_next(self, ctx) -> None:
        if self.music_queue:
            # remove the first element as you are going to play it
            music, channel = self.music_queue.pop(0)

            # get the music url
            music_url = music["source"]

            self.voice_channel.play(
                discord.FFmpegPCMAudio(music_url, **self.FFMPEG_OPTIONS),
                after=lambda e: self.play_next(ctx),
            )
        else:
            self.is_playing = False

    async def play_music(self, ctx: object) -> None:
        """
        Infinite loop checking.
        """

        if self.music_queue:
            self.is_playing = True

            # remove the first element as you are going to play it
            music, channel = self.music_queue.pop(0)
            print(music)
            print(channel)

            # get the music url
            music_url = music["source"]
            print(music_url)

            # try to connect to voice channel if you are not already connected
            if (
                self.voice_channel == ""
                or self.voice_channel is None
                or not self.voice_channel.is_connected()
            ):
                self.voice_channel = await channel.connect()
            elif self.voice_channel != channel:
                self.voice_channel.move_to(channel)

            print(self.voice_channel)
            # play the music using FFMPEG
            self.voice_channel.play(
                discord.FFmpegPCMAudio(music_url, **self.FFMPEG_OPTIONS),
                after=lambda e: self.play_next(ctx),
            )
            print(4)

            await ctx.send(
                f'Playing {music["title"]} for the next {music["duration"]} seconds!'
            )
            print(5)
        else:
            await ctx.send("No music in queue..")
            self.is_playing = False

            await asyncio.sleep(60)

            if not self.is_playing:
                await self.exit(ctx)

    @commands.command(aliases=["p"], help="Plays a selected song from youtube")
    async def play(self, ctx: object, *args) -> None:
        query = " ".join(args)

        actual_voice_channel = ctx.author.voice.channel
        if actual_voice_channel is None:
            print(11111)
            # you need to be connected so that the bot knows where to go
            await ctx.send("Connect to a voice channel!")
        else:
            print(111111111111111111111111111111111)
            song = self.search_yt(query)
            if isinstance(song, bool):
                await ctx.send(
                    "Could not download the song. Incorrect format try another keyword. This could be due to playlist "
                    "or a livestream format."
                )
            else:
                self.music_queue.append([song, actual_voice_channel])

                if self.is_playing:
                    await ctx.send(
                        f'Song added to the queue: {song["title"]}! \nDuration: {song["duration"]}'
                    )
                else:
                    await self.play_music(ctx)

    @commands.command(aliases=["q"], help="Displays the current songs in queue")
    async def queue(self, ctx: object, list_to_me=True) -> None:
        if self.music_queue:
            number_of_musics = len(self.music_queue)

            if number_of_musics == 1:
                await ctx.send("1 music in queue!")
            else:
                await ctx.send(f"{number_of_musics} musics in queue!")

            if list_to_me:
                list_queue = ""

                for i in range(0, number_of_musics):
                    list_queue += f'{i+1} - {self.music_queue[i][0]["title"]}\n'

                await ctx.send(list_queue)
        else:
            await ctx.send("No music in queue..")

    @commands.command(aliases=["jump", "j"], help="Skips the current song being played")
    async def skip(self, ctx: object) -> None:
        if self.voice_channel != "" and self.voice_channel:
            self.voice_channel.stop()

            # try to play next in the queue if it exists
            await self.play_music(ctx)

    @commands.command(aliases=["quit"], help="Removes the bot from the channel")
    async def exit(self, ctx: object) -> None:
        if self.voice_channel != "" and self.voice_channel.is_connected():
            self.voice_channel.stop()
            await self.voice_channel.disconnect()
