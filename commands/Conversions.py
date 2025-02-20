import re
from datetime import datetime

import pytz
from discord import app_commands
from discord.ext import commands

def string_to_timezone(timezone_input: str):
    try:
        return pytz.timezone(timezone_input)
    except pytz.exceptions.UnknownTimeZoneError:
        return None


async def timezone_autocomplete(interaction, current: str):
    current_lower = current.lower()
    filtered = [tz for tz in pytz.all_timezones if tz.lower().startswith(current_lower)]

    if len(filtered) < 25:
        extra = [
            tz for tz in pytz.all_timezones
            if current_lower in tz.lower() and tz not in filtered
        ]
        filtered.extend(extra)

    return [app_commands.Choice(name=tz, value=tz) for tz in filtered][:25]

def convert_to_unix_timestamp(date: str, timezone) -> int:
    dt = datetime.strptime(date, "%B %d, %Y @ %I:%M %p")
    local_dt = timezone.localize(dt)
    timestamp = local_dt.timestamp()
    return int(timestamp)

def replace_with_timestamp(match, tz):
    # Extract the date string inside convert{...}
    date_string = match.group(1)
    try:
        timestamp = convert_to_unix_timestamp(date_string, tz)
        return f"<t:{timestamp}:t>"
    except Exception as e:
        # If conversion fails, return the original string or an error marker.
        return match.group(0)

class Conversions(commands.Cog):
    def __init__(self, bot):
        self._bot = bot
        print("Enabling Conversions Module")

    @app_commands.command(name="convert", description="Convert your message to the proper timezones.")
    @app_commands.describe(timezone="The timezone you want to use.")
    @app_commands.autocomplete(timezone=timezone_autocomplete)
    @app_commands.describe(message_id="The ID of the message you want to convert.")
    async def convert(self, interaction, timezone: str, message_id: str):
        try:
            message = await interaction.channel.fetch_message(int(message_id))
        except Exception as e:
            await interaction.response.send_message("Could not find that message.", ephemeral=True)
            return

        tz = string_to_timezone(timezone)

        if tz is None:
            await interaction.response.send_message(f"Invalid TimeZone: {timezone}", ephemeral=True)
            return

        content = message.content

        # Dates will be in the pattern convert{Month Day, Year @ Hour:Minute AM/PM}
        # Find all occurrences of 'convert{...}' with non-greedy matching
        results = re.findall(r'convert{(.*?)}', content)

        if not results:
            await interaction.response.send_message(
                "No valid date formats found. As an example, use convert{January 11, 2025 @ 5:34 PM}.",
                ephemeral=True
            )
            return

        new_content = re.sub(r'convert{(.*?)}', lambda m: replace_with_timestamp(m, tz), content)

        await interaction.response.send_message(f"{new_content}")


async def setup(bot):
    await bot.add_cog(Conversions(bot))
