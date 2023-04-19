import asyncio

import discord
from discord.ext.commands import Bot, Cog, Context, command
from utils import Playlist, search_yt


class MusicCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

        # all the music related stuff
        self.is_playing = False

        # 2d array containing [song, channel]
        self.music_queue = []
        self.FFMPEG_OPTIONS = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }

        self.voice_channel = ""

    def play_next(self, ctx: Context) -> None:
        if self.music_queue:
            # remove the first element as you are going to play it
            music = self.music_queue.pop(0)[0]

            # get the music url
            music_url = music["url"]

            self.voice_channel.play(
                discord.FFmpegPCMAudio(music_url, **self.FFMPEG_OPTIONS),
                after=lambda e: self.play_next(ctx),
            )
        else:
            self.is_playing = False

    async def play_music(self, ctx: Context) -> None:
        """Infinite loop checking."""

        if self.music_queue:
            self.is_playing = True

            # remove the first element as you are going to play it
            music, channel = self.music_queue.pop(0)

            # get the music url
            music_url = music["url"]

            # try to connect to voice channel if you are not already connected
            if (
                self.voice_channel == ""
                or self.voice_channel is None
                or not self.voice_channel.is_connected()
            ):
                self.voice_channel = await channel.connect()
            elif self.voice_channel != channel:
                self.voice_channel.move_to(channel)

            # play the music using FFMPEG
            self.voice_channel.play(
                discord.FFmpegPCMAudio(music_url, **self.FFMPEG_OPTIONS),
                after=lambda e: self.play_next(ctx),
            )

            await ctx.send(
                f'Playing {music["title"]} for the next {music["duration"]} seconds!'
            )
        else:
            await ctx.send("No music in queue..")
            self.is_playing = False

            await asyncio.sleep(60)

            if not self.is_playing:
                await self.exit(ctx)

    @command(aliases=["p"])
    async def play(self, ctx: Context, *args) -> None:
        """Plays a selected song from youtube"""
        query = " ".join(args)

        try:
            voice_channel = ctx.author.voice.channel
        except AttributeError:
            voice_channel = None

        if not voice_channel:
            # you need to be connected so that the bot knows where to go
            embed = discord.Embed(
                description="Connect to a voice channel!",
                color=discord.Color.green(),
            )
            return await ctx.send(embed=embed)
        else:
            song = search_yt(query)
            if isinstance(song, bool):
                await ctx.send(
                    "Could not download the song. Incorrect format try another keyword. This could be due to playlist "
                    "or a livestream format."
                )
            else:
                self.music_queue.append([song, voice_channel])

                if self.is_playing:
                    await ctx.send(
                        f'Song added to the queue: {song["title"]}! \nDuration: {song["duration"]}'
                    )
                else:
                    await self.play_music(ctx)

    @command()
    async def pause(self, ctx: Context) -> None:
        """Pause the currently playing song."""
        vc = ctx.voice_client

        if not vc or not vc.is_playing():
            embed = discord.Embed(
                description="I am currently not playing anything.",
                color=discord.Color.green(),
            )
            return await ctx.send(embed=embed)
        elif vc.is_paused():
            return

        vc.pause()
        await ctx.send("Paused ⏸️")

    @command()
    async def resume(self, ctx: Context) -> None:
        """Resume the currently paused song"""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(
                description="I'm not connected to a voice channel.",
                color=discord.Color.green(),
            )
            return await ctx.send(embed=embed)
        elif not vc.is_paused():
            return

        vc.resume()
        await ctx.send("Resuming ⏯️")

    @command(aliases=["q"])
    async def queue(self, ctx: Context, list_to_me=True) -> None:
        """Displays the current songs in queue"""
        if self.music_queue:
            number_of_musics = len(self.music_queue)

            if number_of_musics == 1:
                await ctx.send("1 music in queue!")
            else:
                await ctx.send(f"{number_of_musics} musics in queue!")

            if list_to_me:
                list_queue = ""

                for i, music in enumerate(self.music_queue):
                    list_queue += f'{i+1} - {music[0]["title"]}\n'

                await ctx.send(list_queue)
        else:
            await ctx.send("No music in queue..")

    @command(aliases=["add_to_p", "add_t_p"])
    async def add_to_playlist(self, ctx: Context, *args) -> None:
        """Adds a music to the specified playlist
        Examples:
            .add_to_playlist sweet but psycho @@playlist name
        """
        try:
            music, playlist_name = " ".join(args).split("@@")
        except ValueError:
            await ctx.send("Playlist marker not found at the end: @@playlist")
            return

        playlist = Playlist(name=playlist_name)
        added = playlist.add(music=music)
        if added:
            await ctx.send(f"Adding \"{added['title']}\" to @@{playlist.name}")
        else:
            await ctx.send(
                f"An error has occurred, please try with another music name."
            )

    @command(aliases=["remove_from_p", "remove_f_p"])
    async def remove_from_playlist(self, ctx: Context, *args) -> None:
        """Removes all occurrences of a music from the specified playlist
        Examples:
            .remove_from_playlist sweet but psycho @@playlist name
        """
        try:
            music, playlist_name = " ".join(args).split("@@")
        except ValueError:
            await ctx.send("Playlist marker not found at the end: @@playlist")
            return

        playlist = Playlist(name=playlist_name)
        songs_removed = playlist.remove(music=music)
        await ctx.send(
            f"{songs_removed} occurrences found and removed from the playlist."
        )

    @command(aliases=["delete_p", "del_p"])
    async def delete_playlist(self, ctx: Context, *args) -> None:
        """Deletes the given playlist.
        Examples:
            .delete_playlist playlist name
        """
        playlist = Playlist(name=" ".join(args))
        playlist.purge()
        await ctx.send(f"Playlist @@{playlist.name} deleted.")

    @command(aliases=["p_playlist", "p_p", "pp"])
    async def play_playlist(self, ctx: Context, *args) -> None:
        """Add the musics to the given playlist to the queue.
        Examples:
            .play_playlist playlist name
        """
        try:
            voice_channel = ctx.author.voice.channel
        except AttributeError:
            voice_channel = None

        if not voice_channel:
            # you need to be connected so that the bot knows where to go
            embed = discord.Embed(
                description="Connect to a voice channel!",
                color=discord.Color.green(),
            )
            return await ctx.send(embed=embed)

        playlist = Playlist(name=" ".join(args))
        for song in playlist.musics:
            self.music_queue.append([song, voice_channel])

        if self.is_playing:
            await ctx.send("All songs added to the and of the current queue.")
        else:
            await self.play_music(ctx)

    @command(aliases=["list_p", "l_p"])
    async def list_playlist(self, ctx: Context, *args) -> None:
        """Displays the current songs in the playlist."""
        playlist = Playlist(name=" ".join(args))
        if playlist.musics:
            await ctx.send(f"{len(playlist.musics)} music(s) in queue!")

            list_queue = ""

            for i, music in enumerate(playlist.musics):
                list_queue += f'{i+1} - {music["title"]}\n'

            await ctx.send(list_queue)
        else:
            await ctx.send("No musics in playlist..")

    @command(aliases=["jump", "j"])
    async def skip(self, ctx: Context) -> None:
        """Skips the current song being played"""
        if self.voice_channel != "" and self.voice_channel:
            self.voice_channel.stop()

            # try to play next in the queue if it exists
            await self.play_music(ctx)

    @command(aliases=["quit", "stop"])
    async def exit(self, ctx: Context) -> None:
        """Removes the bot from the channel"""
        if self.voice_channel != "" and self.voice_channel.is_connected():
            self.voice_channel.stop()
            await self.voice_channel.disconnect()
