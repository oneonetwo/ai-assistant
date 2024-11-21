from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.models.schemas import ChatRequest
from app.services import chat as chat_service
import json
import asyncio

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/{session_id}/stream")
async def stream_chat(
    session_id: str,
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """处理流式聊天请求，类似ChatGPT的实现"""
    
    async def event_generator():
        try:
            # 发送开始标记
            yield "data: {\"type\":\"start\"}\n\n"
            
            full_text = ""
            async for chunk in chat_service.process_stream_chat(
                db,
                session_id,
                request.message
            ):
                # 累积完整文本
                full_text += chunk.get("chunk", "")
                
                # 构造类似ChatGPT的响应格式
                response = {
                    "type": "chunk",
                    "data": {
                        "content": chunk.get("chunk", ""),
                        "session_id": session_id
                    }
                }
                yield f"data: {json.dumps(response, ensure_ascii=False)}\n\n"
                
                # 模拟真实打字效果
                await asyncio.sleep(0.01)
            
            # 发送完成标记
            completion = {
                "type": "end",
                "data": {
                    "session_id": session_id,
                    "full_text": full_text
                }
            }
            yield f"data: {json.dumps(completion, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            # 发送错误信息
            error_response = {
                "type": "error",
                "data": {
                    "message": str(e)
                }
            }
            yield f"data: {json.dumps(error_response, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    ) 