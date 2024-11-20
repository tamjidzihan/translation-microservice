from fastapi import APIRouter
from utils.process import db_collection

router = APIRouter(prefix="/history", tags=["History Operations"])

def serialize_document(doc):
    """
    Helper function to serialize MongoDB document.
    """
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

@router.get("/", summary="Retrieve translation history")
async def get_translation_history():
    """
    Get the list of all translation sessions and their history.
    Returns metadata about the files that were processed.
    """
    try:
        history = await db_collection.find().to_list(length=100)
        history = [serialize_document(doc) for doc in history]
        return {"success": True, "history": history}
    except Exception as e:
        return {"success": False, "message": str(e)}
