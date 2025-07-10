from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.helpers import escape_markdown
import json
import os

VOTES_FILE = 'votes.json'
OPTIONS_FILE = 'options.json'

def save_options(options):
    with open(OPTIONS_FILE, 'w') as f:
        json.dump(options, f)

def load_options():
    if os.path.exists(OPTIONS_FILE):
        with open(OPTIONS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_vote(user_id, user_name, vote):
    try:
        with open(VOTES_FILE, 'r') as f:
            data = json.load(f)
    except:
        data = {}

    if str(user_id) not in data:
        data[str(user_id)] = {
            "name": user_name,
            "votes": []
        }

    if vote in data[str(user_id)]["votes"]:
        data[str(user_id)]["votes"].remove(vote)
    else:
        data[str(user_id)]["votes"].append(vote)

    with open(VOTES_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_results():
    try:
        with open(VOTES_FILE, 'r') as f:
            data = json.load(f)
    except:
        return "هیچ رأیی ثبت نشده."

    options = load_options()
    results = {opt: 0 for opt in options}
    for user in data.values():
        for vote in user["votes"]:
            if vote in results:
                results[vote] += 1

    text = "📊 *نتایج رأی‌گیری:*\\n"
    for opt in options:
        text += f"{opt}: {results[opt]} رأی\\n"

    text += "\\n🧑 *رأی‌دهندگان:*\\n"
    for user in data.values():
        name = escape_markdown(user['name'])
        votes = ", ".join(user["votes"])
        text += f"- {name}: {votes}\\n"

    return text

async def start_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("❌ لطفاً حداقل ۲ گزینه بده: /poll گزینه۱ گزینه۲ گزینه۳ ...")
        return

    options = args
    save_options(options)

    keyboard = [[InlineKeyboardButton(opt, callback_data=opt)] for opt in options]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📋 رأی‌گیری جدید:\nروی گزینه‌ها کلیک کن:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_name = query.from_user.full_name
    vote = query.data

    save_vote(user_id, user_name, vote)
    await query.edit_message_text(text=f"✅ رأی شما به {vote} ثبت یا حذف شد.\nدوباره /poll بزن برای رأی‌گیری جدید.")

async def show_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = get_results()
    await update.message.reply_markdown_v2(text)

if __name__ == '__main__':
    TOKEN = "7990396416:AAFUlEyUE9keuv4odUOc0AscvMWliAiFgtI"

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('poll', start_poll))
    app.add_handler(CommandHandler('results', show_results))
    app.add_handler(CallbackQueryHandler(button))

    print("✅ ربات با امکان تعیین گزینه‌ها اجرا شد.")
    app.run_polling()
