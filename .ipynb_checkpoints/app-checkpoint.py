from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Route for the chatbot webpage
@app.route('/')
def index():
    return render_template('index.html')

# Route for handling chatbot messages
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data['message']
    api_token = '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'
    try:
        response = requests.post(
            'https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill',
            headers={'Authorization': f'Bearer {api_token}'},
            json={"inputs": user_message}
        )

        # Check if the response was successful
        if response.status_code == 200:
            # Access the first item in the list, then the 'generated_text' key
            bot_reply = response.json()[0]['generated_text']
            return jsonify({'reply': bot_reply})
        else:
            return jsonify({'error': f'Error {response.status_code}: {response.text}'})

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == "__main__":
    app.run(debug=True)
