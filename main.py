from discord.ext import commands
from boilerplate import bot, run_bot
import game

@bot.event
async def on_ready():
    print(f"{bot.user} is online")

@bot.event
async def on_command_error(ctx, error):
    if not isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Error: {error}")
        
if __name__ == "__main__":
    run_bot()