"""
the command wrapper of utils
"""

import discord
from discord import app_commands
from discord.ext import commands
from utils.attachment_helper import convent_attachment_to_url
from utils.hex_helper import to_color_int, normalize_hex_color


class UtilsCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    utils_group = app_commands.Group(name="utils", description="the utils of the bot")

    @utils_group.command(name="attachment_url")
    @app_commands.describe(attachment="the attachment to convent")
    async def convent_attachment(
        self, interaction: discord.Interaction, attachment: discord.Attachment
    ) -> None:
        """convent attachment to discord MDN url"""
        await interaction.response.send_message(
            f"""the attachment url:
                ```text
                {convent_attachment_to_url(attachment)}
                ```
                """,
            ephemeral=True,
        )

    @utils_group.command(name="hex_string_to_integer")
    @app_commands.describe(hex_str="the string fo the hex code (0 for invalid)")
    async def convent_hex(self, interaction: discord.Interaction, hex_str: str) -> None:
        """convent hex code to integer"""
        await interaction.response.send_message(
            f"""the integer result:
                                                ```text
                                                {to_color_int(hex_str)}
                                                ```
                                                """,
            ephemeral=True,
        )

    @utils_group.command(name="normalize_hex_color_str")
    @app_commands.describe(hex_str="the str to normalize")
    async def normalize(self, interaction: discord.Interaction, hex_str: str) -> None:
        """normalize the hex str to #RRGGBB"""
        await interaction.response.send_message(f"""the result:
                                        ```text
                                        {normalize_hex_color(hex_str)}
                                        ````
                                        """)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(UtilsCog(bot))
