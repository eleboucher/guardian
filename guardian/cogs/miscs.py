import logging
import subprocess
from discord.ext.commands import Bot, Cog, command


log = logging.getLogger(__name__)


class Misc(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @command()
    async def meteo(self, ctx, *args):
        location = "+".join(args) or "48.90,2.32"
        data = subprocess.run(
            ["curl", "-s", f"fr.wttr.in/{location}?T0"], stdout=subprocess.PIPE
        )
        await ctx.send(f"```{data.stdout.decode('utf-8')}```")


def setup(bot):
    bot.add_cog(Misc(bot))
    log.info("Cog loaded: Misc")
