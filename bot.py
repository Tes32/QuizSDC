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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_question(update.message.chat_id, context)

async def send_question(chat_id, context):
    q = random.choice(questions)
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

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id
    scelta = int(query.data)
    q = current_question[chat_id]

    if scelta == q["corretta"]:
        risposta = "✅ Corretto!"
    else:
        risposta = f"❌ Sbagliato!\nRisposta corretta: {q['opzioni'][q['corretta']]}\n\n{q['soluzione']}"

    await query.edit_message_text(query.message.text + "\n\n" + risposta)

    await send_question(chat_id, context)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(answer))

app.run_polling()
