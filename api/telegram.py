
import json
import os
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")


def send_message(chat_id, text):
    if not TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text
    }).encode()

    request = urllib.request.Request(url, data=payload)
    with urllib.request.urlopen(request, timeout=10) as response:
        response.read()


def reply_to_update(update):
    message = update.get("message", {})
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    text = message.get("text", "").strip()

    if not chat_id or not text:
        return

    command = text.split()[0].split("@")[0].lower()

    if command == "/start":
        reply = (
            "🎉 Welcome to ExamAce AI!\n\n"
            "Your personal exam preparation companion.\n\n"
            "📅 /plan - Get a starter study plan\n"
            "🧠 /quiz - Try a practice question\n"
            "📊 /progress - Get progress-tracking tips\n"
            "📚 /subjects - Explore supported exams\n"
            "❓ /help - See available commands\n\n"
            "Study smarter. Prepare better. Aim higher! 🚀"
        )
    elif command == "/help":
        reply = (
            "📚 ExamAce AI Help\n\n"
            "/start - Start the bot\n"
            "/plan - Study plan guidance\n"
            "/quiz - Practice question\n"
            "/progress - Progress tips\n"
            "/subjects - Exam options"
        )
    elif command == "/plan":
        reply = (
            "📅 Let's build a study habit!\n\n"
            "1. Choose two subjects for today.\n"
            "2. Study each for 25 minutes.\n"
            "3. Take a 5-minute break.\n"
            "4. Answer practice questions and review mistakes.\n\n"
            "Personalised timetables will be added in a future update."
        )
    elif command == "/quiz":
        reply = (
            "🧠 Quick maths quiz\n\n"
            "What is 15% of 200?\n\n"
            "A) 15\nB) 20\nC) 30\nD) 45\n\n"
            "Reply A, B, C or D."
        )
    elif text.strip().upper() in {"A", "B", "C", "D"}:
        if text.strip().upper() == "C":
            reply = "✅ Correct! 15% of 200 is 30. Well done!"
        else:
            reply = "Not quite! The correct answer is C) 30. Keep practising! 💪"
    elif command == "/progress":
        reply = (
            "📊 Your study progress\n\n"
            "After each session, note your subject, study time, "
            "questions attempted and mistakes reviewed.\n\n"
            "Automatic progress tracking will be added later."
        )
    elif command == "/subjects":
        reply = (
            "📚 ExamAce AI study options\n\n"
            "• WAEC\n• JAMB\n• NECO\n• GCE\n• School exams\n\n"
            "Choose your subjects and begin revising!"
        )
    else:
        reply = "Try /start, /plan, /quiz, /progress or /subjects. 📚"

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
            reply_to_update(update)
        except Exception as error:
            print("Webhook processing error:", str(error))

        # Acknowledge Telegram so it does not keep retrying the update.
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ExamAce AI webhook is ready.")
