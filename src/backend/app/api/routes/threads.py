
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.thread_service import ThreadService


thread_service = ThreadService()
router = APIRouter()

class ThreadUpdateRequest(BaseModel):
    thread_id: str
    thread_title: str

@router.get("/user/threads")
def get_user_threads():
    return thread_service.get_user_threads(user_id='0x1234')

@router.get("/thread")
def get_thread_content(thread_id: str):
    return thread_service.get_thread(thread_id=thread_id)

@router.get("/thread/messages")
def get_thread_messages(thread_id: str):
    return thread_service.get_thread_messages(thread_id=thread_id)

@router.delete("/thread")
def delete_thread(thread_id: str):
    return thread_service.delete_thread(thread_id=thread_id)

@router.post("/thread/update/title")
def update_thread_title(request: ThreadUpdateRequest):
    if not request.thread_title.strip():
        raise HTTPException(status_code=400, detail="Thread title cannot be empty")
    thread_title_trunc = request.thread_title[:50] + "..."
    return thread_service.update_thread_title(thread_id=request.thread_id, title=thread_title_trunc)