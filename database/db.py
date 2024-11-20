from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# Replace with your MongoDB connection string
MONGO_URI = os.getenv("MONGODB_URI")

# Initialize MongoDB client
client = MongoClient(MONGO_URI)

# Access the desired database and collection
db = client["mydatabase"]  # database name
history_collection = db["history"]  # Collection to store sessions
