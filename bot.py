import os
import pandas as pd
from datetime import datetime
from flask import Flask, send_file
import threading

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

# 🔑 GET YOUR BOT TOKEN FROM ENVIRONMENT VARIABLE (Railway)
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8995182920:AAGs3WrTmGPpTO7FpDC32-mJgOfVdLLY5mA")
")

# ---------------------------
# CREATE CSV IF NOT EXISTS
# ---------------------------
CSV_COLUMNS = [
    "user_id", "username", "group", "age", "gender", "year_of_study", "programme",
    "email_usage", "mobile_money_usage", "social_media_usage",
    "knows_phishing_term", "phishing_definition", "identifies_indicators",
    "received_suspicious", "prior_compromise", "prior_training",
    "scenario_1_response", "scenario_2_response", "scenario_3_response",
    "scenario_4_response", "scenario_5_response",
    "uses_2fa", "shares_password", "report_suspicious", "submission_time", "score"
]

if not os.path.exists("data.csv"):
    df = pd.DataFrame(columns=CSV_COLUMNS)
    df.to_csv("data.csv", index=False)


# ---------------------------
# STORE USER SESSION DATA
# ---------------------------
user_sessions = {}


# ---------------------------
# START COMMAND
# ---------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_sessions[user_id] = {"step": "group", "answers": {}}
    
    keyboard = [
        [InlineKeyboardButton("STEM", callback_data="STEM")],
        [InlineKeyboardButton("NON-STEM", callback_data="NON-STEM")],
    ]
    await update.message.reply_text(
        "📚 WELCOME TO THE CYBER SECURITY STUDY\n\n"
        "This study examines phishing awareness among university students.\n"
        "All responses are anonymous and confidential.\n\n"
        "Please select your academic group:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ---------------------------
# STATS COMMAND - Check response count
# ---------------------------
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show statistics about responses collected"""
    df = pd.read_csv("data.csv")
    
    if len(df) == 0:
        await update.message.reply_text("📊 No responses collected yet.")
        return
    
    stem_count = len(df[df['group'] == 'STEM'])
    nonstem_count = len(df[df['group'] == 'NON-STEM'])
    avg_score = df['score'].mean() if 'score' in df.columns else 0
    
    await update.message.reply_text(
        f"📊 STUDY STATISTICS\n\n"
        f"Total responses: {len(df)}\n"
        f"STEM students: {stem_count}\n"
        f"NON-STEM students: {nonstem_count}\n"
        f"Average phishing susceptibility score (0-5): {avg_score:.2f}\n\n"
        f"Higher score means more susceptible to phishing."
    )


# ---------------------------
# HANDLE GROUP SELECTION
# ---------------------------
async def group_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_sessions[user_id]["answers"]["group"] = query.data
    user_sessions[user_id]["step"] = "age"
    
    keyboard = [
        [InlineKeyboardButton("18-21", callback_data="18-21")],
        [InlineKeyboardButton("22-25", callback_data="22-25")],
        [InlineKeyboardButton("Above 25", callback_data="above_25")],
    ]
    await query.edit_message_text(
        "📋 QUESTION 1/19\n\nWhat is your age range?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ---------------------------
# MASTER HANDLER FOR ALL QUESTIONS
# ---------------------------
async def question_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    step = user_sessions[user_id]["step"]
    user_sessions[user_id]["answers"][step] = query.data
    
    # Define the flow of questions
    flow = {
        "age": ("gender", "QUESTION 2/19\n\nWhat is your gender?", 
                [("Male", "male"), ("Female", "female"), ("Prefer not to say", "prefer_not")]),
        
        "gender": ("year_of_study", "QUESTION 3/19\n\nWhat is your year of study?",
                   [("Level 100", "100"), ("Level 200", "200"), ("Level 300", "300"), ("Level 400", "400")]),
        
        "year_of_study": ("programme", "QUESTION 4/19\n\nSelect your programme type:",
                          [("Sciences", "sciences"), ("Humanities", "humanities"), 
                           ("Business", "business"), ("Education", "education"), ("Other", "other")]),
        
        "programme": ("email_usage", "QUESTION 5/19\n\nHow often do you use email?",
                      [("Daily", "daily"), ("Several times a week", "weekly"), 
                       ("Occasionally", "occasional"), ("Rarely", "rarely")]),
        
        "email_usage": ("mobile_money_usage", "QUESTION 6/19\n\nHow often do you use mobile money or online banking?",
                        [("Very often", "very_often"), ("Often", "often"), 
                         ("Sometimes", "sometimes"), ("Never", "never")]),
        
        "mobile_money_usage": ("social_media_usage", "QUESTION 7/19\n\nHow often do you use social media?",
                               [("Daily", "daily"), ("Several times a week", "weekly"), 
                                ("Occasionally", "occasional"), ("Rarely", "rarely")]),
        
        "social_media_usage": ("knows_phishing", "QUESTION 8/19\n\nAre you familiar with the term 'phishing'?",
                               [("Yes", "yes"), ("No", "no"), ("Not sure", "not_sure")]),
        
        "knows_phishing": ("definition", "QUESTION 9/19\n\nWhat does phishing primarily refer to?",
                           [("Tricking users to reveal info", "correct"), 
                            ("Antivirus software", "wrong1"), 
                            ("Secure login method", "wrong2"), 
                            ("Not sure", "not_sure")]),
        
        "definition": ("indicators", "QUESTION 10/19\n\nWhich is a common indicator of phishing? (Select the best answer)",
                       [("Urgent language", "urgent"), ("Professional design", "bad"),
                        ("Official logo", "bad"), ("Not sure", "not_sure")]),
        
        "indicators": ("received_suspicious", "QUESTION 11/19\n\nHave you ever received a suspicious message asking for personal information?",
                       [("Yes, frequently", "frequently"), ("Yes, occasionally", "occasionally"),
                        ("No", "no"), ("Not sure", "not_sure")]),
        
        "received_suspicious": ("prior_compromise", "QUESTION 12/19\n\nHave you ever had an account compromised or lost money online?",
                                [("Yes", "yes"), ("No", "no"), ("Prefer not to say", "prefer_not")]),
        
        "prior_compromise": ("prior_training", "QUESTION 13/19\n\nHave you received any formal cybersecurity training?",
                             [("Yes", "yes"), ("No", "no"), ("Not sure", "not_sure")]),
        
        "prior_training": ("scenario1", "📧 SCENARIO 1/5\n\nYou receive an email from 'UCC IT Helpdesk' saying your password expires today. Click link to keep it. What do you do?",
                           [("Click the link", "clicked"), ("Check with IT department first", "safe"),
                            ("Delete email", "safe"), ("Not sure", "unsure")]),
        
        "scenario1": ("scenario2", "📱 SCENARIO 2/5\n\nSMS: 'Your MTN mobile money has been credited GHS 500. Claim now: http://short.link' What do you do?",
                      [("Click link", "clicked"), ("Ignore and delete", "safe"),
                       ("Call MTN official line", "safe"), ("Not sure", "unsure")]),
        
        "scenario2": ("scenario3", "💼 SCENARIO 3/5\n\nLinkedIn message from a recruiter: 'Urgent job offer. Submit your login details to apply.' What do you do?",
                      [("Submit details", "clicked"), ("Ignore", "safe"),
                       ("Verify recruiter independently", "safe"), ("Not sure", "unsure")]),
        
        "scenario3": ("scenario4", "🏦 SCENARIO 4/5\n\nEmail from your bank: 'Suspicious activity detected. Confirm your account now or it will be frozen.' What do you do?",
                      [("Click confirmation link", "clicked"), ("Call bank official number", "safe"),
                       ("Delete email", "safe"), ("Not sure", "unsure")]),
        
        "scenario4": ("scenario5", "📧 SCENARIO 5/5\n\nEmail from a lecturer: 'Click here to download important course materials.' The email has poor grammar. What do you do?",
                      [("Click link", "clicked"), ("Verify with lecturer directly", "safe"),
                       ("Ignore", "safe"), ("Not sure", "unsure")]),
        
        "scenario5": ("uses_2fa", "QUESTION 17/19\n\nDo you use two-factor authentication (2FA) where available?",
                      [("Always", "always"), ("Sometimes", "sometimes"), 
                       ("Never", "never"), ("Don't know what it is", "dont_know")]),
        
        "uses_2fa": ("shares_password", "QUESTION 18/19\n\nHave you ever shared your password with anyone?",
                     [("Yes", "yes"), ("No", "no"), ("Only with close friends/family", "sometimes")]),
        
        "shares_password": ("report_suspicious", "QUESTION 19/19\n\nIf you receive a suspicious message, do you report it?",
                            [("Always", "always"), ("Sometimes", "sometimes"), 
                             ("Never", "never"), ("Don't know how", "dont_know")]),
    }
    
    current_step = step
    if current_step in flow:
        next_step, question_text, options = flow[current_step]
        user_sessions[user_id]["step"] = next_step
        keyboard = [[InlineKeyboardButton(label, callback_data=value)] for label, value in options]
        
        await query.edit_message_text(
            f"📋 {question_text}",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    else:
        # End of questions - save to CSV
        answers = user_sessions[user_id]["answers"]
        answers["submission_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Calculate score (count how many times user clicked phishing links)
        score = 0
        for i in range(1, 6):
            if answers.get(f"scenario{i}", "") == "clicked":
                score += 1
        
        # Prepare row for CSV
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
            "score": score,
        }
        
        df = pd.read_csv("data.csv")
        df.loc[len(df)] = row
        df.to_csv("data.csv", index=False)
        
        await query.edit_message_text(
            "✅ Thank you for completing the study!\n\n"
            "Your responses have been recorded.\n\n"
            "📊 This research will help improve cybersecurity awareness at UCC.\n\n"
            "You may now close this chat."
        )
        
        # Clean up session
        del user_sessions[user_id]


# ---------------------------
# FLASK DOWNLOAD SERVER (for getting your data)
# ---------------------------
download_app = Flask(__name__)

@download_app.route('/download')
def download_data():
    """Download the CSV file with all responses"""
    return send_file("data.csv", as_attachment=True, download_name='phishing_study_data.csv')

@download_app.route('/')
def home():
    return "Phishing Study Bot is running! Visit /download to get your data."

def run_download_server():
    download_app.run(host='0.0.0.0', port=8080)

# Start the download server in a background thread
threading.Thread(target=run_download_server, daemon=True).start()


# ---------------------------
# MAIN FUNCTION
# ---------------------------
def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(group_handler, pattern="^(STEM|NON-STEM)$"))
    app.add_handler(CallbackQueryHandler(question_handler, pattern="^(?!STEM|NON-STEM$).*"))
    
    print("🤖 Bot is running with 19 questions and download endpoint...")
    print("📊 Visit YOUR_RAILWAY_URL:8080/download to get your data")
    app.run_polling()


if __name__ == "__main__":
    main()
