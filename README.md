AI-Based Minutes of Meeting (MoM) Generator

Powered by Whisper + NLP + Translation
Overview

The AI-Based Minutes of Meeting Generator is an intelligent web application that automatically generates meeting summaries and structured minutes of meetings using speech recognition, natural language processing (NLP), and translation models.

Users can:

Record or upload meeting audio
Or directly paste a meeting transcript
  The system then analyzes the content and produces concise, well-structured meeting minutes with objectives, key points, and action items.

Features

Automatic Speech Recognition (ASR)

* Uses OpenAI Whisper or equivalent models to transcribe speech into text.

Natural Language Processing (NLP)

Extracts key insights, decisions, and action items from the transcript.

Translation Support

 Supports multiple languages for transcription and summary generation.

User-Friendly UI

Built with a simple, responsive design for smooth user interaction.

Multiple Input Options

 🎙️ Record audio live
 📂 Upload existing audio
📝 Paste a transcript manually

Instant MoM Generation

 Automatically structures the minutes in a readable, downloadable format.

🛠️ Tech Stack

| Layer              | Technologies                                             |
| ------------------ | -------------------------------------------------------- |
| Frontend       | HTML, CSS, JavaScript, Bootstrap                         |
| Backend        | Flask (Python), Flask-SocketIO                           |
| AI/ML          | Whisper (Speech-to-Text), NLP-based summarization models |
| Database       | SQLite (for user/session management)                     |
| Authentication | JWT + Flask-Bcrypt                                       |
| Hosting        | GitHub + Flask server / local deployment                 |

⚙️ Setup & Installation

Prerequisites

* Python 3.10+
* pip
* Virtual Environment (recommended)

Steps

bash
# 1. Clone this repository
git clone https://github.com/Di-ya1103/gsfc_mom.git
cd gsfc_mom

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # For Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the Flask app
python app.py

# 5. Access the app
http://127.0.0.1:5000/


 Folder Structure

gsfc_mom/
│
├── app.py                 # Main Flask backend
├── static/                # CSS, JS, and images
├── templates/             # HTML templates (UI pages)
├── requirements.txt       # Python dependencies
├── database/              # SQLite DB (if applicable)
└── README.md              # Project documentation

💡 Future Enhancements

* Integrate AI-powered Action Item Tracker
* Add PDF/Docx export for generated MoMs
* Real-time multi-speaker identification
* Integration with Google Calendar / Outlook
* Live translation during meetings




Would you like me to make this `README.md` include a **“Demo” section** (with buttons or GIF placeholders) for when you later host your app online (e.g., via Render or PythonAnywhere)?
