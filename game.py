import discord

from boilerplate import ( bot, ask_model, send_with_typing_delay, set_anonymous_nicknames, reset_nicknames, run_bot)

from prompts import build_messages
import SimpleChat

active_rounds = {}


@bot.command(name="StartGame")
async def start_game(ctx, interrogator: discord.Member, person: discord.Member):
    if ctx.channel.id in active_rounds:
        await ctx.send("game is already in progress in this channel.")
        return

    labels = await set_anonymous_nicknames([person, ctx.guild.me])
    person_label = labels[person.id]

    roundState = SimpleChat.new_round(str(interrogator.id), str(person.id), person_label)
    active_rounds[ctx.channel.id] = roundState

    await ctx.send(
        f"Round started! {interrogator.mention} is the interrogator.\n"
        f"Ask with `!ask <question>`. Up to {SimpleChat.MAXQUESTIONS} questions, "
        f"then `!guess A` or `!guess B`.\n"
        f"(Note: the bot's messages still show a BOT tag next to its name -- "
        f"Discord always marks bot accounts, there's no way to hide that.)"
    )


@bot.command(name="ask")
async def ask_cmd(ctx, *, question):
    roundState = active_rounds.get(ctx.channel.id)
    if not roundState:
        await ctx.send("No active game in this channel. Start one with '!Startgame'.")
        return

    ok, error = SimpleChat.can_ask(roundState, str(ctx.author.id))
    if not ok:
        await ctx.send(error)
        return

    SimpleChat.recordQuestion(roundState, question)

    messages = build_messages(roundState["history"])
    ai_text = await ask_model(messages)
    SimpleChat.recordAnswer(roundState, roundState["ai_label"], ai_text)
    await send_with_typing_delay(ctx.channel, f"({roundState['ai_label']}) {ai_text}")

    await ctx.send(f"Player {roundState['person_label']}, your turn to answer!")


@bot.event
async def on_message(message):
    roundState = active_rounds.get(message.channel.id)
    if roundState and not message.author.bot and str(message.author.id) == roundState["person"]:
        SimpleChat.recordAnswer(roundState, roundState["person_label"], message.content)
    await bot.process_commands(message)


@bot.command(name="guess")
async def guess_cmd(ctx, letter: str):
    roundState = active_rounds.get(ctx.channel.id)
    if not roundState:
        await ctx.send("No active round running.")
        return
    if str(ctx.author.id) != roundState["interrogator"]:
        await ctx.send("Only the interrogator can take a guess.")
        return

    letter = letter.strip().upper()
    ai_was = SimpleChat.reveal(roundState)
    correct = (letter == ai_was)
    await ctx.send(
        f"The Ai was really **{ai_was}**. " + ("you found them!" if correct else "You were wrong!")
    )
    person_member = ctx.guild.get_member(int(roundState["person"]))
    members_to_reset = [ctx.guild.me] + ([person_member] if person_member else [])
    await reset_nicknames(members_to_reset)
    del active_rounds[ctx.channel.id]


if __name__ == "__main__":
    run_bot()