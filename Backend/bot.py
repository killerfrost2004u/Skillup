from flask import Flask, request, jsonify
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # يسمح لأي origin بالوصول

# حطي مفتاحك هنا
openai.api_key = "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"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Please type a message."})

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response.choices[0].message.content
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
