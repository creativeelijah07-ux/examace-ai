
import os
import json
import urllib.request
import urllib.parse
from http.server import BaseHTTPRequestHandler

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

def send_message(chat_id, text):
    if not TELEGRAM_BOT_TOKEN:
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text
    }).encode()

    request = urllib.request.Request(url, data=data)
    try:
        urllib.request.urlopen(request, timeout=10)
    except Exception as error:
        print("Telegram message failed:", error)

def handle_update(update):
    message = update.get("message", {})
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    text = message.get("text", "").strip()

    if not chat_id or not text:
        return

    if text == "/start":
        reply = (
            "🎉 Welcome to ExamAce AI!\n\n"
            "Your personal exam preparation companion.\n\n"
            "📅 /plan - Get a starter study plan\n"
            "🧠 /quiz - Practise a sample question\n"
            "📊 /progress - View your progress guide\n"
            "📚 /subjects - Explore supported exams\n"
            "❓ /help - Get help\n\n"
            "Study smarter. Prepare better. Aim higher! 🚀"
        )
    elif text == "/help":
        reply = (
            "📚 ExamAce AI Help\n\n"
            "/start - Start the bot\n"
            "/plan - Get a starter study plan\n"
            "/quiz - Try a practice question\n"
            "/progress - Study progress tips\n"
            "/subjects - Explore exam options"
        )
    elif text == "/plan":
        reply = (
            "📅 Let's build your study habit!\n\n"
            "Start with 2 subjects each day. Study for 25 minutes, "
            "take a 5-minute break, then answer practice questions.\n\n"
            "Tell me your exam, subjects and exam date to personalise "
            "your plan in a future update."
        )
    elif text == "/quiz":
        reply = (
            "🧠 Quick practice question\n\n"
            "What is 15% of 200?\n\n"
            "A) 15\nB) 20\nC) 30\nD) 45\n\n"
            "Reply A, B, C or D."
        )
    elif text.upper() in ["A", "B", "C", "D"]:
        reply = (
            "C) 30 is correct!" if text.upper() == "C"
            else "Not quite! The correct answer is C) 30."
        )
    elif text == "/progress":
        reply = (
            "📊 Progress tip\n\n"
            "After each study session, record the subject, "
            "minutes studied and questions answered. "
            "Persistent progress tracking will be added later."
        )
    elif text == "/subjects":
        reply = (
            "📚 ExamAce AI supports preparation for:\n\n"
            "• WAEC\n• JAMB\n• NECO\n• GCE\n• School exams\n\n"
            "Choose your subjects and start practising!"
        )
    else:
        reply = (
            "I'm here to help you prepare for your exams! 📚\n\n"
            "Try /plan, /quiz, /progress or /subjects."
        )

    send_message(chat_id, reply)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path.split("?")[0] != "/api/telegram":
            self.send_response(404)
            self.end_headers()
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            update = json.loads(self.rfile.read(length))
            handle_update(update)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        except Exception:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ExamAce AI webhook is running.")
