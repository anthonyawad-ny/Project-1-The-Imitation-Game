import asyncio
from boilerplate import ask_model, bot, run_bot

@bot.command()
async def ping(ctx):
    await ctx.send("pong")

@bot.command()
async def ai(ctx, *, text):
    reply = await ask_model([{"role": "user", "content": text}])
    await ctx.send(reply)

run_bot()