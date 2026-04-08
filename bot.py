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

def keyboard(q):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("0 • Нет", callback_data=f"{q}_0"),
            InlineKeyboardButton("1 • Иногда", callback_data=f"{q}_1"),
        ],
        [
            InlineKeyboardButton("2 • Часто", callback_data=f"{q}_2"),
            InlineKeyboardButton("3 • Почти всегда", callback_data=f"{q}_3"),
        ]
    ])

def progress_bar(current, total):
    filled = int((current / total) * 10)
    return "🟦" * filled + "⬜" * (10 - filled)

def level(score):
    if score <= 5: return "низкий"
    elif score <= 10: return "средний"
    else: return "высокий"

# 🧠 ПРОФИЛЬ
def get_profile(stress, anxiety, depression):
    if depression == "высокий":
        return "Истощённое состояние"
    if stress == "высокий" and anxiety == "высокий":
        return "Перегруженное и тревожное состояние"
    if stress == "высокий":
        return "Перегруженное состояние"
    if anxiety == "высокий":
        return "Тревожное состояние"
    return "Сбалансированное состояние"

# 💡 СОВЕТЫ
def get_advice(profile):
    if "Истощённое" in profile:
        return (
            "— снизить нагрузку\n"
            "— больше сна и восстановления\n"
            "— не изолироваться от людей"
        )
    if "Перегруженное и тревожное" in profile:
        return (
            "— сократить поток информации\n"
            "— дать себе паузы в течение дня\n"
            "— снизить требования к себе"
        )
    if "Перегруженное" in profile:
        return (
            "— уменьшить количество задач\n"
            "— добавить отдых\n"
            "— не перегружать себя"
        )
    if "Тревожное" in profile:
        return (
            "— меньше перегрузки новостями\n"
            "— больше спокойных активностей\n"
            "— замедлить ритм"
        )
    return "— продолжать в том же темпе\n— следить за балансом"

def build_summary(user):
    strong = [symptoms_map[q] for q, val in user["answers"] if val >= 2]

    text = "Ты прошёл тест. Вот что видно:\n\n"

    if strong:
        text += "Чаще всего отмечалось:\n"
        text += "— " + "\n— ".join(strong[:4]) + "\n\n"

    text += "Похоже, это состояние формировалось постепенно.\n\n"
    text += "Хочешь посмотреть разбор?"

    return text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("Начать тест", callback_data="start_test")
    ]])

    await update.message.reply_text(
        "🧠 Тест состояния\n\nЖми 👇",
        reply_markup=kb
    )

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "start_test":
        users[user_id] = {"q": 0, "stress": 0, "anxiety": 0, "depression": 0, "answers": []}

        bar = progress_bar(1, len(questions))

        await query.edit_message_text(
            f"{bar}\nВопрос 1/{len(questions)}\n\n{questions[0][0]}",
            reply_markup=keyboard(0)
        )
        return

    if query.data == "show_result":
        u = users[user_id]

        stress = level(u["stress"])
        anxiety = level(u["anxiety"])
        depression = level(u["depression"])

        profile = get_profile(stress, anxiety, depression)
        advice = get_advice(profile)

        text = (
            f"📊 Результат\n\n"
            f"Профиль: {profile}\n\n"
            f"Стресс: {stress}\n"
            f"Тревожность: {anxiety}\n"
            f"Состояние: {depression}\n\n"
            f"💡 Что можно сделать:\n{advice}"
        )

        await query.edit_message_text(text)
        return

    q, val = map(int, query.data.split("_"))

    users[user_id]["answers"].append((q, val))
    users[user_id][questions[q][1]] += val
    users[user_id]["q"] += 1

    labels = ["Нет", "Иногда", "Часто", "Почти всегда"]

    await query.edit_message_text(
        query.message.text + f"\n\nВаш ответ: {labels[val]}"
    )

    if users[user_id]["q"] < len(questions):
        next_q = users[user_id]["q"]
        bar = progress_bar(next_q + 1, len(questions))

        await query.message.reply_text(
            f"{bar}\nВопрос {next_q+1}/{len(questions)}\n\n{questions[next_q][0]}",
            reply_markup=keyboard(next_q)
        )
    else:
        summary = build_summary(users[user_id])

        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("Посмотреть разбор", callback_data="show_result")
        ]])

        await query.message.reply_text(summary, reply_markup=kb)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(answer))

app.run_polling()
