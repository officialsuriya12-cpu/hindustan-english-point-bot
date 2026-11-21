import os
import asyncio
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

app = Flask(__name__)

@app.route('/')
def home():
    return "Hindustan English Point Quiz Bot is Running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

QUIZ_DATA = {
    "science": {
        "name": "🔬 विज्ञान (Science)",
        "questions": [
            {"q": "1. प्रकाश के परावर्तन के कितने नियम हैं?", "options": ["1", "2", "3", "4"], "ans": 1},
            {"q": "2. विद्युत धारा का SI मात्रक क्या है?", "options": ["वोल्ट (Volt)", "ओम (Ohm)", "एम्पियर (Ampere)", "वाट (Watt)"], "ans": 2},
            {"q": "3. मनुष्य में वृक्क (Kidney) एक तंत्र का भाग है जो संबंधित है:", "options": ["पोषण से", "श्वसन से", "उत्सर्जन से", "परिवहन से"], "ans": 2}
        ]
    },
    "sst": {
        "name": "🌍 सामाजिक विज्ञान (SST)",
        "questions": [
            {"q": "1. भारत में वित्तीय वर्ष कहा जाता है:", "options": ["1 जनवरी से 31 दिसंबर", "1 जुलाई से 30 जून", "1 अप्रैल से 31 मार्च", "1 सितंबर से 31 अगस्त"], "ans": 2},
            {"q": "2. 'हिंद स्वराज' पुस्तक किसके द्वारा लिखी गई?", "options": ["बाल गंगाधर तिलक", "गोपाल कृष्ण गोखले", "महात्मा गांधी", "लाला लाजपत राय"], "ans": 2},
            {"q": "3. बिहार का शोक किस नदी को कहा जाता है?", "options": ["गंगा", "कोसी", "गंडक", "सोन"], "ans": 1}
        ]
    },
    "math": {
        "name": "📐 गणित (Math)",
        "questions": [
            {"q": "1. दो परिमेय संख्याओं के बीच अधिकतम कितनी परिमेय संख्याएं हो सकती हैं?", "options": ["1", "2", "3", "अनंत (Infinite)"], "ans": 3},
            {"q": "2. यदि sin θ = cos θ हो, तो θ का मान क्या होगा?", "options": ["0°", "30°", "45°", "90°"], "ans": 2},
            {"q": "3. वृत्त के केंद्र पर बना कोण कितने डिग्री का होता है?", "options": ["90°", "180°", "270°", "360°"], "ans": 3}
        ]
    },
    "hindi": {
        "name": "📖 हिंदी (Hindi)",
        "questions": [
            {"q": "1. 'श्रम विभाजन और जाति प्रथा' के लेखक कौन हैं?", "options": ["महात्मा गांधी", "भीमराव अंबेडकर", "रामविलास शर्मा", "हजारी प्रसाद द्विवेदी"], "ans": 1},
            {"q": "2. 'विष के दांत' कहानी के रचयिता कौन हैं?", "options": ["अमरकांत", "नलिन विलोचन शर्मा", "यतींद्र मिश्र", "मैक्स मूलर"], "ans": 1}
        ]
    },
    "english": {
        "name": "🔤 अंग्रेजी (English)",
        "questions": [
            {"q": "1. Who is the author of 'The Pace for Living'?", "options": ["R.C. Hutchinson", "Mahadevi Verma", "Leo Tolstoy", "Toni Morrison"], "ans": 0},
            {"q": "2. Choose the correct spelling:", "options": ["Envirnoment", "Environment", "Enviornment", "Enviroment"], "ans": 1}
        ]
    }
}

def get_subject_keyboard():
    keyboard = []
    for key, val in QUIZ_DATA.items():
        keyboard.append([InlineKeyboardButton(val["name"], callback_data=f"sub:{key}")])
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    welcome_text = (
        f"🙏 नमस्ते *{user_name}*!\n\n"
        "🎓 *Hindustan English Point* के बिहार बोर्ड कक्षा 10वीं ऑब्जेक्टिव क्विज़ बॉट में आपका स्वागत है।\n\n"
        "👇 टेस्ट शुरू करने के लिए नीचे अपना विषय चुनें:"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=get_subject_keyboard())

async def send_question(query, context, sub_key, q_index):
    questions = QUIZ_DATA[sub_key]["questions"]
    q_data = questions[q_index]
    labels = ["A", "B", "C", "D"]
    keyboard = []
    for idx, opt in enumerate(q_data["options"]):
        keyboard.append([InlineKeyboardButton(f"{labels[idx]}. {opt}", callback_data=f"ans:{sub_key}:{q_index}:{idx}")])
    text = (
        f"📚 *{QUIZ_DATA[sub_key]['name']}*\n"
        f"प्रश्न {q_index + 1} / {len(questions)}\n\n"
        f"*{q_data['q']}*"
    )
    await query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu":
        await query.edit_message_text("👇 नया टेस्ट देने के लिए विषय चुनें:", reply_markup=get_subject_keyboard())
        return

    if data.startswith("sub:"):
        _, sub_key = data.split(":")
        context.user_data["score"] = 0
        await send_question(query, context, sub_key, 0)

    elif data.startswith("ans:"):
        _, sub_key, q_idx_str, chosen_str = data.split(":")
        q_idx = int(q_idx_str)
        chosen = int(chosen_str)
        questions = QUIZ_DATA[sub_key]["questions"]
        correct = questions[q_idx]["ans"]
        labels = ["A", "B", "C", "D"]

        if chosen == correct:
            context.user_data["score"] = context.user_data.get("score", 0) + 1
            feedback = "🎉 *Well Done! बिल्कुल सही जवाब!*"
        else:
            right_text = f"{labels[correct]}. {questions[q_idx]['options'][correct]}"
            feedback = f"❌ *गलत जवाब!*\n✅ सही उत्तर है: *{right_text}*"

        next_idx = q_idx + 1
        if next_idx < len(questions):
            keyboard = [[InlineKeyboardButton("अगला प्रश्न ➡️", callback_data=f"next:{sub_key}:{next_idx}")]]
            await query.edit_message_text(
                text=f"{feedback}\n\n📊 वर्तमान स्कोर: *{context.user_data['score']}*",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            total = len(questions)
            score = context.user_data["score"]
            keyboard = [
                [InlineKeyboardButton("🔄 फिर से यही टेस्ट दें", callback_data=f"sub:{sub_key}")],
                [InlineKeyboardButton("📚 दूसरा विषय चुनें", callback_data="menu")]
            ]
            await query.edit_message_text(
                text=(
                    f"{feedback}\n\n"
                    f"🏆 *टेस्ट पूरा हुआ!*\n"
                    f"आपका कुल स्कोर: *{score} / {total}*\n\n"
                    "शानदार अभ्यास! आप जितनी बार चाहें फिर से टेस्ट दे सकते हैं।"
                ),
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    elif data.startswith("next:"):
        _, sub_key, next_idx_str = data.split(":")
        await send_question(query, context, sub_key, int(next_idx_str))

def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        print("Error: BOT_TOKEN not found!")
        return

    threading.Thread(target=run_web, daemon=True).start()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
 
