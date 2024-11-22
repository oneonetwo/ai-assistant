from openai import OpenAI
from openai.types.chat import ChatCompletionChunk
from typing import AsyncGenerator, List, Dict, Any, Generator
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
        self._initialized_sessions = set()  # 新增：跟踪已初始化的会话

    async def initialize_stream(
        self,
        session_id: str,
        messages: List[Dict[str, str]],
        system_prompt: str = "You are a helpful assistant."
    ) -> None:
        """初始化流式响应"""
        try:
            # 构建完整的消息列表
            full_messages = []
            if system_prompt:
                full_messages.append({"role": "system", "content": system_prompt})
            full_messages.extend(messages)
            
            # 验证消息列表
            if len(full_messages) == 1 and full_messages[0]["role"] == "system":
                full_messages.append({"role": "user", "content": "Hello"})

            # 创建流式响应（不使用 await）
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                stream=True,
                temperature=0.7,
                max_tokens=2000,
            )
            
            # 存储流对象并标记会话为已初始化
            self._active_streams[session_id] = {
                "stream": stream,
                "full_text": "",
                "is_active": True,
                "initialized_at": asyncio.get_event_loop().time()  # 记录初始化时间
            }
            self._initialized_sessions.add(session_id)

        except Exception as e:
            app_logger.error(f"初始化流式响应失败: {str(e)}")
            raise APIError(detail=f"初始化流式响应失败: {str(e)}")

    def is_session_initialized(self, session_id: str) -> bool:
        """检查会话是否已初始化"""
        return session_id in self._initialized_sessions

    async def get_stream_response(self, session_id: str) -> AsyncGenerator[str, None]:
        """获取流式响应"""
        try:
            if not self.is_session_initialized(session_id):
                raise APIError(detail="会话未初始化，请先调用初始化接口")

            stream_data = self._active_streams.get(session_id)
            if not stream_data:
                raise APIError(detail="未找到活跃的流式响应")

            # 检查初始化时间
            current_time = asyncio.get_event_loop().time()
            if current_time - stream_data["initialized_at"] > 30:
                await self.cleanup_stream(session_id)
                raise APIError(detail="会话已过期，请重新初始化")

            stream = stream_data["stream"]
            try:
                # 使用异步方式处理流
                for chunk in stream:
                    if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        stream_data["full_text"] += content
                        yield content
                    await asyncio.sleep(0.01)  # 添加小延迟，确保流畅性
            except Exception as e:
                app_logger.error(f"处理流chunk失败: {str(e)}")
                raise

        except Exception as e:
            app_logger.error(f"获取流式响应失败: {str(e)}")
            raise APIError(detail=f"获取流式响应失败: {str(e)}")

    async def cleanup_stream(self, session_id: str) -> None:
        """清理流式响应资源"""
        try:
            if session_id in self._active_streams:
                del self._active_streams[session_id]
            if session_id in self._initialized_sessions:
                self._initialized_sessions.remove(session_id)
        except Exception as e:
            app_logger.error(f"清理流式响应资源失败: {str(e)}")

    def _format_sse_message(self, event_type: str, data: Any) -> str:
        """格式化SSE消息"""
        return f"data: {json.dumps({'type': event_type, 'data': data}, ensure_ascii=False)}\n\n"

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "You are a helpful assistant."
    ) -> str:
        """生成普通响应"""
        try:
            # 构建完整的消息列表
            full_messages = []
            
            # 只有在有其他消息的情况下才添加系统提示
            if system_prompt:
                full_messages.append({"role": "system", "content": system_prompt})
            
            # 添加历史消息
            full_messages.extend(messages)
            
            # 验证消息列表
            if len(full_messages) == 1 and full_messages[0]["role"] == "system":
                # 如果只有系统消息，添加一个默认的用户消息
                full_messages.append({"role": "user", "content": "Hello"})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                temperature=0.7,
                max_tokens=2000,
            )
            
            return response.choices[0].message.content

        except Exception as e:
            app_logger.error(f"生成响应失败: {str(e)}")
            raise APIError(detail=f"AI服务调用失败: {str(e)}")

# 创建全局AI客户端实例
ai_client = AIClient() 