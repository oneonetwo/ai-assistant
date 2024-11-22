from openai import OpenAI
from openai.types.chat import ChatCompletionChunk
from typing import AsyncGenerator, List, Dict, Any
from app.core.config import settings
from app.core.logging import app_logger
from app.utils.exceptions import APIError
import json
import asyncio
from contextlib import asynccontextmanager

class AIClient:
    """通义千问API客户端"""
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.QWEN_API_KEY,
            base_url=settings.QWEN_API_URL,
            timeout=settings.QWEN_API_TIMEOUT
        )
        self.model = "qwen-plus"
        # 存储活跃的流式响应
        self._active_streams = {}

    async def initialize_stream(
        self,
        session_id: str,
        messages: List[Dict[str, str]],
        system_prompt: str = "You are a helpful assistant."
    ) -> None:
        """初始化流式响应"""
        try:
            # 添加系统提示
            full_messages = [
                {"role": "system", "content": system_prompt}
            ] + messages

            # 创建流式响应
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                stream=True,
                temperature=0.7,
                max_tokens=2000,
            )
            
            # 存储流对象和相关状态
            self._active_streams[session_id] = {
                "stream": stream,
                "full_text": "",
                "is_active": True
            }

        except Exception as e:
            app_logger.error(f"初始化流式响应失败: {str(e)}")
            raise APIError(detail=f"初始化流式响应失败: {str(e)}")

    async def generate_stream_events(
        self,
        session_id: str
    ) -> AsyncGenerator[str, None]:
        """生成SSE事件流"""
        try:
            if session_id not in self._active_streams:
                raise APIError(detail="未找到活跃的流式响应")

            stream_data = self._active_streams[session_id]
            stream = stream_data["stream"]

            # 发送开始事件
            yield self._format_sse_message("start", None)

            # 处理流式响应
            try:
                for chunk in stream:
                    if not stream_data["is_active"]:
                        break

                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        stream_data["full_text"] += content
                        
                        # 发送chunk事件
                        yield self._format_sse_message("chunk", {
                            "content": content,
                            "full_text": stream_data["full_text"]
                        })
                        
                        # 模拟真实打字效果
                        await asyncio.sleep(0.01)

                # 发送结束事件
                yield self._format_sse_message("end", {
                    "full_text": stream_data["full_text"]
                })

            finally:
                # 清理资源
                await self.cleanup_stream(session_id)

        except Exception as e:
            app_logger.error(f"生成流式响应失败: {str(e)}")
            yield self._format_sse_message("error", {
                "message": f"生成流式响应失败: {str(e)}"
            })
            await self.cleanup_stream(session_id)
            raise APIError(detail=f"生成流式响应失败: {str(e)}")

    async def cleanup_stream(self, session_id: str) -> None:
        """清理流式响应资源"""
        if session_id in self._active_streams:
            self._active_streams[session_id]["is_active"] = False
            del self._active_streams[session_id]

    def _format_sse_message(self, event_type: str, data: Any) -> str:
        """格式化SSE消息"""
        return f"data: {json.dumps({'type': event_type, 'data': data}, ensure_ascii=False)}\n\n"

# 创建全局AI客户端实例
ai_client = AIClient() 