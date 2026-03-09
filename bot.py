import pandas as pd
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8755489417:AAG8zB17ifshK_ZHNnWeNFzcPaxC55vD20Q"

df = pd.read_excel("domande.xlsx")

questions = []

for _, row in df.iterrows():
    questions.append({
        "domanda": row["Domanda"],
        "opzioni": [
            row["Opzione A"],
            row["Opzione B"],
            row["Opzione C"],
            row["Opzione D"]
        ],
        "corretta": int(row["Corretta"]) - 1,
        "soluzione": row["Soluzione"]
    })

current_question = {}
asked_questions = {}
score = {}
total_answered = {}
wrong_answers = {}
exam_mode = {}
exam_remaining = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    
    asked_questions[chat_id] = []
    score[chat_id] = 0
    total_answered[chat_id] = 0
    wrong_answers[chat_id] = 0
    exam_mode[chat_id] = False

    await send_question(chat_id, context)

async def send_question(chat_id, context):

    if chat_id not in asked_questions:
        asked_questions[chat_id] = []

    remaining = [q for q in questions if q not in asked_questions[chat_id]]

    if not remaining:
        percent = round((score[chat_id] / total_answered[chat_id]) * 100, 1)

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"📊 Quiz finito!\n\n"
                 f"Domande totali: {total_answered[chat_id]}\n"
                 f"Corrette: {score[chat_id]}\n"
                 f"Sbagliate: {wrong_answers[chat_id]}\n"
                 f"Punteggio: {percent}%"
        )

        return
    q = random.choice(remaining)

    asked_questions[chat_id].append(q)
    current_question[chat_id] = q

    keyboard = []
    for i, op in enumerate(q["opzioni"]):
        keyboard.append([InlineKeyboardButton(op, callback_data=str(i))])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=chat_id,
        text=q["domanda"],
        reply_markup=reply_markup
    )

async def esame(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.message.chat_id

    exam_mode[chat_id] = True
    exam_remaining[chat_id] = 4

    score[chat_id] = 0
    total_answered[chat_id] = 0
    wrong_answers[chat_id] = 0
    asked_questions[chat_id] = []

    await update.message.reply_text("📝 Modalità esame iniziata (30 domande)")

    await send_question(chat_id, context)

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id
    scelta = int(query.data)
    q = current_question[chat_id]

    total_answered[chat_id] += 1

    if scelta == q["corretta"]:
        score[chat_id] += 1
        risposta = f"✅ Corretto!\nPunteggio: {score[chat_id]}"
    else:
        wrong_answers[chat_id] += 1
        risposta = f"❌ Sbagliato!\nRisposta corretta: {q['opzioni'][q['corretta']]}\n\n{q['soluzione']}"

    await query.edit_message_text(query.message.text + "\n\n" + risposta)

    if exam_mode.get(chat_id):
        exam_remaining[chat_id] -= 1

        if exam_remaining[chat_id] <= 0:
            percent = round((score[chat_id] / total_answered[chat_id]) * 100, 1)

            await context.bot.send_message(
                chat_id=chat_id,
                text=f"🎓 Esame terminato!\n\n"
                     f"Domande: {total_answered[chat_id]}\n"
                     f"Corrette: {score[chat_id]}\n"
                     f"Sbagliate: {wrong_answers[chat_id]}\n"
                     f"Punteggio finale: {percent}%"
            )

            exam_mode[chat_id] = False
            return

    await send_question(chat_id, context)

async def exit_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id

    # Reset della sessione
    asked_questions[chat_id] = []
    score[chat_id] = 0
    total_answered[chat_id] = 0
    wrong_answers[chat_id] = 0
    exam_mode[chat_id] = False
    exam_remaining[chat_id] = 0
    current_question[chat_id] = None

    await update.message.reply_text("❌ Sessione terminata. Puoi fare /start per ricominciare.")
    

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("exit", exit_session))
app.add_handler(CommandHandler("esame", esame))
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(answer))

app.run_polling()
