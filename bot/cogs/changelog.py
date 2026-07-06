""""""
import discord
from discord import app_commands
from discord.ext import commands
from utils.parse_changelog import InvalidVersion, Version, VersionChangelog, get_changelog, split_changelog


class ChangelogCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    changelog_group = app_commands.Group(
        name="changelog", description="changelog of bot")

    @changelog_group.command(name="show")
    async def changelog_show(self, interaction: discord.Interaction) -> None:
        """show the changelog of bot (warning: global chat, not ephemeral)"""
        await interaction.response.defer(ephemeral=False)
        cl_path = get_changelog()
        if not cl_path:
            embed = discord.Embed(
                description="could't find the changelog, connect administrator for details.",
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )

            await interaction.followup.send(embed=embed)
            return

        cl_version_data = split_changelog(cl_path)

        if not cl_version_data:
            embed = discord.Embed(
                description=("the changelog did't contain any version changes, "
                             + "connect administrator for details."),
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )

            await interaction.followup.send(embed=embed)
            return

        for data in cl_version_data:
            await interaction.followup.send(embed=changelog_to_embed(data))

    @changelog_group.command(name="latest")
    async def changelog_latest(self, interaction: discord.Interaction) -> None:
        """show the latest changelog of bot (warning: global chat, not ephemeral)"""
        await interaction.response.defer(ephemeral=False)
        cl_path = get_changelog()
        if not cl_path:
            embed = discord.Embed(
                description="could't find the changelog, connect administrator for details.",
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )

            await interaction.followup.send(embed=embed)
            return
        cl_version_data = split_changelog(cl_path)

        if not cl_version_data:
            embed = discord.Embed(
                description=("the changelog did't contain any version changes, "
                             + "connect administrator for details."),
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )

            await interaction.followup.send(embed=embed)
            return

        await interaction.followup.send(embed=changelog_to_embed(cl_version_data[0]))

    @changelog_group.command(name="search")
    @app_commands.describe(version="the version to search for")
    async def changelog_search(self, interaction: discord.Interaction, version: str) -> None:
        """search the changelog of bot by version (warning: global chat, not ephemeral)"""
        await interaction.response.defer(ephemeral=False)
        cl_path = get_changelog()
        if not cl_path:
            embed = discord.Embed(
                description="could't find the changelog, connect administrator for details.",
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )

            await interaction.followup.send(embed=embed)
            return

        cl_version_data = split_changelog(cl_path)

        if not cl_version_data:
            embed = discord.Embed(
                description=("the changelog did't contain any version changes, "
                             + "connect administrator for details."),
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )

            await interaction.followup.send(embed=embed)
            return

        try:
            version_obj = Version(version)
        except InvalidVersion:
            embed = discord.Embed(
                description=f"the version {version} is not a valid version, please check the version format.",
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )

            await interaction.followup.send(embed=embed)
            return

        for data in cl_version_data:
            if data.version == version_obj:
                await interaction.followup.send(embed=changelog_to_embed(data))
                return

        embed = discord.Embed(
            description=f"the version {version} is not found in the changelog.",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )

        await interaction.followup.send(embed=embed)


def changelog_to_embed(version: VersionChangelog) -> discord.Embed:
    """parse the changelog data to discord embed"""
    description = ""
    for name, value in version.changelog.items():
        description += f"## {name}\n"
        if not value:
            description += f"No {name} found in this version changelog\n"
            continue

        for v in value:
            description += f"- {v} \n"

        description += "\n"

    embed = discord.Embed(
        color=discord.Color.blue(),
        title=f"Version: {str(version.version)}",
        description=description,
        timestamp=discord.utils.utcnow(),
    )

    return embed


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ChangelogCog(bot))
