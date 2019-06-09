import io
import json
import logging

from discord import File
from discord.ext.commands import Bot, Cog, command

from utils import save_json_to_file

log = logging.getLogger(__name__)


class Emote(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def get_global_emote(self, emote_name):
        try:
            data = await self.bot.http_session.get(
                url="https://twitchemotes.com/api_cache/v3/global.json"
            )
            content = await data.json()
            return content.get(emote_name)
        except Exception as e:
            print(e)
            return False

    async def get_subscriber_file(self):
        try:
            with open("./subscriber.json") as fp:
                data = json.load(fp)
                return data
        except FileNotFoundError:
            data = await self.bot.http_session.get(
                url="https://twitchemotes.com/api_cache/v3/subscriber.json"
            )
            content = await data.json()
            save_json_to_file(content, "./subscriber.json")
            return content

    async def get_subscriber_emote(self, emote_name):
        channels = await self.get_subscriber_file()

        for _, channel in channels.items():
            try:
                emote = next(
                    emote for emote in channel["emotes"] if emote["code"] == emote_name
                )

                if emote:
                    return emote
            except StopIteration:
                pass
        return False

    @command(aliases=("e",), description="Get a twitch emote")
    async def emote(self, ctx, emote_name: str):
        log.info(f"command emote with args {emote_name}")
        emote = await self.get_global_emote(emote_name)
        if not emote:
            emote = await self.get_subscriber_emote(emote_name)
            if not emote:
                return
        url = f"https://static-cdn.jtvnw.net/emoticons/v1/{emote['id']}/5.0"
        response = await self.bot.http_session.get(url=url)
        content = await response.read()
        image = io.BytesIO(content)
        await ctx.send(file=File(image, f"{emote['code']}.png"))


def setup(bot):
    bot.add_cog(Emote(bot))
    log.info("Cog loaded: Emote")
