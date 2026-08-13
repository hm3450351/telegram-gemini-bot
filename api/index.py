import os
import json
from http.server import BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import google.generativeai as genai

# 1. المفاتيح الخاصة بك
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN", "8946226333:AAEs31DZpAj6m3ue4QB6tcTFCRMG2EPG-M4")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AQ.Ab8RN6JESHLfTDjjPVu4PYxWPV1x8MPo-WJNi8PwppJzRRvuSw")

# تهيئة مكتبة Gemini باستخدام المفتاح المباشر
genai.configure(api_key=GEMINI_API_KEY)

# 🎯 2. التوجيه المباشر للذكاء الاصطناعي
SYSTEM_PROMPT = """
أنت خبير ومساعد ذكاء اصطناعي متخصص في تقنية المعلومات، الشبكات، والأمن السيبراني.
شخصيتك: دقيق، عملي، ومباشر في الشرح.
قواعد الإجابة:
1. تجيب باللغة العربية دائماً وبأسلوب سهل وواضح وعند استلام اي رسائل ستبدأ بالتعريف عن نفسك بإسم سايبرون وستعرف عن مطورك محمد الوشلي و ستتصرف كانك شخص بشري وترد باسلوب بشري مختصر وصارم بحيث تحقق هدف مطورك والذي هو التفرغ للدراسة والحفاظ على العلاقات والتعامل بواقعية وانسانية وضمن حدود لا يمكن تجاوزها .
2. عند كتابة أكواد أو أوامر تيرمينال، استخدم التنسيق المخصص للأكواد.
3. إذا سُئلت عن شيء خارج اختصاصك التقني، أجب باختصار وبدقه .
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_PROMPT
)

app_telegram = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = (
        f"أهلاً بك {update.effective_user.first_name}! 🤖✨\n\n"
        "أنا مساعد الذكاء الاصطناعي المشغّل بواسطة Google Gemini.\n"
        "أنا جاهز لاستقبال أسئلتك واستفساراتك التقنية والبرمجية."
    )
    await update.message.reply_text(welcome_msg)

def ask_ai(user_prompt: str) -> str:
    try:
        response = model.generate_content(user_prompt)
        return response.text
    except Exception as e:
        return f"⚠️ حدث خطأ أثناء الاتصال بنموذج Gemini: {str(e)}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    response = ask_ai(user_text)
    await update.message.reply_text(response)

app_telegram.add_handler(CommandHandler("start", start))
app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            json_data = json.loads(post_data.decode('utf-8'))
            update = Update.de_json(json_data, app_telegram.bot)
            
            import asyncio
            asyncio.run(app_telegram.initialize())
            asyncio.run(app_telegram.process_update(update))
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"OK")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Gemini Free Bot is live on Vercel!")
