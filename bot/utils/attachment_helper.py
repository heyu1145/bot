"""
discord attachment convent helper
"""
from discord import Attachment, File
import discord


def convent_attachment_to_url(attachment: Attachment) -> str:
    """
    Convent a discord attachment to discord CDN url
    """
    return attachment.url


def check_attachment_is_image(attachment: Attachment) -> bool:
    """
    check a attachment is a image or not
    """
    return attachment.content_type.startswith("image/") if attachment.content_type else False


async def convent_attachment_to_file(attachments: list[Attachment]) -> list[File | None]:
    """
    convent attachments to file object (None for failed)
    """
    result: list[File | None] = []
    for i, attachment in enumerate(attachments):
        try:
            result[i] = await attachment.to_file()
        except (discord.HTTPException, discord.Forbidden, discord.NotFound):
            result[i] = None

    return result
