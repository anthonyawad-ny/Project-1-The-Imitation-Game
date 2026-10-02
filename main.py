from discord.ext import commands
from boilerplate import bot, run_bot, reset_nicknames
import game
from game import active_rounds

@bot.event
async def on_ready():
    print(f"{bot.user} is online")

@bot.event
async def on_command_error(ctx, error):
    if not isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Error: {error}")

@bot.command(name="reset")
async def reset_cmd(ctx):
    nicknamed = [m for m in ctx.guild.members if m.nick]
    await reset_nicknames(nicknamed)
    active_rounds.pop(ctx.channel.id, None)
    await ctx.send("Game reset.")
        
if __name__ == "__main__":
    run_bot()
