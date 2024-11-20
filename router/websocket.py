import time
import uuid
from datetime import datetime, timezone
from io import BytesIO

from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    Form,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import StreamingResponse

from utils.process import db_collection, process_translation

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

    # Read the file content directly without saving it
    content = (await file.read()).decode("utf-8")

    # Add a placeholder session to MongoDB with the file content
    await db_collection.insert_one(
        {
            "sessionId": session_id,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "translated_language": language,
            "originalFile": {
                "fileName": file.filename,
                "content": content,
                "uploadedAt": datetime.now(timezone.utc).isoformat(),
            },
            "filesProcessed": [],
        }
    )

    return {
        "session_id": session_id,
        "message": "File content uploaded, translation started.",
    }


# WebSocket endpoint for real-time updates with documentation
@router.websocket("/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket, session_id: str, background_tasks: BackgroundTasks
):
    """
    WebSocket connection to provide real-time updates on file translation progress.
    Once the file is uploaded and translation starts, the WebSocket sends status updates.
    """
    await websocket.accept()
    try:
        # Retrieve session details from MongoDB
        session = await db_collection.find_one({"sessionId": session_id})
        if not session:
            await websocket.send_text("No file found for this session.")
            await websocket.close()
            return

        # Extract necessary details
        language = session["translated_language"]
        file_data = session.get("originalFile", {})
        content = file_data.get("content", None)

        if not content:
            await websocket.send_text("No file content found for this session.")
            await websocket.close()
            return

        await websocket.send_text("File received, processing...")
        time.sleep(3)

        # Call process_translation with file content
        await websocket.send_text("Translating...")
        background_tasks.add_task(process_translation, content, language, session_id)
        time.sleep(10)
        # await process_translation(content, language, session_id)
        await websocket.send_text("complete")

        await websocket.close()
    except WebSocketDisconnect:
        print(f"Client {session_id} disconnected")


@router.get("/download/{session_id}", summary="Download the translated file")
async def download_file(session_id: str):
    """
    Download the translated file after processing is complete.
    """
    # Retrieve session from MongoDB
    session = await db_collection.find_one({"sessionId": session_id})

    if not session or not session.get("filesProcessed"):
        return {"error": "No processed files found for this session."}

    # Fetch the last processed file (you can modify this for multiple files)
    file_object = session["filesProcessed"][-1]
    content = file_object.get("content", "")
    file_name = file_object.get("fileName", "translated_file.txt")

    if not content:
        return {"error": "No content found for the translated file."}

    # Use StreamingResponse to return the content
    content_stream = BytesIO(content.encode("utf-8"))
    response = StreamingResponse(content_stream, media_type="application/octet-stream")
    response.headers["Content-Disposition"] = f'attachment; filename="{file_name}"'
    return response
