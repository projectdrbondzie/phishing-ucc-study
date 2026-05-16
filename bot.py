import os
import pandas as pd
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ============================================
# GET TOKEN FROM ENVIRONMENT VARIABLE
# ============================================
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8665911975:AAHtyG2P-ECob4hQCIdKN0as9054lgrMm0I")

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
        "✅ Takes 3-4 minutes\n"
        "✅ Your data helps improve cybersecurity education\n\n"
        "Please select your academic group:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ============================================
# STATS COMMAND (RESEARCHER ONLY)
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
# HANDLE GROUP SELECTION
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
# AGE HANDLER
# ============================================
async def age_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_sessions[user_id]["answers"]["age"] = query.data
    user_sessions[user_id]["step"] = "gender"
    
    keyboard = [
        [InlineKeyboardButton("👨 Male", callback_data="male")],
        [InlineKeyboardButton("👩 Female", callback_data="female")],
        [InlineKeyboardButton("🔒 Prefer not to say", callback_data="prefer_not")]
    ]
    
    await query.edit_message_text(
        "📋 QUESTION 2/19\n\nWhat is your gender?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ============================================
# GENDER HANDLER
# ============================================
async def gender_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_sessions[user_id]["answers"]["gender"] = query.data
    user_sessions[user_id]["step"] = "year"
    
    keyboard = [
        [InlineKeyboardButton("Level 100", callback_data="100")],
        [InlineKeyboardButton("Level 200", callback_data="200")],
        [InlineKeyboardButton("Level 300", callback_data="300")],
        [InlineKeyboardButton("Level 400", callback_data="400")]
    ]
    
    await query.edit_message_text(
        "📋 QUESTION 3/19\n\nWhat is your year of study?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ============================================
# YEAR HANDLER
# ============================================
async def year_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_sessions[user_id]["answers"]["year"] = query.data
    user_sessions[user_id]["step"] = "programme"
    
    keyboard = [
        [InlineKeyboardButton("🔬 Sciences", callback_data="sciences")],
        [InlineKeyboardButton("📖 Humanities", callback_data="humanities")],
        [InlineKeyboardButton("💼 Business", callback_data="business")],
        [InlineKeyboardButton("📚 Education", callback_data="education")]
    ]
    
    await query.edit_message_text(
        "📋 QUESTION 4/19\n\nSelect your programme type:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ============================================
# PROGRAMME HANDLER
# ============================================
async def programme_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_sessions[user_id]["answers"]["programme"] = query.data
    user_sessions[user_id]["step"] = "email"
    
    keyboard = [
        [InlineKeyboardButton("📧 Daily", callback_data="daily")],
        [InlineKeyboardButton("📧 Several times/week", callback_data="weekly")],
        [InlineKeyboardButton("📧 Occasionally", callback_data="occasional")],
        [InlineKeyboardButton("📧 Rarely", callback_data="rarely")]
    ]
    
    await query.edit_message_text(
        "📋 QUESTION 5/19\n\nHow often do you use email?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ============================================
# EMAIL HANDLER
# ============================================
async def email_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_sessions[user_id]["answers"]["email"] = query.data
    user_sessions[user_id]["step"] = "mobile"
    
    keyboard = [
        [InlineKeyboardButton("💰 Very often", callback_data="very_often")],
        [InlineKeyboardButton("💰 Often", callback_data="often")],
        [InlineKeyboardButton("💰 Sometimes", callback_data="sometimes")],
        [InlineKeyboardButton("💰 Never", callback_data="never")]
    ]
    
    await query.edit_message_text(
        "📋 QUESTION 6/19\n\nHow often do you use mobile money or online banking?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ============================================
# MOBILE MONEY HANDLER
# ============================================
async def mobile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_sessions[user_id]["answers"]["mobile"] = query.data
    user_sessions[user_id]["step"] = "social"
    
    keyboard = [
        [InlineKeyboardButton("📱 Daily", callback_data="daily")],
        [InlineKeyboardButton("📱 Several times/week", callback_data="weekly")],
        [InlineKeyboardButton("📱 Occasionally", callback_data="occasional")],
        [InlineKeyboardButton("📱 Rarely", callback_data="rarely")]
    ]
    
    await query.edit_message_text(
        "📋 QUESTION 7/19\n\nHow often do you use social media?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ============================================
# SOCIAL MEDIA HANDLER
# ============================================
async def social_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_sessions[user_id]["answers"]["social"] = query.data
    user_sessions[user_id]["step"] = "knows_phishing"
    
    keyboard = [
        [InlineKeyboardButton("✅ Yes", callback_data="yes")],
        [InlineKeyboardButton("❌ No", callback_data="no")],
        [InlineKeyboardButton("🤔 Not sure", callback_data="not_sure")]
    ]
    
    await query.edit_message_text(
        "📋 QUESTION 8/19\n\nAre you familiar with the term 'phishing'?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ============================================
# KNOWS PHISHING HANDLER
# ============================================
async def knows_phishing_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_sessions[user_id]["answers"]["knows_phishing"] = query.data
    user_sessions[user_id]["step"] = "scenario1"
    
    keyboard = [
        [InlineKeyboardButton("❌ Click the link", callback_data="clicked")],
        [InlineKeyboardButton("✅ Check with IT department first", callback_data="safe")],
        [InlineKeyboardButton("🗑️ Delete email", callback_data="safe")]
    ]
    
    await query.edit_message_text(
        "📧 SCENARIO 1/5\n\n"
        "You receive an email from 'UCC IT Helpdesk' saying:\n"
        '"Your password expires today. Click here to keep it."\n\n'
        "What do you do?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ============================================
# SCENARIO 1 HANDLER
# ============================================
async def scenario1_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_sessions[user_id]["answers"]["scenario1"] = query.data
    user_sessions[user_id]["step"] = "scenario2"
    
    keyboard = [
        [InlineKeyboardButton("❌ Click link", callback_data="clicked")],
        [InlineKeyboardButton("✅ Ignore and delete", callback_data="safe")],
        [InlineKeyboardButton("✅ Call MTN official line", callback_data="safe")]
    ]
    
    await query.edit_message_text(
        "📱 SCENARIO 2/5\n\n"
        "SMS message:\n"
        '"Your MTN mobile money has been credited GHS 500. Claim now: http://short.link"\n\n'
        "What do you do?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ============================================
# SCENARIO 2 HANDLER
# ============================================
async def scenario2_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_sessions[user_id]["answers"]["scenario2"] = query.data
    user_sessions[user_id]["step"] = "scenario3"
    
    keyboard = [
        [InlineKeyboardButton("❌ Submit details", callback_data="clicked")],
        [InlineKeyboardButton("✅ Ignore", callback_data="safe")],
        [InlineKeyboardButton("✅ Verify recruiter independently", callback_data="safe")]
    ]
    
    await query.edit_message_text(
        "💼 SCENARIO 3/5\n\n"
        "LinkedIn message from a recruiter:\n"
        '"Urgent job offer. Submit your login details to apply."\n\n'
        "What do you do?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ============================================
# SCENARIO 3 HANDLER
# ============================================
async def scenario3_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_sessions[user_id]["answers"]["scenario3"] = query.data
    user_sessions[user_id]["step"] = "scenario4"
    
    keyboard = [
        [InlineKeyboardButton("❌ Click confirmation link", callback_data="clicked")],
        [InlineKeyboardButton("✅ Call bank official number", callback_data="safe")],
        [InlineKeyboardButton("🗑️ Delete email", callback_data="safe")]
    ]
    
    await query.edit_message_text(
        "🏦 SCENARIO 4/5\n\n"
        "Email from your bank:\n"
        '"Suspicious activity detected. Confirm your account now or it will be frozen."\n\n'
        "What do you do?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ============================================
# SCENARIO 4 HANDLER
# ============================================
async def scenario4_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_sessions[user_id]["answers"]["scenario4"] = query.data
    user_sessions[user_id]["step"] = "scenario5"
    
    keyboard = [
        [InlineKeyboardButton("❌ Click link", callback_data="clicked")],
        [InlineKeyboardButton("✅ Verify with lecturer directly", callback_data="safe")],
        [InlineKeyboardButton("🗑️ Ignore", callback_data="safe")]
    ]
    
    await query.edit_message_text(
        "📧 SCENARIO 5/5\n\n"
        "Email from a lecturer:\n"
        '"Click here to download important course materials."\n'
        "The email has poor grammar.\n\n"
        "What do you do?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ============================================
# SCENARIO 5 HANDLER (FINAL - SAVES DATA)
# ============================================
async def scenario5_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    answers = user_sessions[user_id]["answers"]
    answers["scenario5"] = query.data
    answers["submission_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Calculate vulnerability score (0-5, higher = more vulnerable)
    score = 0
    for i in range(1, 6):
        if answers.get(f"scenario{i}", "") == "clicked":
            score += 1
    
    # Prepare row for CSV
    row = {
        "user_id": query.from_user.id,
        "username": query.from_user.username,
        "group": answers.get("group", ""),
        "submission_time": answers.get("submission_time", ""),
        "age": answers.get("age", ""),
        "gender": answers.get("gender", ""),
        "year_of_study": answers.get("year", ""),
        "programme": answers.get("programme", ""),
        "email_usage": answers.get("email", ""),
        "mobile_money_usage": answers.get("mobile", ""),
        "social_media_usage": answers.get("social", ""),
        "knows_phishing": answers.get("knows_phishing", ""),
        "phishing_definition": "",
        "identifies_indicators": "",
        "received_suspicious": "",
        "prior_compromise": "",
        "prior_training": "",
        "scenario_1": answers.get("scenario1", ""),
        "scenario_2": answers.get("scenario2", ""),
        "scenario_3": answers.get("scenario3", ""),
        "scenario_4": answers.get("scenario4", ""),
        "scenario_5": answers.get("scenario5", ""),
        "uses_2fa": "",
        "shares_password": "",
        "report_suspicious": "",
        "score": score,
    }
    
    # Save to CSV
    df = pd.read_csv("data.csv")
    df.loc[len(df)] = row
    df.to_csv("data.csv", index=False)
    
    # Thank you message
    await query.edit_message_text(
        f"✅ THANK YOU FOR COMPLETING THE STUDY! ✅\n\n"
        f"📊 Your phishing vulnerability score: {score}/5\n"
        f"{'⚠️ Higher scores indicate more susceptibility to phishing attacks' if score >= 3 else '✅ Lower scores indicate good phishing awareness'}\n\n"
        f"🔒 Your responses have been recorded anonymously.\n\n"
        f"This research will help improve cybersecurity education at UCC.\n\n"
        f"You may now close this chat."
    )
    
    # Clean up session
    del user_sessions[user_id]

# ============================================
# MAIN FUNCTION
# ============================================
def main():
    app = Application.builder().token(TOKEN).build()
    
    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    
    # Callback handlers
    app.add_handler(CallbackQueryHandler(group_handler, pattern="^(STEM|NON-STEM)$"))
    app.add_handler(CallbackQueryHandler(age_handler, pattern="^(18-21|22-25|26-30|31+)$"))
    app.add_handler(CallbackQueryHandler(gender_handler, pattern="^(male|female|prefer_not)$"))
    app.add_handler(CallbackQueryHandler(year_handler, pattern="^(100|200|300|400)$"))
    app.add_handler(CallbackQueryHandler(programme_handler, pattern="^(sciences|humanities|business|education)$"))
    app.add_handler(CallbackQueryHandler(email_handler, pattern="^(daily|weekly|occasional|rarely)$"))
    app.add_handler(CallbackQueryHandler(mobile_handler, pattern="^(very_often|often|sometimes|never)$"))
    app.add_handler(CallbackQueryHandler(social_handler, pattern="^(daily|weekly|occasional|rarely)$"))
    app.add_handler(CallbackQueryHandler(knows_phishing_handler, pattern="^(yes|no|not_sure)$"))
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
