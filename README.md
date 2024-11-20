# Translation Microservice

A robust, real-time translation microservice developed using FastAPI, WebSockets, and the Google Gemini API for seamless multilingual communication.

## Features
- **Real-time Translation**: Utilizes WebSockets for instant message translation.
- **Google Gemini API Integration**: Leverages advanced translation capabilities for high accuracy.
- **Scalability**: Designed with modularity for integration into larger applications.
- **File Upload and Translation**: Upload a file, and the microservice will translate its contents to the desired language.
- **Translation History**: Keeps a history of all translation sessions and processed files.

## Tech Stack
- **FastAPI**: A modern, high-performance web framework for Python.
- **WebSockets**: Provides real-time communication between clients and the server.
- **Google Gemini API**: For state-of-the-art translation services.
- **MongoDB**: NoSQL database to store translation history and session details.
- **Motor**: MongoDB asynchronous driver for Python.
- **Uvicorn**: ASGI server for serving FastAPI applications.

## Prerequisites
Make sure you have the following installed:
- **Python 3.7+**
- **MongoDB** (local or cloud, such as MongoDB Atlas)
- **Google Gemini API key** (for translation)
- **Git**

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/translation-microservice.git
   cd translation-microservice
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # For Linux/macOS
   venv\Scripts\activate  # For Windows
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
- Create a .env file in the root directory of the project.
- Add the following environment variables to the .env file:
   ```bash
   MONGODB_URI=mongodb://your_mongo_db_connection_string
   GEMINI_API_KEY=your_google_gemini_api_key
   ```
Replace your_mongo_db_connection_string with your MongoDB URI (local or from MongoDB Atlas) and your_google_gemini_api_key with your Gemini API key.

5. Start the FastAPI server using Uvicorn:
   ```bash
   uvicorn main:app --reload
   ```
- Access the Swagger UI at http://127.0.0.1:8000/docs to interact with the API, test endpoints, and view API documentation.
- You can also access the frontend HTML form at http://127.0.0.1:8000/ to upload files and initiate translation.


You can copy and paste this entire block into a file named `README.md` in your project directory. This file includes all the necessary installation, deployment, and usage instructions for your Translation Microservice.
