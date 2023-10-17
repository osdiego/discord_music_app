import json
import os
from typing import Union

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError


class MusicQueue:
    def __init__(self) -> None:
        self.queue = list()

    def next_music(self) -> dict:
        return self.queue.pop(0)

    def add_music(self, music) -> None:
        self.queue.append(music)


class Channel:
    def __init__(self, channel_id) -> None:
        self.id = channel_id
        self.music_queue = MusicQueue()


class ChannelManager:
    def __init__(self) -> None:
        self.channels = dict()

    def __add_channel(self, channel_id) -> Channel:
        channel = Channel(channel_id=channel_id)
        self.channels[channel_id] = channel
        return channel

    def get_channel(self, channel_id) -> Channel:
        try:
            channel = self.channels[channel_id]
        except KeyError:
            channel = self.__add_channel(channel_id=channel_id)
        return channel


def safe_mkdir(folder: str) -> None:
    """Creates a directory if it doesn't already exist.

    Args:
        folder (str): path of folder to be created.
    """
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"Created {folder}")


def search_yt(item: str) -> Union[bool, dict[str, Union[str, int]]]:
    """Searching the item on YouTube."""
    YDL_OPTIONS = {
        "format": "bestaudio/best",
        "noplaylist": False,
    }
    with YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            print("Trying default download")
            info = ydl.extract_info(item, download=False)

            if "_type" in info.keys() and info["_type"] == "playlist":
                if len(info["entries"]) == 0:
                    raise ValueError("No musics found in YouTube playlist.")

                songs = [
                    {
                        "title": song["title"],
                        "duration": song["duration"],
                        "url": song["url"],
                    }
                    for song in info["entries"]
                ]
                return songs

            return [
                {
                    "title": info["title"],
                    "duration": info["duration"],
                    "url": info["url"],
                }
            ]

        except DownloadError:
            print("Trying search download")
            info = ydl.extract_info("ytsearch:%s" % item, download=False)

            info = info["entries"][0]
            return [
                {
                    "title": info["title"],
                    "duration": info["duration"],
                    "url": info["url"],
                }
            ]


class Playlist:
    def __init__(self, name: str) -> None:
        self.name = name
        self.__load_musics()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str):
        if hasattr(self, "name"):
            old_file_name = self.file_name
        self._name = " ".join(value.split())

        try:
            os.rename(old_file_name, self.file_name)
        except (FileNotFoundError, FileExistsError, UnboundLocalError):
            pass

    @property
    def file_name(self):
        file_name = [l for l in self.name if l.isalpha() or l.isdigit() or l.isspace()]
        return "playlists/" + "".join(file_name).replace(" ", "_").lower() + ".json"

    def __load_musics(self):
        try:
            with open(self.file_name) as p_file:
                self._musics = json.load(p_file)
        except FileNotFoundError:
            self._musics = []

    @property
    def musics(self) -> list[dict]:
        return self._musics

    @musics.setter
    def musics(self, value: list):
        self._musics = value
        with open(self.file_name, "w") as outfile:
            json.dump(obj=self.musics, fp=outfile, indent=4)

    def add(self, music: str) -> bool:
        music = search_yt(music)
        if music:
            self.musics = self.musics + [music]
            return music
        return False

    def remove(self, music: str):
        music = music.strip()
        musics_to_be_removed = len([m for m in self.musics if m["title"] == music])
        if musics_to_be_removed:
            self.musics = [m for m in self.musics if m["title"] != music]
        return musics_to_be_removed

    def purge(self):
        try:
            os.remove(self.file_name)
        except FileNotFoundError:
            pass
