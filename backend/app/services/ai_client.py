from openai import OpenAI
from openai.types.chat import ChatCompletionChunk
from typing import AsyncGenerator, List, Dict
from app.core.config import settings
from app.core.logging import app_logger
from app.utils.exceptions import APIError

class AIClient:
    """通义千问API客户端"""
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.QWEN_API_KEY,
            base_url=settings.QWEN_API_URL,
            timeout=settings.QWEN_API_TIMEOUT
        )
        self.model = "qwen-plus"

    async def generate_stream_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "You are a helpful assistant."
    ) -> AsyncGenerator[ChatCompletionChunk, None]:
        """生成流式AI回复"""
        try:
            # 添加系统提示
            full_messages = [
                {"role": "system", "content": system_prompt}
            ] + messages

            # 调用流式API
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                stream=True,
                temperature=0.7,  # 添加温度参数控制随机性
                max_tokens=2000,  # 限制响应长度
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            app_logger.error(f"AI流式响应生成失败: {str(e)}")
            raise APIError(detail=f"AI服务调用失败: {str(e)}")

# 创建全局AI客户端实例
ai_client = AIClient()