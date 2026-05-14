import os
import pandas as pd
from datetime import datetime
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ============================================
# CONFIGURATION
# ============================================

# PUT YOUR REAL BOT TOKEN HERE
TOKEN = "8995182920:AAGs3WrTmGPpTO7FpDC32-mJgOfVdLLY5mA"

# Get the absolute path to the current directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(CURRENT_DIR, "data.csv")

# Create empty CSV if it doesn't exist
if not os.path.exists(CSV_FILE):
    df = pd.DataFrame(columns=[
        "user_id", "username", "group", "age", "gender", "year_of_study", "programme",
        "email_usage", "mobile_money_usage", "social_media_usage",
        "knows_phishing_term", "phishing_definition", "identifies_indicators",
        "received_suspicious", "prior_compromise", "prior_training",
        "scenario_1_response", "scenario_2_response", "scenario_3_response",
        "scenario_4_response", "scenario_5_response",
        "uses_2fa", "shares_password", "report_suspicious", "submission_time"
    ])
    df.to_csv(CSV_FILE, index=False)
    print(f"Created: {CSV_FILE}")

user_sessions = {}

# ============================================
# BOT HANDLERS
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_sessions[user_id] = {"step": "group", "answers": {}}
    
    keyboard = [[InlineKeyboardButton("STEM", callback_data="STEM")], [InlineKeyboardButton("NON-STEM", callback_data="NON-STEM")]]
    await update.message.reply_text(
        "📚 WELCOME TO THE CYBER SECURITY STUDY\n\nSelect your academic group:",
        reply_markup=InlineKeyboardMarkup(keyboard))

async def group_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_sessions[user_id]["answers"]["group"] = query.data
    user_sessions[user_id]["step"] = "age"
    
    keyboard = [[InlineKeyboardButton("18-21", callback_data="18-21")], [InlineKeyboardButton("22-25", callback_data="22-25")], [InlineKeyboardButton("Above 25", callback_data="above_25")]]
    await query.edit_message_text("QUESTION 1/19: What is your age range?", reply_markup=InlineKeyboardMarkup(keyboard))

async def question_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    step = user_sessions[user_id]["step"]
    user_sessions[user_id]["answers"][step] = query.data
    
    flow = {
        "age": ("gender", "QUESTION 2/19: What is your gender?", [("Male", "male"), ("Female", "female")]),
        "gender": ("year_of_study", "QUESTION 3/19: Year of study?", [("Level 100", "100"), ("Level 200", "200"), ("Level 300", "300"), ("Level 400", "400")]),
        "year_of_study": ("programme", "QUESTION 4/19: Programme type?", [("Sciences", "sciences"), ("Humanities", "humanities"), ("Business", "business"), ("Education", "education")]),
        "programme": ("email_usage", "QUESTION 5/19: Email usage?", [("Daily", "daily"), ("Weekly", "weekly"), ("Rarely", "rarely")]),
        "email_usage": ("mobile_money_usage", "QUESTION 6/19: Mobile money usage?", [("Often", "often"), ("Sometimes", "sometimes"), ("Never", "never")]),
        "mobile_money_usage": ("social_media_usage", "QUESTION 7/19: Social media usage?", [("Daily", "daily"), ("Weekly", "weekly"), ("Rarely", "rarely")]),
        "social_media_usage": ("knows_phishing", "QUESTION 8/19: Familiar with 'phishing'?", [("Yes", "yes"), ("No", "no")]),
        "knows_phishing": ("scenario1", "📧 SCENARIO 1: Email from UCC IT says password expires today. Click link? What do you do?", [("Click link", "clicked"), ("Check with IT first", "safe"), ("Ignore", "safe")]),
        "scenario1": ("scenario2", "📱 SCENARIO 2: SMS: 'MTN credited GHS 500. Claim now: http://short.link'", [("Click link", "clicked"), ("Ignore & delete", "safe"), ("Call MTN official", "safe")]),
        "scenario2": ("scenario3", "💼 SCENARIO 3: LinkedIn: 'Urgent job offer. Submit login details to apply'", [("Submit details", "clicked"), ("Ignore", "safe"), ("Verify recruiter", "safe")]),
        "scenario3": ("scenario4", "🏦 SCENARIO 4: Bank email: 'Suspicious activity. Confirm account or it will be frozen'", [("Click link", "clicked"), ("Call bank official", "safe"), ("Delete email", "safe")]),
        "scenario4": ("scenario5", "📧 SCENARIO 5: Email from lecturer: 'Click here for course materials' (poor grammar)", [("Click link", "clicked"), ("Verify with lecturer", "safe"), ("Ignore", "safe")]),
        "scenario5": ("uses_2fa", "QUESTION: Do you use two-factor authentication?", [("Always", "always"), ("Sometimes", "sometimes"), ("Never", "never")]),
        "uses_2fa": ("shares_password", "QUESTION: Have you shared your password?", [("Yes", "yes"), ("No", "no")]),
        "shares_password": ("report_suspicious", "QUESTION: Do you report suspicious messages?", [("Always", "always"), ("Sometimes", "sometimes"), ("Never", "never")]),
    }
    
    if step in flow:
        next_step, text, opts = flow[step]
        user_sessions[user_id]["step"] = next_step
        keyboard = [[InlineKeyboardButton(label, callback_data=val)] for label, val in opts]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        answers = user_sessions[user_id]["answers"]
        answers["submission_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        row = {
            "user_id": query.from_user.id,
            "username": query.from_user.username,
            "group": answers.get("group", ""),
            "age": answers.get("age", ""),
            "gender": answers.get("gender", ""),
            "year_of_study": answers.get("year_of_study", ""),
            "programme": answers.get("programme", ""),
            "email_usage": answers.get("email_usage", ""),
            "mobile_money_usage": answers.get("mobile_money_usage", ""),
            "social_media_usage": answers.get("social_media_usage", ""),
            "knows_phishing_term": answers.get("knows_phishing", ""),
            "phishing_definition": answers.get("definition", ""),
            "identifies_indicators": answers.get("indicators", ""),
            "received_suspicious": answers.get("received_suspicious", ""),
            "prior_compromise": answers.get("prior_compromise", ""),
            "prior_training": answers.get("prior_training", ""),
            "scenario_1_response": answers.get("scenario1", ""),
            "scenario_2_response": answers.get("scenario2", ""),
            "scenario_3_response": answers.get("scenario3", ""),
            "scenario_4_response": answers.get("scenario4", ""),
            "scenario_5_response": answers.get("scenario5", ""),
            "uses_2fa": answers.get("uses_2fa", ""),
            "shares_password": answers.get("shares_password", ""),
            "report_suspicious": answers.get("report_suspicious", ""),
            "submission_time": answers.get("submission_time", ""),
        }
        
        df = pd.read_csv(CSV_FILE)
        df.loc[len(df)] = row
        df.to_csv(CSV_FILE, index=False)
        
        await query.edit_message_text("✅ Thank you! Your responses have been recorded for this study.")
        del user_sessions[user_id]

# ============================================
# FLASK APP
# ============================================

flask_app = Flask(__name__)
telegram_app = Application.builder().token(TOKEN).build()

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(group_handler, pattern="^(STEM|NON-STEM)$"))
telegram_app.add_handler(CallbackQueryHandler(question_handler))

@flask_app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            update = Update.de_json(request.get_json(force=True), telegram_app.bot)
            telegram_app.process_update(update)
            return "ok", 200
        except Exception as e:
            return str(e), 500
    return "Bot is running!"

@flask_app.route("/setwebhook")
def set_webhook():
    url = "https://uccphishing2024.pythonanywhere.com/"
    result = telegram_app.bot.set_webhook(url)
    return f"Webhook set: {result}"

@flask_app.route("/health")
def health():
    return jsonify({"status": "ok", "csv_exists": os.path.exists(CSV_FILE), "csv_path": CSV_FILE})

application = flask_app

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=5000)