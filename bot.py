import os
import sys
import traceback
import pandas as pd
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

print("Starting bot initialization...")

try:
    # ============================================
    # GET TOKEN FROM ENVIRONMENT VARIABLE
    # ============================================
    TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8665911975:AAHtyG2P-ECob4hQCIdKN0as9054lgrMm0I")
    
    if not TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN environment variable is not set!")
        print("Please add it in Render dashboard: Environment tab")
        sys.exit(1)
    
    print(f"Token loaded (length: {len(TOKEN)} characters)")
    
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
        print("✅ data.csv created")
    else:
        print("✅ data.csv already exists")
    
    user_sessions = {}
    
    # ============================================
    # START COMMAND
    # ============================================
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user_sessions[user_id] = {"step": "group", "answers": {}}
        
        keyboard = [
            [InlineKeyboardButton("📊 STEM", callback_data="STEM")],
            [InlineKeyboardButton("📚 NON-STEM", callback_data="NON-STEM")]
        ]
        
        await update.message.reply_text(
            "🎓 WELCOME TO THE UCC CYBER SECURITY STUDY 🎓\n\n"
            "This research compares phishing awareness between STEM and NON-STEM students.\n\n"
            "✅ All responses are anonymous\n"
            "✅ Takes 3-4 minutes\n\n"
            "Please select your academic group:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    # ============================================
    # STATS COMMAND
    # ============================================
    async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
        df = pd.read_csv("data.csv")
        
        if len(df) == 0:
            await update.message.reply_text("📊 No responses collected yet.")
            return
        
        stem = len(df[df['group'] == 'STEM'])
        nonstem = len(df[df['group'] == 'NON-STEM'])
        avg_score = df['score'].mean() if 'score' in df.columns else 0
        
        await update.message.reply_text(
            f"📊 STUDY PROGRESS 📊\n\n"
            f"Total responses: {len(df)}\n"
            f"STEM students: {stem}\n"
            f"NON-STEM students: {nonstem}\n"
            f"Average vulnerability score: {avg_score:.1f}/5"
        )
    
    # ============================================
    # GROUP HANDLER
    # ============================================
    async def group_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user_sessions[user_id]["answers"]["group"] = query.data
        user_sessions[user_id]["step"] = "age"
        
        keyboard = [
            [InlineKeyboardButton("18-21", callback_data="18-21")],
            [InlineKeyboardButton("22-25", callback_data="22-25")],
            [InlineKeyboardButton("26-30", callback_data="26-30")],
            [InlineKeyboardButton("31+", callback_data="31+")]
        ]
        
        await query.edit_message_text(
            "📋 QUESTION 1/19\n\nWhat is your age range?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    # ============================================
    # SIMPLIFIED AGE HANDLER (redirect to scenarios)
    # ============================================
    async def age_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user_sessions[user_id]["answers"]["age"] = query.data
        user_sessions[user_id]["step"] = "scenario1"
        
        keyboard = [
            [InlineKeyboardButton("❌ Click link", callback_data="clicked")],
            [InlineKeyboardButton("✅ Check with IT first", callback_data="safe")],
            [InlineKeyboardButton("🗑️ Delete", callback_data="safe")]
        ]
        
        await query.edit_message_text(
            "📧 SCENARIO 1/5\n\n"
            "Email from 'UCC IT Helpdesk': 'Your password expires today. Click here to keep it.'\n\n"
            "What do you do?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    # ============================================
    # SCENARIO HANDLERS
    # ============================================
    async def scenario1_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        user_sessions[user_id]["answers"]["scenario1"] = query.data
        user_sessions[user_id]["step"] = "scenario2"
        
        keyboard = [
            [InlineKeyboardButton("❌ Click link", callback_data="clicked")],
            [InlineKeyboardButton("✅ Ignore", callback_data="safe")]
        ]
        await query.edit_message_text(
            "📱 SCENARIO 2/5\n\nSMS: 'MTN credited GHS 500. Claim now: http://short.link'\n\nWhat do you do?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def scenario2_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        user_sessions[user_id]["answers"]["scenario2"] = query.data
        user_sessions[user_id]["step"] = "scenario3"
        
        keyboard = [
            [InlineKeyboardButton("❌ Submit", callback_data="clicked")],
            [InlineKeyboardButton("✅ Ignore", callback_data="safe")]
        ]
        await query.edit_message_text(
            "💼 SCENARIO 3/5\n\nLinkedIn: 'Urgent job offer. Submit your login details.'\n\nWhat do you do?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def scenario3_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        user_sessions[user_id]["answers"]["scenario3"] = query.data
        user_sessions[user_id]["step"] = "scenario4"
        
        keyboard = [
            [InlineKeyboardButton("❌ Click link", callback_data="clicked")],
            [InlineKeyboardButton("✅ Call bank", callback_data="safe")]
        ]
        await query.edit_message_text(
            "🏦 SCENARIO 4/5\n\nBank email: 'Suspicious activity. Confirm your account.'\n\nWhat do you do?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def scenario4_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        user_sessions[user_id]["answers"]["scenario4"] = query.data
        user_sessions[user_id]["step"] = "scenario5"
        
        keyboard = [
            [InlineKeyboardButton("❌ Click link", callback_data="clicked")],
            [InlineKeyboardButton("✅ Verify with lecturer", callback_data="safe")]
        ]
        await query.edit_message_text(
            "📧 SCENARIO 5/5\n\nEmail from lecturer: 'Click here for materials' (poor grammar)\n\nWhat do you do?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def scenario5_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        answers = user_sessions[user_id]["answers"]
        answers["scenario5"] = query.data
        answers["submission_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        score = sum(1 for i in range(1, 6) if answers.get(f"scenario{i}", "") == "clicked")
        
        row = {
            "user_id": query.from_user.id,
            "username": query.from_user.username,
            "group": answers.get("group", ""),
            "submission_time": answers.get("submission_time", ""),
            "age": answers.get("age", ""), "gender": "", "year_of_study": "", "programme": "",
            "email_usage": "", "mobile_money_usage": "", "social_media_usage": "",
            "knows_phishing": "", "phishing_definition": "", "identifies_indicators": "",
            "received_suspicious": "", "prior_compromise": "", "prior_training": "",
            "scenario_1": answers.get("scenario1", ""),
            "scenario_2": answers.get("scenario2", ""),
            "scenario_3": answers.get("scenario3", ""),
            "scenario_4": answers.get("scenario4", ""),
            "scenario_5": answers.get("scenario5", ""),
            "uses_2fa": "", "shares_password": "", "report_suspicious": "", "score": score,
        }
        
        df = pd.read_csv("data.csv")
        df.loc[len(df)] = row
        df.to_csv("data.csv", index=False)
        
        await query.edit_message_text(
            f"✅ THANK YOU!\n\nYour vulnerability score: {score}/5\n\n"
            f"{'⚠️ Higher score = more susceptible' if score >= 3 else '✅ Good phishing awareness!'}\n\n"
            f"Responses recorded anonymously."
        )
        del user_sessions[user_id]
    
    # ============================================
    # MAIN FUNCTION
    # ============================================
    def main():
        print("Building application...")
        app = Application.builder().token(TOKEN).build()
        
        print("Adding handlers...")
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("stats", stats))
        app.add_handler(CallbackQueryHandler(group_handler, pattern="^(STEM|NON-STEM)$"))
        app.add_handler(CallbackQueryHandler(age_handler, pattern="^(18-21|22-25|26-30|31+)$"))
        app.add_handler(CallbackQueryHandler(scenario1_handler, pattern="^(clicked|safe)$"))
        app.add_handler(CallbackQueryHandler(scenario2_handler, pattern="^(clicked|safe)$"))
        app.add_handler(CallbackQueryHandler(scenario3_handler, pattern="^(clicked|safe)$"))
        app.add_handler(CallbackQueryHandler(scenario4_handler, pattern="^(clicked|safe)$"))
        app.add_handler(CallbackQueryHandler(scenario5_handler, pattern="^(clicked|safe)$"))
        
        print("🤖 UCC Phishing Study Bot is running...")
        print("📊 Data will be saved to data.csv automatically")
        app.run_polling()
    
    if __name__ == "__main__":
        main()

except Exception as e:
    print("=" * 50)
    print("FATAL ERROR:")
    print(traceback.format_exc())
    print("=" * 50)
    sys.exit(1)
