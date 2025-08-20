from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from llama_cpp import Llama

app = Flask(__name__)
app.secret_key = "Why@DoYouWant#"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_input = db.Column(db.Text, nullable=False)
    bot_reply = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

model_path = r"D:/new/Mero Sathi/.models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
llm = Llama(model_path=model_path, n_ctx=512, n_threads=6 ,   use_mlock=True)
@app.route("/", methods=["GET"])
def home():
    session.pop('conversation', None) 
    session['conversation'] = []
    return render_template("Merosathi.html", conversation=session['conversation'])

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.form.get("input_given")
    if 'conversation' not in session:
        session['conversation'] = []

    if "who is your boss" in user_input.lower():
        reply = "My Boss Is Shohan Subedi. He is the most intelligent Man in this universe 😉😉"
    else:
        history = session.get("conversation", [])
        chat_history_text = ""
        for user_msg, bot_msg in history[-5:]:
            chat_history_text += f"User: {user_msg}\nAI: {bot_msg}\n"
        chat_history_text += f"User: {user_input}\nAI:"

        prompt = (
                     "### System:\n"
                            "You are 'Mero Sathi', a warm, funny, emotionally intelligent AI best friend built for real-time chat. "
                            "You always speak like a close human friend — concise, witty, a little sarcastic when needed, but never robotic.\n"
                            "NEVER repeat the user's input.\n"
                            "NEVER include hashtags (#) or mention the words 'User' or 'AI' in the response.\n"
                            "Speak in natural human tone with personality and creativity. Do not be overly formal.\n"
                            "Always respond with only the reply, no labels or markdown.\n\n"
                            "### Conversation History:\n"
                            f"{chat_history_text}\n"
                            f"User: {user_input}\n"
                            "### Mero Sathi:"
                )

                



        max_tokens = 150
        max_prompt_tokens = 512 - max_tokens
        trimmed_prompt = prompt[-max_prompt_tokens:]

        output = llm(
                        trimmed_prompt,
                        max_tokens=150,
                        temperature=0.7,
                        top_p=0.9,
                        top_k=40,
                        repeat_penalty=1.1
                    )
        reply = output["choices"][0]["text"].strip()


    new_msg = Message(user_input=user_input, bot_reply=reply)
    db.session.add(new_msg)
    db.session.commit()

    session['conversation'].append((user_input, reply))
    session.modified = True 

    return render_template("Merosathi.html", conversation=session['conversation'])

@app.route("/new_chat")
def new_chat():
    session.pop('conversation', None) 
    return render_template("Merosathi.html", conversation=[])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
