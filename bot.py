import os
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
    6: "потеря интереса",
    7: "ощущение пустоты",
    8: "сложно начать делать дела",
    9: "раздражительность",
    10: "проблемы с концентрацией",
    11: "проблемы со сном",
    12: "избегание общения",
    13: "сложности с решениями",
    14: "ощущение, что не справляешься",
    15: "чувство вины",
    16: "физическое напряжение",
    17: "мысли всё остановить",
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

def level(score):
    if score <= 5: return "низкий"
    elif score <= 10: return "средний"
    else: return "высокий"

# 🧠 Профиль
def get_profile(stress, anxiety, depression):
    if depression == "высокий":
        return "эмоциональное истощение"
    if stress == "высокий" and anxiety == "высокий":
        return "сильная перегрузка с тревожностью"
    if stress == "высокий":
        return "перегрузка"
    if anxiety == "высокий":
        return "повышенная тревожность"
    return "относительно стабильное состояние"

# 🧠 Развёрнутый анализ
def build_analysis(user, profile):
    strong = [symptoms_map[q] for q, val in user["answers"] if val >= 2]

    text = ""

    if strong:
        text += "По твоим ответам видно, что сейчас у тебя проявляются такие состояния:\n"
        text += "— " + "\n— ".join(strong[:5]) + "\n\n"

    if "истощение" in profile:
        text += (
            "Это похоже на состояние эмоционального истощения. "
            "Обычно оно возникает, когда человек долго живёт в режиме напряжения "
            "и не успевает восстанавливаться. Может ощущаться пустота, отсутствие энергии "
            "и сложности даже с простыми задачами.\n\n"
        )

    elif "перегрузка" in profile:
        text += (
            "Сейчас состояние похоже на перегрузку. Когда задач и напряжения становится слишком много, "
            "организм начинает сигналить через усталость, раздражительность и трудности с концентрацией.\n\n"
        )

    elif "тревожность" in profile:
        text += (
            "Есть признаки повышенной тревожности. Это может ощущаться как постоянное внутреннее напряжение, "
            "невозможность расслабиться и прокручивание мыслей.\n\n"
        )

    else:
        text += (
            "В целом состояние выглядит стабильным. Нет выраженных признаков сильной перегрузки или истощения.\n\n"
        )

    text += "Это не диагноз, а сигнал от твоей психики о текущем состоянии.\n"

    return text

# 💡 советы
def get_advice(profile):
    if "истощение" in profile:
        return (
            "— снизить нагрузку\n"
            "— больше отдыха и сна\n"
            "— не оставаться в изоляции"
        )
    if "перегрузка" in profile:
        return (
            "— сократить задачи\n"
            "— делать паузы\n"
            "— снизить давление на себя"
        )
    if "тревожность" in profile:
        return (
            "— уменьшить поток информации\n"
            "— добавить спокойные активности\n"
            "— замедлить ритм"
        )
    return "— продолжать в том же духе"

def build_summary(user):
    strong = [symptoms_map[q] for q, val in user["answers"] if val >= 2]

    text = "Ты прошёл тест.\n\n"

    if strong:
        text += "Чаще всего ты отмечал:\n"
        text += "— " + "\n— ".join(strong[:4]) + "\n\n"

    text += "Похоже, это состояние формировалось постепенно.\n\n"
    text += "Хочешь посмотреть разбор?"

    return text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🧠 Привет!\n\n"
        "Это короткий тест, который поможет понять твоё состояние:\n"
        "— стресс\n"
        "— тревожность\n"
        "— признаки выгорания\n\n"
        "⏱ ~2 минуты\n\n"
        "📊 Как отвечать:\n"
        "0 — нет\n"
        "1 — иногда\n"
        "2 — часто\n"
        "3 — почти всегда\n\n"
        "Нажми кнопку ниже 👇"
    )

    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("Начать тест", callback_data="start_test")
    ]])

    await update.message.reply_text(text, reply_markup=kb)

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "start_test":
        users[user_id] = {"q": 0, "stress": 0, "anxiety": 0, "depression": 0, "answers": []}

        await query.edit_message_text(
            f"Вопрос 1/{len(questions)}\n\n{questions[0][0]}",
            reply_markup=keyboard(0)
        )
        return

    if query.data == "show_result":
        u = users[user_id]

        stress = level(u["stress"])
        anxiety = level(u["anxiety"])
        depression = level(u["depression"])

        profile = get_profile(stress, anxiety, depression)
        analysis = build_analysis(u, profile)
        advice = get_advice(profile)

        text = (
            f"📊 Результат\n\n"
            f"Состояние: {profile}\n\n"
            f"{analysis}\n\n"
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

        await query.message.reply_text(
            f"Вопрос {next_q+1}/{len(questions)}\n\n{questions[next_q][0]}",
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
