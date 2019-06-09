import asyncio
import logging
import discord
import os

from discord.ext.commands import Cog, command

from utils import get_internship

log = logging.getLogger(__name__)

TOKEN_URL = "https://api.intra.42.fr/oauth/token"

BASE_URL = "https://api.intra.42.fr/v2"


class FortyTwo(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = os.getenv("FORTYTWO_KEY")
        self.secret = os.getenv("FORTYTWO_SECRET")
        self.token = None

    async def _fetch_token(self):
        log.info("getting new token")
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client,
            "client_secret": self.secret,
        }
        response = await self.bot.http_session.post(TOKEN_URL, json=payload)
        print("status code :", response.status)
        content = await response.json()
        return content["access_token"]

    async def get(self, url):
        if not self.token:
            self.token = await self._fetch_token()
        header = {"Authorization": f"Bearer {self.token}"}
        response = await self.bot.http_session.get(BASE_URL + url, headers=header)
        if response.status == 401:
            self.token = await self._fetch_token()
            return await self.get(url)
        elif response.status == 403:
            asyncio.sleep(int(response.headers["Retry-After"]))
            return await self.get(url)
        return await response.json()

    async def post(self, url, body):
        header = {"Authorization": f"Bearer {self.token}"}
        response = await self.bot.http_session.get(
            BASE_URL + url, data=body, headers=header
        )
        if response.status == 401:
            self.token = await self._fetch_token()
            return await self.post(url)
        elif response.status == 403:
            asyncio.asleep(int(response.headers["Retry-After"]))
            return await self.post(url)
        return await response.json()

    @command()
    async def profile(self, ctx, username):
        log.info(f"profil for username {username}")
        url = f"/users/{username}"
        url_coalition = f"{url}/coalitions/"
        user_data = await self.get(url)
        if not user_data or user_data == {}:
            return

        coalition_data = await self.get(url_coalition)
        location = user_data.get("location") or "Unavailable"
        number = user_data.get("phone") or "Hidden"
        cursus_level = "\n".join(
            [
                f"{cursus_users.get('cursus').get('name')}: "
                + f"{cursus_users.get('level'):02.02f}"
                for cursus_users in user_data.get("cursus_users")
            ]
        )
        title = (
            f"{user_data.get('displayname')} {username} - "
            + f"{coalition_data[-1].get('slug')}"
        )

        embed = discord.Embed(
            title=title,
            colour=discord.Colour(
                int(coalition_data[-1].get("color", "#D40000").replace("#", ""), 16)
            ),
            url=f"https://profile.intra.42.fr/users/{username}",
        )
        embed.set_thumbnail(url=user_data.get("image_url"))

        embed.add_field(name="Level", value=cursus_level)
        embed.add_field(
            name="Internship", value=get_internship(user_data.get("projects_users"))
        )
        embed.add_field(name="Location", value=location)
        embed.add_field(
            name="Contact", value=f"Phone: {number}\nEmail: {user_data['email']}"
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(FortyTwo(bot))
    log.info("Cog loaded: FortyTwo")
