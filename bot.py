import os
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("TOKEN")

questions = [
("Мне сложно расслабиться", "stress"),
("Я чувствую усталость даже после отдыха", "stress"),
("У меня ощущение, что всё навалилось", "stress"),

("Я чувствую тревогу без причины", "anxiety"),
("У меня бывают навязчивые мысли", "anxiety"),
("Я ощущаю внутреннее напряжение", "anxiety"),

("Мне стало меньше интересно то, что раньше нравилось", "depression"),
("Я чувствую себя пустым", "depression"),
("Мне сложно начать делать дела", "depression"),

("Я раздражаюсь из-за мелочей", "stress"),
("Мне трудно сосредоточиться", "stress"),
("Я стал хуже спать", "stress"),

("Я избегаю общения", "depression"),
("Мне трудно принимать решения", "depression"),
("Я чувствую, что не справляюсь", "depression"),

("У меня есть чувство вины", "depression"),
("У меня есть физические симптомы стресса", "stress"),
("Я думаю о том, чтобы всё остановилось", "depression"),
]

symptoms_map = {
    0: "трудно расслабиться",
    1: "усталость даже после отдыха",
    2: "ощущение перегруженности",
    3: "тревога без причины",
    4: "навязчивые мысли",
    5: "внутреннее напряжение",
    6: "потеря интереса к привычным вещам",
    7: "ощущение пустоты",
    8: "сложно начать что-то делать",
    9: "раздражительность",
    10: "проблемы с концентрацией",
    11: "проблемы со сном",
    12: "избегание общения",
    13: "сложности с принятием решений",
    14: "ощущение, что не справляешься",
    15: "чувство вины",
    16: "физическое напряжение",
    17: "мысли о том, чтобы всё остановилось",
}

users = {}
history = {}

def keyboard(q):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("0", callback_data=f"{q}_0"),
        InlineKeyboardButton("1", callback_data=f"{q}_1"),
        InlineKeyboardButton("2", callback_data=f"{q}_2"),
        InlineKeyboardButton("3", callback_data=f"{q}_3"),
    ]])

def level(score):
    if score <= 5: return "низкий"
    elif score <= 10: return "средний"
    else: return "высокий"

def build_analysis(user):
    answers = user["answers"]

    strong = []
    medium = []

    for q, val in answers:
        if val >= 2:
            strong.append(symptoms_map[q])
        elif val == 1:
            medium.append(symptoms_map[q])

    text = ""

    if strong:
        text += "Сейчас у тебя заметны такие состояния:\n"
        text += ", ".join(strong[:5]) + ".\n\n"

    if medium:
        text += "Также частично проявляется:\n"
        text += ", ".join(medium[:3]) + ".\n\n"

    text += "Это выглядит как накопленная нагрузка и эмоциональное напряжение.\n\n"
    text += "Важно понимать: это не слабость, а сигнал, что ресурсы заканчиваются.\n"

    return text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🧠 Привет!\n\n"
        "Это тест для оценки состояния:\n"
        "— стресс\n"
        "— тревожность\n"
        "— признаки выгорания\n\n"
        "⏱ ~2 минуты\n\n"
        "📊 Как отвечать:\n"
        "0 — нет\n"
        "1 — иногда\n"
        "2 — часто\n"
        "3 — почти всегда\n\n"
        "Команда /history — посмотреть прошлые результаты\n\n"
        "Жми 👇"
    )

    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("Начать тест", callback_data="start_test")
    ]])

    await update.message.reply_text(text, reply_markup=kb)

async def show_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in history or not history[user_id]:
        await update.message.reply_text("История пока пуста 🙂")
        return

    text = "📊 Твоя история:\n\n"

    for item in history[user_id][-5:]:
        text += f"{item['date']}\n"
        text += f"Стресс: {item['stress']}, Тревога: {item['anxiety']}, Состояние: {item['depression']}\n\n"

    await update.message.reply_text(text)

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "start_test":
        users[user_id] = {
            "q": 0,
            "stress": 0,
            "anxiety": 0,
            "depression": 0,
            "answers": []
        }

        await query.edit_message_text(
            f"Вопрос 1/{len(questions)}\n\n{questions[0][0]}\n\n"
            "(0 — нет, 1 — иногда, 2 — часто, 3 — почти всегда)",
            reply_markup=keyboard(0)
        )
        return

    q, val = map(int, query.data.split("_"))

    users[user_id]["answers"].append((q, val))
    category = questions[q][1]

    users[user_id][category] += val
    users[user_id]["q"] += 1

    if users[user_id]["q"] < len(questions):
        next_q = users[user_id]["q"]
        await query.edit_message_text(
            f"Вопрос {next_q+1}/{len(questions)}\n\n{questions[next_q][0]}\n\n"
            "(0 — нет, 1 — иногда, 2 — часто, 3 — почти всегда)",
            reply_markup=keyboard(next_q)
        )
    else:
        u = users[user_id]

        stress_lvl = level(u["stress"])
        anxiety_lvl = level(u["anxiety"])
        depression_lvl = level(u["depression"])

        comment = build_analysis(u)

        entry = {
            "date": datetime.now().strftime("%d.%m %H:%M"),
            "stress": stress_lvl,
            "anxiety": anxiety_lvl,
            "depression": depression_lvl
        }

        history.setdefault(user_id, []).append(entry)

        text = (
            f"📊 Результат:\n\n"
            f"Стресс: {stress_lvl}\n"
            f"Тревожность: {anxiety_lvl}\n"
            f"Состояние: {depression_lvl}\n\n"
            f"🧠 Разбор:\n\n{comment}"
        )

        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("Пройти заново", callback_data="start_test")
        ]])

        await query.edit_message_text(text, reply_markup=kb)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("history", show_history))
app.add_handler(CallbackQueryHandler(answer))

app.run_polling()
