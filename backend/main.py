
import os
import uuid
import asyncio
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from google import genai
from google.genai import types, errors

from backend.database import (
    initialize_database,
    create_conversation,
    save_message,
    get_messages,
    get_all_conversations,
    delete_conversation,
)


# ==========================================
# 1. ENVIRONMENT CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY missing. Check your root .env file."
    )


# ==========================================
# 2. GEMINI CONFIGURATION
# ==========================================

MODEL_NAME = "gemini-3.5-flash-lite"

client = genai.Client(
    api_key=API_KEY,
    http_options=types.HttpOptions(
        api_version="v1beta",
        timeout=180000,
    ),
)


# ==========================================
# 3. FASTAPI APPLICATION
# ==========================================

app = FastAPI(
    title="Nova AI Chatbot",
    description="Multi-turn AI chatbot with persistent SQLite memory",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# 4. DATABASE INITIALIZATION
# ==========================================

initialize_database()

print("Nova AI SQLite database initialized successfully!")


# ==========================================
# 5. SYSTEM PROMPT
# ==========================================

SYSTEM_PROMPT = """
You are Nova AI, a friendly and intelligent AI assistant.

Your responsibilities:

1. Give clear and accurate answers.
2. Remember information from the current conversation.
3. Answer follow-up questions using previous messages.
4. Explain technical concepts step by step.
5. Be polite, helpful and concise.
6. Never pretend to know information you do not know.
7. Maintain context throughout the conversation.

Always provide helpful and understandable answers.
"""


# ==========================================
# 6. CONFIGURATION
# ==========================================

MAX_HISTORY = 10


# ==========================================
# 7. REQUEST MODEL
# ==========================================

class ChatRequest(BaseModel):

    message: str = Field(
        min_length=1,
        max_length=10000,
    )

    conversation_id: Optional[str] = None


# ==========================================
# 8. RESPONSE MODEL
# ==========================================

class ChatResponse(BaseModel):

    conversation_id: str
    response: str


# ==========================================
# 9. HOME ENDPOINT
# ==========================================

@app.get("/")
async def home():

    return {
        "message": "Welcome to Nova AI Chatbot API",
        "status": "running",
        "model": MODEL_NAME,
        "version": "2.0.0",
    }


# ==========================================
# 10. HEALTH ENDPOINT
# ==========================================

@app.get("/health")
async def health():

    return {
        "status": "healthy",
        "database": "SQLite",
        "model": MODEL_NAME,
    }


# ==========================================
# 11. CHAT ENDPOINT
# ==========================================

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):

    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    # Create or retrieve conversation ID
    conversation_id = (
        request.conversation_id or str(uuid.uuid4())
    )

    if len(conversation_id) > 100:
        raise HTTPException(
            status_code=400,
            detail="Invalid conversation ID.",
        )

    # Retrieve previous conversation from SQLite
    history = get_messages(conversation_id)

    # Prepare current conversation context
    updated_history = history + [
        {
            "role": "user",
            "parts": [{"text": message}],
        }
    ]

    # Limit context to latest 10 messages
    context = updated_history[-MAX_HISTORY:]

    try:

        # Generate response using Gemini
        response = await asyncio.wait_for(

            asyncio.to_thread(
                client.models.generate_content,

                model=MODEL_NAME,

                contents=context,

                config={
                    "system_instruction": SYSTEM_PROMPT,
                    "temperature": 0.7,
                    "max_output_tokens": 1024,
                },
            ),

            timeout=185,
        )

        answer = (response.text or "").strip()

        if not answer:
            raise HTTPException(
                status_code=502,
                detail="Gemini returned an empty response.",
            )

        # Create conversation only after successful response
        create_conversation(conversation_id)

        # Save user message permanently
        save_message(
            conversation_id,
            "user",
            message,
        )

        # Save AI response permanently
        save_message(
            conversation_id,
            "model",
            answer,
        )

        return ChatResponse(
            conversation_id=conversation_id,
            response=answer,
        )

    # ======================================
    # ERROR HANDLING
    # ======================================

    except asyncio.TimeoutError:

        raise HTTPException(
            status_code=504,
            detail="Gemini request timed out. Please try again.",
        )

    except errors.APIError as e:

        print(
            f"Gemini API Error: Code={e.code}, "
            f"Message={e.message}"
        )

        raise HTTPException(
            status_code=502,
            detail=f"Gemini API error (code {e.code}).",
        )

    except HTTPException:
        raise

    except Exception as e:

        print(
            f"Unexpected error: {type(e).__name__}: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again.",
        )


# ==========================================
# 12. GET ALL CONVERSATIONS
# ==========================================

@app.get("/conversations")
async def conversations():

    try:

        all_conversations = get_all_conversations()

        return {
            "conversations": all_conversations,
            "total": len(all_conversations),
        }

    except Exception as e:

        print(f"Conversation retrieval error: {e}")

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve conversations.",
        )


# ==========================================
# 13. GET CONVERSATION MESSAGES
# ==========================================

@app.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):

    if len(conversation_id) > 100:
        raise HTTPException(
            status_code=400,
            detail="Invalid conversation ID.",
        )

    all_conversations = get_all_conversations()

    exists = any(
        item["conversation_id"] == conversation_id
        for item in all_conversations
    )

    if not exists:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    messages = get_messages(conversation_id)

    return {
        "conversation_id": conversation_id,
        "messages": [
            {
                "role": item["role"],
                "content": item["parts"][0]["text"],
            }
            for item in messages
        ],
    }


# ==========================================
# 14. DELETE CONVERSATION
# ==========================================

@app.delete("/conversation/{conversation_id}")
async def clear_conversation(conversation_id: str):

    if len(conversation_id) > 100:
        raise HTTPException(
            status_code=400,
            detail="Invalid conversation ID.",
        )

    all_conversations = get_all_conversations()

    exists = any(
        item["conversation_id"] == conversation_id
        for item in all_conversations
    )

    if not exists:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    delete_conversation(conversation_id)

    return {
        "message": "Conversation deleted successfully.",
        "conversation_id": conversation_id,
    }


# ==========================================
# 15. APPLICATION STATUS
# ==========================================

@app.get("/status")
async def status():

    all_conversations = get_all_conversations()

    return {
        "application": "Nova AI",
        "status": "running",
        "model": MODEL_NAME,
        "database": "SQLite",
        "active_conversations": len(all_conversations),
        "max_history_messages": MAX_HISTORY,
    }
