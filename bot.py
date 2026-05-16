import os
import pandas as pd
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ============================================
# CONFIGURATION
# ============================================

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8665911975:AAHtyG2P-ECob4hQCIdKN0as9054lgrMm0I")

# YOUR TELEGRAM USER ID - ONLY YOU CAN USE /download
# To find your ID: Telegram -> search @userinfobot -> send /start
YOUR_USER_ID = 6955757619  # Replace with your actual Telegram user ID!

# ============================================
# CREATE CSV IF NOT EXISTS
# ============================================
CSV_COLUMNS = [
    "user_id", "username", "group", "submission_time",
    "age", "gender", "year_of_study", "programme",
    "email_usage", "mobile_money_usage", "social_media_usage",
    "knows_phishing", "scenario_1", "scenario_2", "scenario_3", "scenario_4", "scenario_5", "score"
]

if not os.path.exists("data.csv"):
    df = pd.DataFrame(columns=CSV_COLUMNS)
    df.to_csv("data.csv", index=False)

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
# STATS COMMAND - Anyone can see progress
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
# DOWNLOAD COMMAND - ONLY YOU CAN USE THIS
# ============================================
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send the CSV file to the researcher only"""
    
    # Check if user is authorized
    if update.effective_user.id != YOUR_USER_ID:
        await update.message.reply_text("⛔ Access denied. This command is for researchers only.")
        return
    
    try:
        with open("data.csv", "rb") as f:
            await update.message.reply_document(
                document=f, 
                filename=f"phishing_study_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
        await update.message.reply_text("✅ Data file sent successfully!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ============================================
# HANDLERS
# ============================================
async def group_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_sessions[user_id]["answers"]["group"] = query.data
    user_sessions[user_id]["step"] = "age"
    keyboard = [[InlineKeyboardButton("18-21", callback_data="age_18_21")], [InlineKeyboardButton("22-25", callback_data="age_22_25")], [InlineKeyboardButton("26-30", callback_data="age_26_30")], [InlineKeyboardButton("31+", callback_data="age_31_plus")]]
    await query.edit_message_text("📋 QUESTION 1/19\n\nWhat is your age range?", reply_markup=InlineKeyboardMarkup(keyboard))

async def age_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    age_map = {"age_18_21": "18-21", "age_22_25": "22-25", "age_26_30": "26-30", "age_31_plus": "31+"}
    user_sessions[user_id]["answers"]["age"] = age_map.get(query.data, "18-21")
    user_sessions[user_id]["step"] = "gender"
    keyboard = [[InlineKeyboardButton("Male", callback_data="gender_male")], [InlineKeyboardButton("Female", callback_data="gender_female")], [InlineKeyboardButton("Prefer not to say", callback_data="gender_prefer_not")]]
    await query.edit_message_text("📋 QUESTION 2/19\n\nWhat is your gender?", reply_markup=InlineKeyboardMarkup(keyboard))

async def gender_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    gender_map = {"gender_male": "Male", "gender_female": "Female", "gender_prefer_not": "Prefer not to say"}
    user_sessions[user_id]["answers"]["gender"] = gender_map.get(query.data, "Male")
    user_sessions[user_id]["step"] = "year"
    keyboard = [[InlineKeyboardButton("Level 100", callback_data="year_100")], [InlineKeyboardButton("Level 200", callback_data="year_200")], [InlineKeyboardButton("Level 300", callback_data="year_300")], [InlineKeyboardButton("Level 400", callback_data="year_400")]]
    await query.edit_message_text("📋 QUESTION 3/19\n\nWhat is your year of study?", reply_markup=InlineKeyboardMarkup(keyboard))

async def year_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    year_map = {"year_100": "100", "year_200": "200", "year_300": "300", "year_400": "400"}
    user_sessions[user_id]["answers"]["year"] = year_map.get(query.data, "100")
    user_sessions[user_id]["step"] = "programme"
    keyboard = [[InlineKeyboardButton("Sciences", callback_data="prog_sciences")], [InlineKeyboardButton("Humanities", callback_data="prog_humanities")], [InlineKeyboardButton("Business", callback_data="prog_business")], [InlineKeyboardButton("Education", callback_data="prog_education")]]
    await query.edit_message_text("📋 QUESTION 4/19\n\nSelect your programme type:", reply_markup=InlineKeyboardMarkup(keyboard))

async def programme_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    prog_map = {"prog_sciences": "Sciences", "prog_humanities": "Humanities", "prog_business": "Business", "prog_education": "Education"}
    user_sessions[user_id]["answers"]["programme"] = prog_map.get(query.data, "Sciences")
    user_sessions[user_id]["step"] = "email"
    keyboard = [[InlineKeyboardButton("Daily", callback_data="email_daily")], [InlineKeyboardButton("Weekly", callback_data="email_weekly")], [InlineKeyboardButton("Occasionally", callback_data="email_occasional")], [InlineKeyboardButton("Rarely", callback_data="email_rarely")]]
    await query.edit_message_text("📋 QUESTION 5/19\n\nHow often do you use email?", reply_markup=InlineKeyboardMarkup(keyboard))

async def email_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    email_map = {"email_daily": "Daily", "email_weekly": "Weekly", "email_occasional": "Occasionally", "email_rarely": "Rarely"}
    user_sessions[user_id]["answers"]["email"] = email_map.get(query.data, "Daily")
    user_sessions[user_id]["step"] = "mobile"
    keyboard = [[InlineKeyboardButton("Very often", callback_data="mobile_very_often")], [InlineKeyboardButton("Often", callback_data="mobile_often")], [InlineKeyboardButton("Sometimes", callback_data="mobile_sometimes")], [InlineKeyboardButton("Never", callback_data="mobile_never")]]
    await query.edit_message_text("📋 QUESTION 6/19\n\nHow often do you use mobile money or online banking?", reply_markup=InlineKeyboardMarkup(keyboard))

async def mobile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    mobile_map = {"mobile_very_often": "Very often", "mobile_often": "Often", "mobile_sometimes": "Sometimes", "mobile_never": "Never"}
    user_sessions[user_id]["answers"]["mobile"] = mobile_map.get(query.data, "Sometimes")
    user_sessions[user_id]["step"] = "social"
    keyboard = [[InlineKeyboardButton("Daily", callback_data="social_daily")], [InlineKeyboardButton("Weekly", callback_data="social_weekly")], [InlineKeyboardButton("Occasionally", callback_data="social_occasional")], [InlineKeyboardButton("Rarely", callback_data="social_rarely")]]
    await query.edit_message_text("📋 QUESTION 7/19\n\nHow often do you use social media?", reply_markup=InlineKeyboardMarkup(keyboard))

async def social_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    social_map = {"social_daily": "Daily", "social_weekly": "Weekly", "social_occasional": "Occasionally", "social_rarely": "Rarely"}
    user_sessions[user_id]["answers"]["social"] = social_map.get(query.data, "Daily")
    user_sessions[user_id]["step"] = "knows_phishing"
    keyboard = [[InlineKeyboardButton("Yes", callback_data="knows_yes")], [InlineKeyboardButton("No", callback_data="knows_no")], [InlineKeyboardButton("Not sure", callback_data="knows_not_sure")]]
    await query.edit_message_text("📋 QUESTION 8/19\n\nAre you familiar with the term 'phishing'?", reply_markup=InlineKeyboardMarkup(keyboard))

async def knows_phishing_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    knows_map = {"knows_yes": "Yes", "knows_no": "No", "knows_not_sure": "Not sure"}
    user_sessions[user_id]["answers"]["knows_phishing"] = knows_map.get(query.data, "No")
    user_sessions[user_id]["step"] = "scenario1"
    keyboard = [[InlineKeyboardButton("Click the link", callback_data="s1_clicked")], [InlineKeyboardButton("Check with IT first", callback_data="s1_safe")], [InlineKeyboardButton("Delete email", callback_data="s1_safe")]]
    await query.edit_message_text("📧 SCENARIO 1/5\n\nEmail from 'UCC IT Helpdesk': 'Your password expires today. Click here to keep it.'\n\nWhat do you do?", reply_markup=InlineKeyboardMarkup(keyboard))

async def scenario1_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_sessions[user_id]["answers"]["scenario1"] = "clicked" if "clicked" in query.data else "safe"
    user_sessions[user_id]["step"] = "scenario2"
    keyboard = [[InlineKeyboardButton("Click link", callback_data="s2_clicked")], [InlineKeyboardButton("Ignore and delete", callback_data="s2_safe")], [InlineKeyboardButton("Call MTN official line", callback_data="s2_safe")]]
    await query.edit_message_text("📱 SCENARIO 2/5\n\nSMS: 'Your MTN mobile money has been credited GHS 500. Claim now: http://short.link'\n\nWhat do you do?", reply_markup=InlineKeyboardMarkup(keyboard))

async def scenario2_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_sessions[user_id]["answers"]["scenario2"] = "clicked" if "clicked" in query.data else "safe"
    user_sessions[user_id]["step"] = "scenario3"
    keyboard = [[InlineKeyboardButton("Submit details", callback_data="s3_clicked")], [InlineKeyboardButton("Ignore", callback_data="s3_safe")], [InlineKeyboardButton("Verify recruiter", callback_data="s3_safe")]]
    await query.edit_message_text("💼 SCENARIO 3/5\n\nLinkedIn: 'Urgent job offer. Submit your login details to apply.'\n\nWhat do you do?", reply_markup=InlineKeyboardMarkup(keyboard))

async def scenario3_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_sessions[user_id]["answers"]["scenario3"] = "clicked" if "clicked" in query.data else "safe"
    user_sessions[user_id]["step"] = "scenario4"
    keyboard = [[InlineKeyboardButton("Click link", callback_data="s4_clicked")], [InlineKeyboardButton("Call bank official", callback_data="s4_safe")], [InlineKeyboardButton("Delete email", callback_data="s4_safe")]]
    await query.edit_message_text("🏦 SCENARIO 4/5\n\nBank email: 'Suspicious activity detected. Confirm your account or it will be frozen.'\n\nWhat do you do?", reply_markup=InlineKeyboardMarkup(keyboard))

async def scenario4_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_sessions[user_id]["answers"]["scenario4"] = "clicked" if "clicked" in query.data else "safe"
    user_sessions[user_id]["step"] = "scenario5"
    keyboard = [[InlineKeyboardButton("Click link", callback_data="s5_clicked")], [InlineKeyboardButton("Verify with lecturer", callback_data="s5_safe")], [InlineKeyboardButton("Ignore", callback_data="s5_safe")]]
    await query.edit_message_text("📧 SCENARIO 5/5\n\nEmail from lecturer: 'Click here for course materials' (poor grammar)\n\nWhat do you do?", reply_markup=InlineKeyboardMarkup(keyboard))

async def scenario5_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    answers = user_sessions[user_id]["answers"]
    answers["scenario5"] = "clicked" if "clicked" in query.data else "safe"
    answers["submission_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Calculate score
    score = 0
    for i in range(1, 6):
        if answers.get(f"scenario{i}", "") == "clicked":
            score += 1
    
    # Save to CSV
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
        "scenario_1": answers.get("scenario1", ""),
        "scenario_2": answers.get("scenario2", ""),
        "scenario_3": answers.get("scenario3", ""),
        "scenario_4": answers.get("scenario4", ""),
        "scenario_5": answers.get("scenario5", ""),
        "score": score,
    }
    
    df = pd.read_csv("data.csv")
    df.loc[len(df)] = row
    df.to_csv("data.csv", index=False)
    
    await query.edit_message_text(
        f"✅ THANK YOU FOR COMPLETING THE STUDY! ✅\n\n"
        f"📊 Your phishing vulnerability score: {score}/5\n"
        f"{'⚠️ Higher scores indicate more susceptibility to phishing attacks' if score >= 3 else '✅ Lower scores indicate good phishing awareness'}\n\n"
        f"🔒 Your responses have been recorded anonymously.\n\n"
        f"This research will help improve cybersecurity education at UCC."
    )
    
    del user_sessions[user_id]

# ============================================
# MAIN FUNCTION
# ============================================
def main():
    app = Application.builder().token(TOKEN).build()
    
    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("download", download))  # PRIVATE - only you can use
    
    # Callback handlers
    app.add_handler(CallbackQueryHandler(group_handler, pattern="^(STEM|NON-STEM)$"))
    app.add_handler(CallbackQueryHandler(age_handler, pattern="^age_"))
    app.add_handler(CallbackQueryHandler(gender_handler, pattern="^gender_"))
    app.add_handler(CallbackQueryHandler(year_handler, pattern="^year_"))
    app.add_handler(CallbackQueryHandler(programme_handler, pattern="^prog_"))
    app.add_handler(CallbackQueryHandler(email_handler, pattern="^email_"))
    app.add_handler(CallbackQueryHandler(mobile_handler, pattern="^mobile_"))
    app.add_handler(CallbackQueryHandler(social_handler, pattern="^social_"))
    app.add_handler(CallbackQueryHandler(knows_phishing_handler, pattern="^knows_"))
    app.add_handler(CallbackQueryHandler(scenario1_handler, pattern="^s1_"))
    app.add_handler(CallbackQueryHandler(scenario2_handler, pattern="^s2_"))
    app.add_handler(CallbackQueryHandler(scenario3_handler, pattern="^s3_"))
    app.add_handler(CallbackQueryHandler(scenario4_handler, pattern="^s4_"))
    app.add_handler(CallbackQueryHandler(scenario5_handler, pattern="^s5_"))
    
    print("🤖 UCC Phishing Study Bot is running with full survey!")
    print("📊 Data will be saved to data.csv automatically")
    print("🔐 /download command is PRIVATE - only you can use it")
    app.run_polling()

if __name__ == "__main__":
    main()
