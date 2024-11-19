import uuid
import asyncio
from fastapi import (
    APIRouter,
    BackgroundTasks,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
    File,
)
from datetime import datetime, timezone
from utils.process import process_translation, db_collection

router = APIRouter(prefix="/ws", tags=["utils"])


# WebSocket for real-time status updates
@router.websocket("/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    try:
        session = await db_collection.find_one({"sessionId": session_id})
        if not session or not session.get("filesProcessed"):
            await websocket.send_text("No file found for this session.")
            return
        # Send initial status
        file_path = session["filesProcessed"][-1]["filePath"]

        await websocket.send_text("File received, processing...")

        # Wait for translation to complete
        while True:
            await websocket.send_text("Translating...")
            # Simulate real-time update, process the translation
            await process_translation(file_path, "bangla", session_id)
            await websocket.send_text("Translation complete. Download available.")
            break
    except WebSocketDisconnect:
        print(f"Client {session_id} disconnected")


# File upload endpoint
@router.post("/upload/")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    language: str = "bangla",
):
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
            "filesProcessed": [],
        }
    )

    background_tasks.add_task(process_translation, file_path, language, session_id)

    return {"session_id": session_id, "message": "File uploaded, translation started."}
