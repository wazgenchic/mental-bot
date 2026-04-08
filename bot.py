import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("TOKEN")

questions = [
"Мне сложно расслабиться даже в спокойной обстановке",
"Я чувствую усталость даже после отдыха",
"У меня есть ощущение, что «всё навалилось»",
"Мне трудно сосредоточиться",
"Я стал хуже спать",
"Я чувствую тревогу без причины",
"Мне стало меньше интересно то, что раньше нравилось",
"Я раздражаюсь из-за мелочей",
"У меня есть внутреннее напряжение",
"Мне трудно принимать решения",
"Я чувствую себя пустым",
"У меня бывают навязчивые мысли",
"Я избегаю общения",
"Я чувствую, что не справляюсь",
"У меня есть чувство вины",
"У меня есть физические симптомы стресса",
"Мне сложно начать делать дела",
"Я думаю о том, чтобы всё остановилось"
]

users = {}

def keyboard(q):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("0", callback_data=f"{q}_0"),
        InlineKeyboardButton("1", callback_data=f"{q}_1"),
        InlineKeyboardButton("2", callback_data=f"{q}_2"),
        InlineKeyboardButton("3", callback_data=f"{q}_3"),
    ]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users[update.effective_user.id] = {"q": 0, "score": 0}
    await update.message.reply_text(
        "🧠 Начнём тест\n\n0 — нет | 1 — иногда | 2 — часто | 3 — почти всегда\n\n" + questions[0],
        reply_markup=keyboard(0)
    )

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    q, val = map(int, query.data.split("_"))

    users[user_id]["score"] += val
    users[user_id]["q"] += 1

    if users[user_id]["q"] < len(questions):
        next_q = users[user_id]["q"]
        await query.edit_message_text(
            f"Вопрос {next_q+1}/{len(questions)}\n\n{questions[next_q]}",
            reply_markup=keyboard(next_q)
        )
    else:
        score = users[user_id]["score"]

        if score <= 12:
            result = "🟢 Норма"
        elif score <= 24:
            result = "🟡 Повышенный стресс"
        elif score <= 38:
            result = "🟠 Выгорание"
        else:
            result = "🔴 Тяжёлое состояние"

        await query.edit_message_text(f"Твой результат: {score}\n\n{result}")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(answer))

app.run_polling()
