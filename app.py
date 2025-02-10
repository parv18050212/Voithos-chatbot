from flask import Flask, request, jsonify, render_template
import os
import time
import google.generativeai as genai

# Initialize Flask app
app = Flask(__name__)

# Configure Gemini API key
genai.configure(api_key="AIzaSyDFyMzWGPXK0K6R_nQBEwagQ1ubzZaZH3g")

# Global variables
uploaded_file = None
chat_session = None
document_summary = ""  # Store the career-related summary

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
PDF_FILE_PATH = os.path.join(UPLOAD_FOLDER, "Data.pdf")

def upload_to_gemini():
    """Uploads the PDF file only once and returns the reference."""
    global uploaded_file
    if uploaded_file is None:
        if not os.path.exists(PDF_FILE_PATH):
            raise Exception(f"File {PDF_FILE_PATH} not found!")
        file = genai.upload_file(PDF_FILE_PATH, mime_type="application/pdf")
        print(f"Uploaded file '{file.display_name}' as: {file.uri}")
        uploaded_file = file  # Store reference
    return uploaded_file

def wait_for_file_active(file):
    """Waits until the uploaded file is processed and active."""
    print("Waiting for file processing...")
    while True:
        file_status = genai.get_file(file.name)
        if file_status.state.name == "ACTIVE":
            break
        elif file_status.state.name == "FAILED":
            raise Exception(f"File {file.name} failed to process")
        time.sleep(2)  # Reduced delay
    print("File is ready for use.")

def initialize_chat():
    """Automatically initializes the chat session when the server starts."""
    global chat_session, uploaded_file, document_summary
    try:
        file = upload_to_gemini()  # Upload file once
        wait_for_file_active(file)

        # Configure model
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 30,
                "max_output_tokens": 1024,
                "response_mime_type": "text/plain",
            },
        )

        # Start a persistent chat session
        chat_session = model.start_chat(history=[])

        # Generate a career-related summary of the document
        summary_prompt = "Extract career advice and job recommendations from this document in 3-4 sentences."
        summary_response = chat_session.send_message([uploaded_file, summary_prompt])
        document_summary = summary_response.text.strip()
        print("📄 Career Advice Summary:", document_summary)

    except Exception as e:
        print(f"❌ Chat initialization failed: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global chat_session, uploaded_file, document_summary

    if chat_session is None or uploaded_file is None:
        return jsonify({'error': 'Chat session initialization failed. Try restarting the server.'}), 500

    user_prompt = request.json.get('prompt', None)
    if not user_prompt:
        return jsonify({'error': 'Prompt is required'}), 400

    try:
        # Handle general conversation
        greetings = ["hi", "hello", "hey"]
        if user_prompt.lower() in greetings:
            return jsonify({'response': "Hello! How can I assist you today?"})

        casual_topics = ["weather", "movies", "sports", "news", "music", "hobbies"]
        if any(topic in user_prompt.lower() for topic in casual_topics):
            return jsonify({'response': "I'm here to chat! What's on your mind?"})

        # Detect if the user is asking about career-related topics
        career_keywords = ["career", "job", "resume", "interview", "skills", "work", "profession"]
        if any(keyword in user_prompt.lower() for keyword in career_keywords):
            response_prompt = f"Based on this career advice summary: {document_summary}, answer this question: {user_prompt}"
            response = chat_session.send_message(response_prompt)
            return jsonify({'response': f"<pre>{response.text}</pre>"})

        # If the input doesn't match any category, respond as a friendly chatbot
        return jsonify({'response': "Please Reframe your question."})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    initialize_chat()  # 🚀 Auto-start chat session on server start
    app.run(debug=True)
