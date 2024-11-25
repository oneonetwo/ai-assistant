from openai import OpenAI, AsyncOpenAI
from openai.types.chat import ChatCompletionChunk
from typing import AsyncGenerator, List, Dict, Any, Generator, Optional
from app.core.config import settings
from app.core.logging import app_logger
from app.utils.exceptions import APIError
from app.utils.cache import cache_manager
import json
import asyncio
from contextlib import asynccontextmanager
from tenacity import retry, stop_after_attempt, wait_exponential

class AIClient:
    """通义千问API客户端增强版"""
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.QWEN_API_KEY,
            base_url=settings.QWEN_API_URL,
            timeout=settings.QWEN_API_TIMEOUT
        )
        self.model = "qwen-plus"
        self._active_streams = {}
        self._initialized_sessions = set()
        self._response_cache = cache_manager.get_cache('ai_responses')

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _make_api_call(
        self,
        messages: List[Dict[str, Any]],
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Any:
        """统一的API调用方法，支持重试"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=stream,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return response
        except Exception as e:
            app_logger.error(f"API调用失败: {str(e)}")
            raise APIError(f"AI服务调用失败: {str(e)}")

    async def _get_cached_response(self, cache_key: str) -> Optional[str]:
        """获取缓存的响应"""
        return await self._response_cache.get(cache_key)

    async def _cache_response(self, cache_key: str, response: str, ttl: int = 3600):
        """缓存响应结果"""
        await self._response_cache.set(cache_key, response, ttl)

    def _generate_cache_key(self, messages: List[Dict[str, Any]], **kwargs) -> str:
        """生成缓存键"""
        # 创建一个包含所有相关参数的字典
        cache_dict = {
            "messages": messages,
            **kwargs
        }
        # 转换为JSON字符串并生成哈希
        return f"ai_response:{hash(json.dumps(cache_dict, sort_keys=True))}"

    async def generate_response(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        use_cache: bool = True,
        **kwargs
    ) -> str:
        """生成AI响应，支持缓存"""
        try:
            # 添加系统提示
            if system_prompt:
                messages.insert(0, {"role": "system", "content": system_prompt})

            # 检查缓存
            if use_cache:
                cache_key = self._generate_cache_key(messages, **kwargs)
                cached_response = await self._get_cached_response(cache_key)
                if cached_response:
                    return cached_response

            # 生成新响应
            response = await self._make_api_call(messages, **kwargs)
            result = response.choices[0].message.content

            # 缓存响应
            if use_cache:
                await self._cache_response(cache_key, result)

            return result

        except Exception as e:
            app_logger.error(f"生成响应失败: {str(e)}")
            raise APIError(f"生成响应失败: {str(e)}")

    async def analyze_document(
        self,
        text: str,
        query: str,
        system_prompt: Optional[str] = None,
        use_cache: bool = True
    ) -> str:
        """分析文档内容，支持长文本分段处理"""
        try:
            # 文本分段处理
            segments = self._split_text(text)
            
            if len(segments) == 1:
                # 单段处理
                return await self._analyze_single_segment(
                    segments[0], query, system_prompt, use_cache
                )
            else:
                # 多段处理
                return await self._analyze_multiple_segments(
                    segments, query, system_prompt, use_cache
                )

        except Exception as e:
            app_logger.error(f"文档分析失败: {str(e)}")
            raise APIError(f"文档分析失败: {str(e)}")

    def _split_text(self, text: str, max_length: int = 4000) -> List[str]:
        """将长文本分段"""
        if len(text) <= max_length:
            return [text]

        segments = []
        current_segment = []
        current_length = 0

        for paragraph in text.split('\n'):
            if current_length + len(paragraph) > max_length:
                if current_segment:
                    segments.append('\n'.join(current_segment))
                    current_segment = []
                    current_length = 0

            current_segment.append(paragraph)
            current_length += len(paragraph) + 1  # +1 for newline

        if current_segment:
            segments.append('\n'.join(current_segment))

        return segments

    async def _analyze_single_segment(
        self,
        text: str,
        query: str,
        system_prompt: Optional[str],
        use_cache: bool
    ) -> str:
        """分析单个文本段落"""
        messages = [
            {"role": "user", "content": f"文档内容：\n{text}\n\n分析要求：{query}"}
        ]
        return await self.generate_response(
            messages, system_prompt, use_cache=use_cache
        )

    async def _analyze_multiple_segments(
        self,
        segments: List[str],
        query: str,
        system_prompt: Optional[str],
        use_cache: bool
    ) -> str:
        """分析多个文本段落并整合结果"""
        # 并行处理所有段落
        segment_analyses = await asyncio.gather(*[
            self._analyze_single_segment(
                segment,
                "请总结这段内容的要点。",
                system_prompt,
                use_cache
            )
            for segment in segments
        ])

        # 整合分析结果
        combined_analysis = "\n\n".join([
            f"第{i+1}部分分析：\n{analysis}"
            for i, analysis in enumerate(segment_analyses)
        ])

        # 生成最终总结
        final_messages = [
            {"role": "user", "content": f"基于以下分段分析结果，{query}\n\n{combined_analysis}"}
        ]
        return await self.generate_response(
            final_messages,
            system_prompt,
            use_cache=use_cache
        )

    async def analyze_image(
        self,
        image_base64: str,
        query: str,
        system_prompt: Optional[str] = None,
        extracted_text: Optional[str] = None,
        use_cache: bool = True
    ) -> str:
        """增强的图片分析功能"""
        try:
            # 构建消息内容
            content = [
                {"type": "text", "text": f"分析要求：{query}"},
                {"type": "image", "image": image_base64}
            ]

            if extracted_text:
                content.append({
                    "type": "text",
                    "text": f"\n提取的文字内容：\n{extracted_text}"
                })

            messages = [{"role": "user", "content": content}]
            
            if system_prompt:
                messages.insert(0, {"role": "system", "content": system_prompt})

            # 检查缓存
            if use_cache:
                cache_key = self._generate_cache_key(messages)
                cached_response = await self._get_cached_response(cache_key)
                if cached_response:
                    return cached_response

            # 生成新响应
            response = await self._make_api_call(messages)
            result = response.choices[0].message.content

            # 缓存响应
            if use_cache:
                await self._cache_response(cache_key, result)

            return result

        except Exception as e:
            app_logger.error(f"图片分析失败: {str(e)}")
            raise APIError(f"图片分析失败: {str(e)}")

# 创建全局AI客户端实例
ai_client = AIClient() 