"""
message groups cog
"""
import json
import discord
from discord import app_commands
from discord.ext import commands
from utils.attachment_helper import check_attachment_is_image, convent_attachment_to_url
from utils.embed_json_handler import convent_embed_json
from utils.hex_helper import to_color_int

class MessagesCommands(commands.Cog):
    """
    message groups cog
    """
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    send_group = app_commands.Group(
            name="send",
            description="send messages to channels by bot",
            guild_only=True
            )

    embed_group = app_commands.Group(
            name="embed", 
            description="send embed messages to channels by bot", 
            parent=send_group,
            guild_only=True
            )

    @send_group.command(name="text")
    @app_commands.describe(
            channel="the channel to send the message to",
            message="the message to send",
            attachment="the file to send"
            )
    async def send_text(
            self, 
            interaction: discord.Interaction,
            channel: discord.TextChannel,
            message: str,
            attachment: discord.Attachment | None = None
            ) -> None:
        """
        send a text message to a channel
        """
        await interaction.response.defer(ephemeral=True)
        if not interaction.guild:
            raise app_commands.CheckFailure("This command can only be used in a guild.")
        
        if not channel.permissions_for(interaction.guild.me).send_messages:
            raise app_commands.BotMissingPermissions(["send_messages"])

        if attachment:
            msg = await channel.send(message, file=(await attachment.to_file()))
        else:
            msg = await channel.send(message)

        embed = discord.Embed(
                title="Message Sent",
                description=f"Message sent to {channel.jump_url}, message jump url at [here]({msg.jump_url})",
                color=discord.Color.green()
                )

        await interaction.followup.send(embed=embed, ephemeral=True)


    @embed_group.command(name="custom")
    @app_commands.describe(
        channel="the channel to send the embed message to",
        title="the title of the embed message",
        description="the description of the embed message",
        color="the color of the embed message ( hex code, full black if invalid )",
        add_timestamp="should bot add timestamp in embed",
        footer="the footer of the embed message",
        author="the author of the embed message"
    )
    async def send_embed(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        description: str,
        add_timestamp: bool,
        title: str | None = None,
        color: str = "0000FF",
        footer: str | None = None,
        author: str | None = None
    ) -> None:
        """
        send a custom embed message to a channel
        """
        if not interaction.guild:
            raise app_commands.CheckFailure("This command can only be used in a guild.")
        
        if not channel.permissions_for(interaction.guild.me).send_messages:
            raise app_commands.BotMissingPermissions(["send_messages"])

        color_int = to_color_int(color)

        embed = discord.Embed(
            title=title,
            description=description,
            color=color_int,
            timestamp=discord.utils.utcnow() if add_timestamp else None
        )
        embed.set_footer(text=footer)
        if author:
            embed.set_author(name=author)

        msg = await channel.send(embed=embed)

        response_embed = discord.Embed(
                title="Embed Message Sent",
                description=f"Embed message sent to {channel.jump_url}, message jump url at [here]({msg.jump_url})",
                color=discord.Color.green()
                )

        await interaction.response.send_message(embed=response_embed, ephemeral=True)

    @embed_group.command(name="advanced")
    @app_commands.describe(
            channel="the channel to send to",
            title="the title of the embed message",
            add_timestamp="include timestamp or not",
            description="the description of the embed message",
            color="the color of the embed message",
            image="the image of the embed message",
            thumbnail="the thumbnail of the embed message",
            footer="the footer of the embed message",
            author="the author ofbthe embed message",
            )
    async def send_embed_advanced(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        description: str,
        add_timestamp: bool,
        title: str | None = None,
        color: str = "0000FF",
        image: discord.Attachment | None = None,
        thumbnail: discord.Attachment | None = None,
        footer: str | None = None,
        footer_icon: discord.Attachment | None = None,
        author: str | None = None,
        author_icon: discord.Attachment | None = None,
    ) -> None:
        """
        send advanced embed ( use embed json for fields support )
        """

        await interaction.response.defer(ephemeral=True)

        if not interaction.guild:
            raise app_commands.CheckFailure("This command can only used in guild!")

        if not channel.permissions_for(interaction.guild.me).send_messages:
            raise app_commands.BotMissingPermissions(["send_messages"])

        embed = discord.Embed(
                title=title,
                description=description,
                timestamp=discord.utils.utcnow() if add_timestamp else None,
                color=to_color_int(color)
        )
        embed.set_footer(
                text=footer, 
                icon_url=convent_attachment_to_url(footer_icon) 
                    if footer_icon and check_attachment_is_image(footer_icon) 
                    else None
                )

        embed.set_author(
                name=author if author else "",
                icon_url=convent_attachment_to_url(author_icon)
                    if author_icon and check_attachment_is_image(author_icon)
                    else None
            )

        embed.set_image(url=convent_attachment_to_url(image)
                            if image and check_attachment_is_image(image)
                            else None
                        )

        embed.set_thumbnail(url=convent_attachment_to_url(thumbnail)
                                if thumbnail and check_attachment_is_image(thumbnail)
                                else None
                            )

        msg = await channel.send(embed=embed)

        response_embed = discord.Embed(
                title="Embed Sent",
                description=f"Embed message sent to {channel.jump_url}, message jump url at [here]({msg.jump_url}).",
                color=discord.Color.green()
        )
        await interaction.followup.send(embed=response_embed, ephemeral=True)
 
    @embed_group.command(name="json")
    @app_commands.describe(
        channel="the channel to send the embed message to",
        json_str="the json of the embed message"
    )
    async def send_embed_json(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        json_str: str
    ) -> None:
        """
        send a send by json following webhook format
        """

        await interaction.response.defer(ephemeral=True)

        if not interaction.guild:
            raise app_commands.CheckFailure("This command can only be used in a guild.")
        
        if not channel.permissions_for(interaction.guild.me).send_messages:
            raise app_commands.BotMissingPermissions(["send_messages"])

        try:
            json_obj = json.loads(json_str)
            ok, data, errembed = convent_embed_json(json_obj)
            if not ok:
                await interaction.followup.send(embed=errembed, ephemeral=True)
            if not data:
                return
        except (json.JSONDecodeError):
            raise RuntimeError("The JSON String is Invalid, Please try again with right format")

        embed = discord.Embed.from_dict(data)
        try:
            msg = await channel.send(embed=embed)
        except discord.HTTPException as e:
            tit, desc, *_ = e.text.splitlines()

            resp_embed = discord.Embed(
                title=tit,
                description=desc,
                color=discord.Color.red()
            )
            resp_embed.add_field(
                    name="hint",
                    value="view [webhook format]"
                    +"(https://discord.com/developers/docs/resources/message#embed-object) for details",
                    inline=False
            )
            await interaction.followup.send(embed=resp_embed, ephemeral=True)
            return

        response_embed = discord.Embed(
                title="Embed Message Sent",
                description=f"Embed message sent to {channel.jump_url}, message jump url at [here]({msg.jump_url})",
                color=discord.Color.green()
                )

        await interaction.followup.send(embed=response_embed, ephemeral=True)

 


async def setup(bot: commands.Bot) -> None:
    """
    setup function for the cog
    """
    await bot.add_cog(MessagesCommands(bot))
