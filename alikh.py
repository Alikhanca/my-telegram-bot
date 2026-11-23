import json
import os

from dotenv import load_dotenv
from telegram import Update

load_dotenv()
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
DB_FILE = "user.json"

# 5 параметров (для челленджа)
FIELDS = {
    "name": "Имя",
    "color": "Любимый цвет",
    "car": "Любимая машина",
    "food": "Любимая еда",
    "hobby": "Хобби",
}


def load_data() -> dict:
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_data(data: dict) -> None:
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keys = "\n".join(f"/set {k} <значение> — {v}" for k, v in FIELDS.items())
    await update.message.reply_text(
        "Привет! Я запоминаю твои данные 🧠\n\n"
        f"Доступные параметры:\n{keys}\n\n"
        "Пример: /set color синий\n"
        "Посмотреть всё сохранённое: /profile"
    )


async def set_param(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text(
            "Формат: /set <параметр> <значение>\n"
            f"Параметры: {', '.join(FIELDS)}"
        )
        return

    key = context.args[0].lower()
    value = " ".join(context.args[1:])

    if key not in FIELDS:
        await update.message.reply_text(
            f"Не знаю параметр «{key}». Доступные: {', '.join(FIELDS)}"
        )
        return

    data = load_data()
    user_id = str(update.effective_user.id)
    data.setdefault(user_id, {})[key] = value
    save_data(data)

    await update.message.reply_text(f"✅ Запомнил: {FIELDS[key]} — {value}")


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    user = data.get(str(update.effective_user.id), {})

    if not user:
        await update.message.reply_text(
            "Я пока ничего о тебе не знаю. Попробуй: /set name Алия"
        )
        return

    lines = [f"{FIELDS[k]}: {user[k]}" for k in FIELDS if k in user]
    await update.message.reply_text("👤 Твой профиль:\n" + "\n".join(lines))


def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("set", set_param))
    app.add_handler(CommandHandler("profile", profile))
    print("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()