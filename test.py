# import os

# import google.generativeai as genai
# from dotenv import load_dotenv
# from pymongo.mongo_client import MongoClient
# from pymongo.server_api import ServerApi

# load_dotenv()

# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# model = genai.GenerativeModel("gemini-1.5-flash")
# response = model.generate_content("trance this text to bangla:'I eat rice' ")
# print(response.text)


# uri = os.getenv("MONGODB_URI")

# # Create a new client and connect to the server
# client = MongoClient(uri, server_api=ServerApi("1"))

# # Send a ping to confirm a successful connection
# try:
#     client.admin.command("ping")
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)


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


import asyncio


async def test_translation():
    # Sample data
    content = "The sky was painted in hues of orange and pink as the sun set over the horizon. A gentle breeze carried the scent of blooming flowers, signaling the arrival of spring. Birds chirped melodiously, adding a serene background symphony to the evening. Children played joyfully in the park, their laughter echoing in the air. It was a perfect moment of harmony between nature and life."
    language = "Spanish"
    session_id = "679e6e3c-c205-4dff-a2f2-f40a795b0afb"

    # Call the function
    await process_translation(content, language, session_id)

    print(f"Translation process for session ID {session_id} completed.")


# Run the test
asyncio.run(test_translation())
