import discord
from datetime import datetime
import asyncio

async def generate_transcript(thread: discord.Thread, close_reason: str = None, closer: discord.User = None) -> str:
    transcript = []
    transcript.append(f"=== Ticket Transcript - {thread.name} ===")
    transcript.append(f"Created: {thread.created_at.strftime('%Y-%m-%d %H:%M UTC')}")
    transcript.append(f"Creator: {thread.owner.name} (ID: {thread.owner.id})")
    transcript.append(f"Closed: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    if closer:
        transcript.append(f"Closed by: {closer.name} (ID: {closer.id})")
    if close_reason:
        transcript.append(f"Close Reason: {close_reason}")
    transcript.append("\n=== Conversation ===\n")
    messages = []
    async for msg in thread.history(limit=None, oldest_first=True):
        messages.append(msg)
    for msg in messages:
        timestamp = msg.created_at.strftime('%H:%M:%S')
        transcript.append(f"[{timestamp}] {msg.author.name}: {msg.content or '[Attachment/Embed]'}")
    return "\n".join(transcript)