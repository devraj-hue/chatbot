import os
from flask import Flask, render_template, request, jsonify, session
import openai

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

openai.api_key = os.environ.get("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")

MAX_HISTORY = 20

def ask_openai(prompt, history):
    messages = [{"role": "system", "content": "You are a helpful AI assistant."}]
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": prompt})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages[-10:],  # send last 10 messages for context
            max_tokens=200,
            temperature=0.7,
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("OpenAI API error:", e)
        return "Sorry, I couldn't process your request at the moment."

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    prompt = data.get("prompt", "")
    if not prompt.strip():
        return jsonify({"reply": "Please enter a message."}), 400

    if "history" not in session:
        session["history"] = []
    history = session["history"]
    history.append({"role": "user", "content": prompt})
    ai_reply = ask_openai(prompt, history)
    history.append({"role": "assistant", "content": ai_reply})
    session["history"] = history[-MAX_HISTORY:]  # Limit history length
    return jsonify({"reply": ai_reply})

@app.route("/history", methods=["GET"])
def get_history():
    return jsonify(session.get("history", []))

@app.route("/reset", methods=["POST"])
def reset():
    session["history"] = []
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode)import os
    from flask import Flask, render_template, request, jsonify, session
    import openai