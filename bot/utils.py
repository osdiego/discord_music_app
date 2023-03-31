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
