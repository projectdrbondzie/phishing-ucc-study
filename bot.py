import os
import sys
import traceback
import pandas as pd
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Write startup to a file
with open("/tmp/bot_startup.log", "w") as f:
    f.write("Bot starting...\n")

try:
    with open("/tmp/bot_startup.log", "a") as f:
        f.write("Import successful\n")
    
    # ============================================
    # GET TOKEN FROM ENVIRONMENT VARIABLE
    # ============================================
    TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8665911975:AAHtyG2P-ECob4hQCIdKN0as9054lgrMm0I")
    
    with open("/tmp/bot_startup.log", "a") as f:
        f.write(f"Token loaded, length: {len(TOKEN)}\n")
        f.write(f"Token exists: {bool(TOKEN)}\n")
    
    if not TOKEN:
        with open("/tmp/bot_startup.log", "a") as f:
            f.write("ERROR: No token found!\n")
        print("ERROR: TELEGRAM_BOT_TOKEN environment variable is not set!")
        sys.exit(1)
    
    # ============================================
    # CREATE CSV FILE IF IT DOESN'T EXIST
    # ============================================
    CSV_COLUMNS = [
        "user_id", "username", "group", "submission_time",
        "age", "gender", "year_of_study", "programme",
        "email_usage", "mobile_money_usage", "social_media_usage",
        "knows_phishing", "phishing_definition", "identifies_indicators",
        "received_suspicious", "prior_compromise", "prior_training",
        "scenario_1", "scenario_2", "scenario_3", "scenario_4", "scenario_5",
        "uses_2fa", "shares_password", "report_suspicious", "score"
    ]
    
    if not os.path.exists("data.csv"):
        df = pd.DataFrame(columns=CSV_COLUMNS)
        df.to_csv("data.csv", index=False)
        with open("/tmp/bot_startup.log", "a") as f:
            f.write("Created data.csv\n")
    
    user_sessions = {}
    
    # ============================================
    # BOT HANDLERS (simplified for testing)
    # ============================================
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("📊 STEM", callback_data="STEM")],
            [InlineKeyboardButton("📚 NON-STEM", callback_data="NON-STEM")]
        ]
        await update.message.reply_text(
            "🎓 UCC CYBER SECURITY STUDY\n\nSelect your group:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
        df = pd.read_csv("data.csv")
        await update.message.reply_text(f"📊 Total responses: {len(df)}")
    
    async def group_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        keyboard = [[InlineKeyboardButton("18-21", callback_data="age_18_21")]]
        await query.edit_message_text("Age?", reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def age_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        await query.edit_message_text("✅ Thank you! Response recorded.")
        
        # Save to CSV
        df = pd.read_csv("data.csv")
        df.loc[len(df)] = [query.from_user.id, query.from_user.username, "TEST", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", 0]
        df.to_csv("data.csv", index=False)
    
    # ============================================
    # MAIN FUNCTION
    # ============================================
    def main():
        with open("/tmp/bot_startup.log", "a") as f:
            f.write("Building application...\n")
        
        app = Application.builder().token(TOKEN).build()
        
        with open("/tmp/bot_startup.log", "a") as f:
            f.write("Adding handlers...\n")
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("stats", stats))
        app.add_handler(CallbackQueryHandler(group_handler, pattern="^(STEM|NON-STEM)$"))
        app.add_handler(CallbackQueryHandler(age_handler, pattern="^age_"))
        
        with open("/tmp/bot_startup.log", "a") as f:
            f.write("Starting polling...\n")
        
        print("🤖 Bot is running...")
        app.run_polling()
    
    if __name__ == "__main__":
        main()

except Exception as e:
    with open("/tmp/bot_error.log", "w") as f:
        f.write("=" * 50 + "\n")
        f.write("FATAL ERROR:\n")
        f.write(traceback.format_exc())
        f.write("=" * 50 + "\n")
    print("FATAL ERROR. Check /tmp/bot_error.log")
    sys.exit(1)
