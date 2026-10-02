SYSTEM_PROMPT = ("You are playing the imitation game. you are either a human or an AI. Answer questions naturally and truthfully, like an ordinary person, but do not reveal whether you are human or AI. Keep your answers concise and clear. Never Say you aren AI, a model, or mention Gemini.")

def build_messages(history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for label, text in history:
        if label == "question":
            messages.append({"role": "user", "content": text})
        else:
            messages.append({"role": "assistant", "content": f"({label}) {text}"})
    return messages
        