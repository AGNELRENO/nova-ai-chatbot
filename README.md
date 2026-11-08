# 🚀 Nova AI – Multi-Turn AI Chatbot

Nova AI is an intelligent conversational chatbot powered by Google's Gemini API. It maintains conversation context, stores chat history using SQLite, and provides a modern React-based user interface.

## ✨ Features

- AI-powered conversations using Google Gemini.
- Multi-turn conversation memory.
- Persistent chat history using SQLite.
- Create, view, switch and delete conversations.
- Context window management using the latest 10 messages.
- Modern React frontend with a dark-themed interface.
- Backend error handling and request timeouts.
- Secure API key management using environment variables.

## 🛠️ Technologies Used

| Component | Technology |
|---|---|
| Frontend | React.js, Vite |
| Backend | Python, FastAPI |
| AI Model | Gemini (`gemini-3.5-flash-lite`) |
| Database | SQLite |
| AI Integration | Google GenAI SDK |
| Styling | CSS |
| Icons | Lucide React |

## 📁 Project Structure

```text
nova-ai-chatbot/
├── backend/
│   ├── main.py
│   ├── database.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   └── index.html
├── .env.example
├── .gitignore
└── README.md
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/AGNELRENO/nova-ai-chatbot.git
cd nova-ai-chatbot
```

### 2. Configure environment variables

Create a `.env` file in the project root.

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Never upload your actual `.env` file or API key to GitHub.

### 3. Set up the Python backend

```powershell
python -m venv backend/.venv
.\backend\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

Start the backend from the project root:

```powershell
python -m uvicorn backend.main:app --reload
```

Backend URL: `http://127.0.0.1:8000`

API documentation: `http://127.0.0.1:8000/docs`

### 4. Set up the React frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL displayed by Vite.

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Welcome message |
| GET | `/health` | Health check |
| POST | `/chat` | Send messages to Nova AI |
| GET | `/conversations` | Retrieve chat history |
| GET | `/conversation/{conversation_id}` | Retrieve messages |
| DELETE | `/conversation/{conversation_id}` | Delete a conversation |
| GET | `/status` | Application status |

## 🧠 Conversation Memory

1. Receive the user's message.
2. Retrieve previous messages from SQLite.
3. Send the latest 10 messages as context to Gemini.
4. Generate an AI response.
5. Save both user and assistant messages.
6. Return the response to the frontend.

## 🗄️ Database Design

**Conversations table**
- conversation_id
- title
- created_at
- updated_at

**Messages table**
- id
- conversation_id
- role
- content
- created_at

## 🧪 Testing

The following functionality has been tested:

- Gemini API connectivity.
- Multi-turn conversation memory.
- SQLite persistent storage.
- Conversation retrieval.
- New conversation creation.
- Conversation deletion.
- Browser refresh persistence.
- Backend error handling and recovery.

## 🔐 Security

- API keys stored in environment variables.
- `.env` excluded through `.gitignore`.
- Input validation using Pydantic.
- API errors and timeouts handled by the backend.

## 🚀 Future Improvements

- User authentication.
- Multiple user accounts.
- Conversation search.
- Streaming AI responses.
- Cloud database integration.
- Production deployment.
- Advanced conversation summarization.

## 👨‍💻 Author

**Agnel Reno**

GitHub: [@AGNELRENO](https://github.com/AGNELRENO)

GitHub Profile: https://github.com/AGNELRENO

Project Repository: https://github.com/AGNELRENO/nova-ai-chatbot

---

⭐ If you find this project useful, consider giving it a star!

**Nova AI – Intelligent Conversations, Persistent Memory.**