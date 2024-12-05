from flask import Flask, request, jsonify, render_template
import os
import time
import google.generativeai as genai

# Initialize Flask app
app = Flask(__name__)

# Configure the Gemini API key
genai.configure(api_key='AIzaSyDN7IK2C2tsIbBfE2eeVZEtRWogORED2AI')

def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini."""
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

def wait_for_files_active(files):
    """Waits for the given files to be active."""
    print("Waiting for file processing...")
    for name in (file.name for file in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(10)
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")
    print("...all files ready")
    print()

# Route to serve the frontend page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle the file processing and chat generation
@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    user_prompt = request.json.get('prompt', None)
    if not user_prompt:
        return jsonify({'error': 'Prompt is required'}), 400

    try:
        # Upload the PDF file to Gemini
        file = upload_to_gemini("uploads/Data.pdf", mime_type="application/pdf")
        
        # Wait for the file to be processed and ready for use
        wait_for_files_active([file])

        # Create the model
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
        )

        # Start chat with the uploaded file and user prompt
        chat_session = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        file,
                        user_prompt,
                    ],
                },
                {
                    "role": "model",
                    "parts": [
                        "Model response based on the provided PDF and prompt goes here.",
                    ],
                },
            ]
        )

        response = chat_session.send_message(user_prompt)

        return jsonify({'response': response.text})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
