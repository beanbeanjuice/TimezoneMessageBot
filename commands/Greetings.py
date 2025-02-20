from discord import app_commands
from discord.ext import commands

class Greetings(commands.Cog):
    def __init__(self, bot):
        self._bot = bot
        print("Enabling Greetings Module")

    @app_commands.command(name="ping", description="Ping the bot.")
    async def ping(self, interaction):
        await interaction.response.send_message("Pong!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Greetings(bot))
