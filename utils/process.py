import os
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Replace with your MongoDB connection string
MONGO_URI = os.getenv("MONGODB_URI")

# Replace with your GEMINI connection string
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize MongoDB client
client = AsyncIOMotorClient(MONGO_URI)

# Access the desired database and collection
db = client["translation-microservice"]  # database name
db_collection = db["history"]  # Collection to store sessions


async def translate_text(content: str, language: str) -> str:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(f"Translate this text to {language}: {content}")

    # Access the response content properly
    return response.text


async def process_translation(content: str, language: str, session_id: str):
    try:
        # Request translation from LLM
        translated = await translate_text(content, language)

        # Prepare file object
        file_object = {
            "fileName": f"translated_{session_id}.txt",
            "content": translated,  # Store content instead of saving file
            "processedAt": datetime.now(timezone.utc).isoformat(),
        }

        # Check if session exists in MongoDB
        session = await db_collection.find_one({"sessionId": session_id})

        if session:
            # Update existing session
            await db_collection.update_one(
                {"sessionId": session_id}, {"$push": {"filesProcessed": file_object}}
            )
        else:
            # Create new session
            await db_collection.insert_one(
                {
                    "sessionId": session_id,
                    "createdAt": datetime.now(timezone.utc).isoformat(),
                    "filesProcessed": [file_object],
                }
            )

    except Exception as e:
        error_message = f"Error during translation: {e}"
        # Store error result in MongoDB
        file_object = {
            "fileName": f"translated_{session_id}.txt",
            "content": error_message,
            "processedAt": datetime.now(timezone.utc).isoformat(),
        }

        # Check if session exists in MongoDB
        session = await db_collection.find_one({"sessionId": session_id})

        if session:
            # Update existing session
            await db_collection.update_one(
                {"sessionId": session_id}, {"$push": {"filesProcessed": file_object}}
            )
        else:
            # Create new session
            await db_collection.insert_one(
                {
                    "sessionId": session_id,
                    "createdAt": datetime.now(timezone.utc).isoformat(),
                    "filesProcessed": [file_object],
                }
            )
