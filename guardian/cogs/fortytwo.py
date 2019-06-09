import asyncio
import logging
import os
from datetime import datetime

import discord
from discord.ext.commands import Bot, Cog, command

from utils import format_timedelta, get_internship

log = logging.getLogger(__name__)

TOKEN_URL = "https://api.intra.42.fr/oauth/token"

BASE_URL = "https://api.intra.42.fr/v2"


class FortyTwo(Cog):
    def __init__(self, bot: Bot):
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
    async def score(self, ctx):
        log.info(f"score")
        url = f"/blocs/1/coalitions"
        data = await self.get(url)
        data.sort(key=lambda i: i["score"], reverse=True)
        embed = discord.Embed(
            title="Score:",
            color=int(data[0].get("color", "#D40000").replace("#", ""), 16),
            description=f"{data[0].get('name')} domine !",
        )
        embed.set_footer(text="Powered by the Guardian")

        for idx, coa in enumerate(data):
            diff = f"({int(coa['score'] - data[0]['score'])})" if idx > 0 else ""
            score = f"{coa['score']} {diff}"
            embed.add_field(
                name=f"{idx + 1} - {coa['name']}", value=score, inline=False
            )
        await ctx.send(embed=embed)

    @command()
    async def where(self, ctx, login):
        log.info(f"where for login {login}")
        url = f"/users/{login}/locations"
        data = await self.get(url)
        ret = ""
        if len(data) == 0 or data[0]["end_at"] is not None:
            diff = datetime.now() - datetime.strptime(
                data[0]["end_at"], "%Y-%m-%dT%H:%M:%S.%fZ"
            )
            formated_diff = format_timedelta(diff)
            ret = f"*{login}* est hors ligne depuis {formated_diff}"
        else:
            ret = f"*{login}* est à la place *{data[0]['host']}*"
        await ctx.send(ret)

    @command()
    async def profile(self, ctx, login):
        log.info(f"profil for login {login}")
        url = f"/users/{login}"
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
            f"{user_data.get('displayname')} {login} - "
            + f"{coalition_data[-1].get('slug')}"
        )

        embed = discord.Embed(
            title=title,
            colour=discord.Colour(
                int(coalition_data[-1].get("color", "#D40000").replace("#", ""), 16)
            ),
            url=f"https://profile.intra.42.fr/users/{login}",
        )
        embed.set_thumbnail(url=user_data.get("image_url"))
        embed.set_footer(text="Powered by the Guardian")

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
