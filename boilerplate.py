"""
Boilerplate helpers for the Imitation Game project.
Contains ONLY plumbing: config, Discord setup, Gemini call wrapper,
nickname assignment, and a typing-delay helper.

The game loop, player instructions, and AI prompts are NOT included.
Those are yours to write (see the TODOs at the bottom).
"""
import asyncio
import os
import random

import discord
from discord.ext import commands
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ---------- Config ----------
load_dotenv()  # reads DISCORD_TOKEN and GEMINI_API_KEY from a .env file
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3.8-flash"  # if you get "model not found", check AI Studio for available models

# ---------- Discord setup ----------
intents = discord.Intents.default()
intents.message_content = True  # also enable "Message Content Intent" in the Developer Portal
intents.members = True          # needed to change nicknames; enable "Server Members Intent" too
bot = commands.Bot(command_prefix="!", intents=intents)

# ---------- Gemini wrapper ----------
_client = genai.Client(api_key=GEMINI_API_KEY)


async def ask_model(messages: list[dict], temperature: float = 0.9) -> str:
    """
    Send a list of chat messages ({"role": "system"|"user"|"assistant", "content": ...})
    to Gemini and return the reply text. You build the messages (including the system prompt).
    """
    system = "\n".join(m["content"] for m in messages if m["role"] == "system")
    contents = [
        types.Content(role="model" if m["role"] == "assistant" else "user",
                      parts=[types.Part(text=m["content"])])
        for m in messages if m["role"] != "system"
    ]
    response = await _client.aio.models.generate_content(
        model=MODEL_NAME,
        contents=contents,
        config=types.GenerateContentConfig(system_instruction=system, temperature=temperature),
    )
    return response.text.strip()


# ---------- Anonymization helpers ----------
async def set_anonymous_nicknames(members: list[discord.Member],
                                  labels: list[str] | None = None) -> dict[int, str]:
    """
    Shuffle labels (default: 'Player A', 'Player B', ...) and assign them as
    server nicknames. Returns {member_id: label}.
    Note: the bot can't rename the server owner, and its role must sit
    above the members' roles with the "Manage Nicknames" permission.
    """
    labels = labels or [f"Player {chr(65 + i)}" for i in range(len(members))]
    shuffled = random.sample(labels, k=len(labels))
    mapping = {}
    for member, label in zip(members, shuffled):
        try:
            await member.edit(nick=label)
        except discord.Forbidden:
            print(f"Could not rename {member} (owner or role too high)")
        mapping[member.id] = label
    return mapping


async def reset_nicknames(members: list[discord.Member]) -> None:
    """Remove the nicknames so everyone returns to normal after the game."""
    for member in members:
        try:
            await member.edit(nick=None)
        except discord.Forbidden:
            pass


# ---------- Human-like response timing ----------
async def send_with_typing_delay(channel: discord.abc.Messageable, text: str,
                                 chars_per_second: float = 6.0) -> None:
    """
    Show the 'typing...' indicator and wait in proportion to message length
    (plus a little jitter) before sending, so the AI doesn't reply instantly.
    """
    delay = len(text) / chars_per_second + random.uniform(0.5, 2.0)
    async with channel.typing():
        await asyncio.sleep(min(delay, 20))  # cap so long replies aren't absurd
    await channel.send(text)


# ---------- Entry point ----------
def run_bot() -> None:
    bot.run(DISCORD_TOKEN)


# ---------------------------------------------------------------------------
# TODO (YOURS TO WRITE, not boilerplate):
#   - Start-up sequence: who is interrogator / human / AI, randomizing roles
#   - Main game loop: turns, question rounds, guessing, win condition
#   - Instructions shown to each player
#   - The AI's system prompt and any conversation-history handling
#   - Deciding when/how the AI responds (using ask_model + send_with_typing_delay)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    run_bot()
