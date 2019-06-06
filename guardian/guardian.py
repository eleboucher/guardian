import discord
import os

from process import process_message

client = discord.Client()


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        # check if it's not the bot
        return

    if message.content.startswith("!"):
        process_message(message)


if __name__ == "__main__":
    client.run(os.getenv("DISCORD_TOKEN"))
