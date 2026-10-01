MAXQUESTIONS = 5

def new_round(interrogator_id, person_id, person_label):

    ai_label = "B" if person_label == "A" else "A"
    return {
        "interrogator": interrogator_id,
        "person":person_id,
        "person_label": person_label,
        "ai_label": ai_label,
        "questions_asked": 0,
        "history": [],

    }

def can_ask(roundState, sender_id):
    if sender_id != roundState["interrogator"]:
        return False, "Sorry you are not the interrogator."
    if roundState["questions_asked"] >= MAXQUESTIONS:
        return False, "Sorry too many questions, just guess already!"
    return True,None

def recordQuestion(roundState, QuestionText):
    roundState["questions_asked"] +=1
    roundState["history"].append(("question", QuestionText))

def recordAnswer(roundState, label, AnswerText):
    roundState["history"].append((label, AnswerText))

def getRoundHistory(roundState):
    return roundState["history"]

def reveal(roundState):
    return roundState["ai_label"]
