
import os
import json
import urllib.request
from http.server import BaseHTTPRequestHandler

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
API = f"https://api.telegram.org/bot{TOKEN}"

GENERAL = [
    "English", "Mathematics", "Biology",
    "Civic Education", "French"
]

DEPARTMENTS = {
    "Science": ["Chemistry", "Physics"],
    "Art": ["Literature", "Government"],
    "Commercial": ["Financial Accounting", "Commerce"]
}

QUESTIONS = {
    "English": ("Choose the correctly spelled word.",
                ["Recieve", "Receive", "Receeve", "Receve"], 1,
                "The correct spelling is Receive."),
    "Mathematics": ("What is 15% of 200?",
                    ["20", "25", "30", "35"], 2,
                    "15% of 200 = 0.15 × 200 = 30."),
    "Biology": ("Which organ pumps blood around the body?",
                ["Liver", "Lungs", "Kidney", "Heart"], 3,
                "The heart pumps blood around the body."),
    "Civic Education": ("What is the supreme law of Nigeria?",
                        ["The Constitution", "A school rule",
                         "A court notice", "A campaign speech"], 0,
                        "The Constitution is the supreme law of Nigeria."),
    "French": ("What does 'Bonjour' mean in English?",
               ["Good night", "Good morning/Hello",
                "Goodbye", "Thank you"], 1,
               "'Bonjour' is a French greeting."),
    "Chemistry": ("What is the chemical symbol for oxygen?",
                  ["Ox", "O", "Oy", "O2"], 1,
                  "O is the symbol for the oxygen element. O₂ represents an oxygen molecule."),
    "Physics": ("What is the SI unit of force?",
                ["Joule", "Watt", "Newton", "Pascal"], 2,
                "Force is measured in newtons (N)."),
    "Literature": ("Who writes a play?",
                   ["Playwright", "Audience", "Publisher", "Critic"], 0,
                   "A playwright writes plays."),
    "Government": ("Which arm of government interprets laws?",
                   ["Executive", "Legislature", "Judiciary", "Civil service"], 2,
                   "The judiciary interprets laws."),
    "Financial Accounting": ("Which statement shows assets and liabilities?",
                             ["Balance sheet", "Sales invoice",
                              "Receipt", "Petty cash voucher"], 0,
                             "A balance sheet reports assets, liabilities and equity."),
    "Commerce": ("What is trade?",
                ["Production only", "Buying and selling",
                 "Advertising only", "Transport only"], 1,
                "Trade involves buying and selling goods and services.")
}


def api_call(method, payload):
    if not TOKEN:
        return
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"{API}/{method}",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception:
        return None


def send_message(chat_id, text, keyboard=None):
    payload = {"chat_id": chat_id, "text": text}
    if keyboard:
        payload["reply_markup"] = {"inline_keyboard": keyboard}
    api_call("sendMessage", payload)


def subject_keyboard(subjects, prefix="subject"):
    return [
        [{"text": subject, "callback_data": f"{prefix}:{subject}"}]
        for subject in subjects
    ]


def show_subjects(chat_id):
    keyboard = [
        [{"text": "📘 General Subjects", "callback_data": "group:General"}],
        [{"text": "🔬 Science", "callback_data": "group:Science"}],
        [{"text": "🎨 Art", "callback_data": "group:Art"}],
        [{"text": "💼 Commercial", "callback_data": "group:Commercial"}]
    ]
    send_message(chat_id, "📚 Choose a subject category:", keyboard)


def show_question(chat_id, subject):
    if subject not in QUESTIONS:
        send_message(chat_id, "Please choose a subject from the menu.")
        return

    question, options, correct, explanation = QUESTIONS[subject]
    keyboard = [
        [{
            "text": f"{chr(65+i)}. {option}",
            "callback_data": f"answer:{subject}:{i}"
        }]
        for i, option in enumerate(options)
    ]
    send_message(
        chat_id,
        f"📚 {subject} Practice\n\n{question}",
        keyboard
    )


def handle_callback(callback):
    data = callback.get("data", "")
    chat_id = callback.get("message", {}).get("chat", {}).get("id")
    callback_id = callback.get("id")

    if callback_id:
        api_call("answerCallbackQuery", {"callback_query_id": callback_id})

    if not chat_id:
        return

    if data == "group:General":
        send_message(chat_id, "📘 Choose a general subject:",
                     subject_keyboard(GENERAL))
        return

    if data.startswith("group:"):
        department = data.split(":", 1)[1]
        if department in DEPARTMENTS:
            send_message(
                chat_id,
                f"📚 Choose a {department} subject:",
                subject_keyboard(DEPARTMENTS[department])
            )
        return

    if data.startswith("subject:"):
        subject = data.split(":", 1)[1]
        show_question(chat_id, subject)
        return

    if data.startswith("answer:"):
        parts = data.split(":")
        if len(parts) != 3:
            return

        subject = parts[1]
        try:
            selected = int(parts[2])
        except ValueError:
            return

        if subject not in QUESTIONS:
            return

        question, options, correct, explanation = QUESTIONS[subject]
        if selected == correct:
            result = "✅ Correct!"
        else:
            result = f"❌ Not quite. The correct answer is {chr(65+correct)}. {options[correct]}."

        send_message(
            chat_id,
            f"{result}\n\n💡 Explanation: {explanation}\n\n"
            "Ready to practise another subject? Send /quiz."
        )


def handle_update(update):
    if "callback_query" in update:
        handle_callback(update["callback_query"])
        return

    message = update.get("message", {})
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    text = message.get("text", "").strip()

    if not chat_id or not text:
        return

    command = text.split()[0].split("@")[0].lower()

    if command == "/start":
        send_message(
            chat_id,
            "🎓 Welcome to ExamAce AI!\n\n"
            "Your exam-preparation companion for WAEC, JAMB, NECO, "
            "GCE and school exams.\n\n"
            "📚 Choose subjects, practise questions and learn from explanations.\n\n"
            "Send /quiz to get started!"
        )
    elif command == "/help":
        send_message(
            chat_id,
            "📚 ExamAce AI Help\n\n"
            "/start - Start the bot\n"
            "/help - Get help\n"
            "/plan - Get a starter study plan\n"
            "/quiz - Choose a subject and practise\n"
            "/progress - Study progress tips\n"
            "/subjects - Explore available subjects"
        )
    elif command == "/plan":
        send_message(
            chat_id,
            "🗓️ Starter Study Plan\n\n"
            "1. Choose one subject to study.\n"
            "2. Study for 30 minutes.\n"
            "3. Practise questions for 15 minutes.\n"
            "4. Review your mistakes.\n\n"
            "Personalised saved timetables will be added later."
        )
    elif command == "/quiz":
        show_subjects(chat_id)
    elif command == "/subjects":
        show_subjects(chat_id)
    elif command == "/progress":
        send_message(
            chat_id,
            "📊 Progress tip\n\n"
            "Record the subject, minutes studied and questions answered "
            "after each session. Saved progress tracking is coming later."
        )
    else:
        send_message(chat_id, "Send /quiz to choose a subject and practise!")


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ExamAce AI webhook is ready.")

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            update = json.loads(self.rfile.read(length))
            handle_update(update)
        except Exception:
            pass

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
