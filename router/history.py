from fastapi import APIRouter
from utils.process import  db_collection

router = APIRouter(prefix="/history", tags=["history"])

def serialize_document(doc):
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

@router.get("/")
async def get_translation_history():
    try:
        history = await db_collection.find().to_list(length=100)
        history = [serialize_document(doc) for doc in history]
        return {"success": True, "history": history}
    except Exception as e:
        return {"success": False, "message": str(e)}
    

