import os
import uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Replace with your MongoDB connection string
MONGO_URI = os.getenv("MONGODB_URI")

# Initialize MongoDB client
client = AsyncIOMotorClient(MONGO_URI)

# Access the desired database and collection
db = client["translation-microservice"]  # database name
db_collection = db["history"]  # Collection to store sessions


async def translate_text(content: str, language: str) -> str:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(f"Translate this text to {language}: {content}")

    # Access the response content properly
    return response.text


async def process_translation(file_path: str, language: str, session_id: str):
    try:
        # Read file content
        with open(file_path, "r") as file:
            content = file.read()

        # Request translation from LLM
        translated = await translate_text(content, language)

        # Save translated file
        translated_path = f"translated_{session_id}.txt"
        with open(translated_path, "w", encoding="utf-8") as file:
            file.write(translated)

        # Prepare file object
        file_object = {
            "fileName": os.path.basename(file_path),
            "filePath": file_path,
            "processedAt": datetime.now(timezone.utc).isoformat(),
            "result": translated,
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
        print(error_message)

        # Store error result in MongoDB
        file_object = {
            "fileName": os.path.basename(file_path),
            "filePath": file_path,
            "processedAt": datetime.now(timezone.utc).isoformat(),
            "result": error_message,
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
