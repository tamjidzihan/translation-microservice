import uuid
import time
from fastapi import APIRouter, BackgroundTasks, UploadFile, WebSocket, WebSocketDisconnect, File, Form
from fastapi.responses import FileResponse
from datetime import datetime, timezone
from utils.process import process_translation, db_collection

router = APIRouter(prefix="/ws", tags=["WebSocket Operations"])

# File upload endpoint with documentation
@router.post("/upload/", summary="Upload file for translation")
async def upload_file(
    file: UploadFile = File(...),
    language: str = Form(...),
):
    """
    Upload a file for translation to the specified language. 
    A session ID is generated and returned to track the progress.
    """
    session_id = str(uuid.uuid4())
    file_path = f"uploaded_{session_id}.txt"

    # Save the uploaded file temporarily
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Add a placeholder session to MongoDB
    await db_collection.insert_one(
        {
            "sessionId": session_id,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "translated_language": language,
            "filesProcessed": [],
        }
    )

    return {"session_id": session_id, "message": "File uploaded, translation started."}

# WebSocket endpoint for real-time updates with documentation
@router.websocket("/{session_id}", summary="WebSocket for real-time translation status")
async def websocket_endpoint(websocket: WebSocket, session_id: str, background_tasks: BackgroundTasks):
    """
    WebSocket connection to provide real-time updates on file translation progress.
    Once the file is uploaded and translation starts, the WebSocket sends status updates.
    """
    await websocket.accept()
    try:
        session = await db_collection.find_one({"sessionId": session_id})
        if not session:
            await websocket.send_text("No file found for this session.")
            WebSocketDisconnect
            return
        
        language = session["translated_language"]
        file_path = f"uploaded_{session_id}.txt"
        
        time.sleep(3)
        await websocket.send_text("File received, processing...")
        time.sleep(3)

        while True:
            await websocket.send_text("Translating...")
            await process_translation(file_path, language, session_id)
            await websocket.send_text("Translation complete")
            WebSocketDisconnect
            break

    except WebSocketDisconnect:
        print(f"Client {session_id} disconnected")

# Download endpoint for translated files with documentation
@router.get("/{session_id}", summary="Download the translated file")
async def download_file(session_id: str):
    """
    Download the translated file after processing is complete.
    """
    translated_file_path = f"./translated_file/translated_{session_id}.txt"
    try:
        return FileResponse(
            path=translated_file_path,
            media_type="application/octet-stream",
            filename=f"translation_{session_id}.txt",
        )
    except FileNotFoundError:
        return {"error": "File not found. Please try again later."}
