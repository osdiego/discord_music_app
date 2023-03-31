from discord.ext import commands


class MainCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.text_channel_list = []
        # self.help_message = """
        self.aaaaa = """

```
General commands:
/help - displays all the available commands
/clear amount - will delete the past messages with the amount specified
Image commands:
/search <keywords> - will change the search to the keyword
/get - will get the image based on the current search
Music commands:
/p <keywords> - finds the song on youtube and plays it in your current channel
/q - displays the current music queue
/skip - skips the current song being played
```
"""

    # some debug info so that we know the bot has started
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                self.text_channel_list.append(channel)
        print(f"The {self.bot.user.name} will look after you!")

    async def send_to_all(self, message: str) -> None:
        for text_channel in self.text_channel_list:
            await text_channel.send(message)

    @commands.command(aliases=["cls", "delete", "del", "purge"])
    @commands.has_permissions(manage_messages=True)
    async def clear(
        self,
        ctx: commands.Context,
        amount: int = 5,
        # to be implemented in a future release
        # like: str = None,
    ) -> None:
        """
        Delete an amount of messages from the channel.

        @param amount: (int, optional) The maximum number of messages to delete. Defaults to 5.
        """
        # @param like: (string, optional) A substring to use as a filter.
        deleted = await ctx.channel.purge(limit=amount)

        # deleted = 0
        # async for message in ctx.channel.history(limit=amount):
        #     if like is None or like.lower() in message.content.lower():
        #         await message.delete()
        #         deleted += 1

        await ctx.send(f"Just deleted {len(deleted)} messages!", delete_after=10)

    @commands.command()
    async def hello(self, ctx: commands.Context) -> None:
        """Answer you with a nice message!"""
        await ctx.send(f"Hello, {ctx.author.display_name}!", delete_after=60 * 1)

    @commands.command()
    async def garbage(self, ctx: commands.Context, amount: int) -> None:
        """Inserts a bunch of messages on the channel so you can test the clear
        command.

        Args:
            amount (int): The number of messages to be added.
        """
        for number in range(1, amount + 1):
            await ctx.send(number)
        await ctx.send("Just created a bunch of garbage..")
