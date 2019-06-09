import logging
import os
import socket

from aiohttp import AsyncResolver, ClientSession, TCPConnector
from discord.ext.commands import Bot, when_mentioned_or
from dotenv import load_dotenv

from constant import prefix

load_dotenv(verbose=True)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

bot = Bot(command_prefix=when_mentioned_or(prefix), case_insensitive=True)


@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")


bot.http_session = ClientSession(
    connector=TCPConnector(resolver=AsyncResolver(), family=socket.AF_INET)
)

bot.load_extension("cogs.emote")
bot.load_extension("cogs.fortytwo")
bot.load_extension("cogs.miscs")

bot.run(os.getenv("DISCORD_TOKEN"))

bot.http_session.close()
