import os
import pandas as pd
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Get token from environment
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8665911975:AAHtyG2P-ECob4hQCIdKN0as9054lgrMm0I")

# Create CSV if not exists
if not os.path.exists("data.csv"):
    df = pd.DataFrame(columns=["user_id", "username", "group", "response", "time"])
    df.to_csv("data.csv", index=False)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("STEM", callback_data="STEM")],
        [InlineKeyboardButton("NON-STEM", callback_data="NON-STEM")]
    ]
    await update.message.reply_text(
        "🎓 UCC CYBER SECURITY STUDY\n\nSelect your academic group:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["group"] = query.data
    
    keyboard = [
        [InlineKeyboardButton("Click Link", callback_data="clicked")],
        [InlineKeyboardButton("Ignore", callback_data="ignored")]
    ]
    await query.message.reply_text(
        "⚠️ SECURITY ALERT\n\nYour account requires verification.\nhttp://fake-link.com\n\nWhat do you do?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    df = pd.read_csv("data.csv")
    df.loc[len(df)] = [
        query.from_user.id,
        query.from_user.username,
        context.user_data.get("group", "Unknown"),
        query.data,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ]
    df.to_csv("data.csv", index=False)
    
    await query.edit_message_text("✅ Response recorded. Thank you!")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button, pattern="^(STEM|NON-STEM)$"))
    app.add_handler(CallbackQueryHandler(response, pattern="^(clicked|ignored)$"))
    
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
