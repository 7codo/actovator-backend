import structlog
from fastapi import APIRouter, Depends, Request, Body

from app.api.v1.dependencies import verify_session_token
from typing import List
from pydantic import BaseModel

# Use structlog's get_logger (structlog is configured in main.py)
logger = structlog.get_logger()

checkpointer_router = APIRouter(prefix="/checkpointer", tags=["checkpointer"])


class DeleteThreadsRequest(BaseModel):
    thread_ids: List[str]


@checkpointer_router.delete("/delete_threads")
async def delete_checkpointer(
    request: Request,
    body: DeleteThreadsRequest = Body(...),
    _=Depends(verify_session_token),
):
    """Delete one or more checkpointer threads."""
    results = {"deleted": [], "failed": []}
    for thread_id in body.thread_ids:
        try:
            checkpointer = request.app.state.checkpointer
            await checkpointer.adelete_thread(thread_id)
            logger.info(f"Successfully deleted checkpointer thread: {thread_id}")
            results["deleted"].append(thread_id)
        except Exception as e:
            logger.error(f"Error deleting checkpointer thread {thread_id}: {e}")
            results["failed"].append({"thread_id": thread_id, "error": str(e)})
    return results
