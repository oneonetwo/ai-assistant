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
import redis.asyncio as redis
import uuid

# 初始化 Redis 客户端
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True
)

class AIClient:
    """通义千问API客户端增强版"""
    def __init__(self):
        # API客户端配置
        self.client = AsyncOpenAI(
            api_key=settings.QWEN_API_KEY,
            base_url=settings.QWEN_API_URL,
            timeout=settings.QWEN_API_TIMEOUT
        )
        self.model = "qwen-max"
        self.vision_model = "qwen-vl-plus"
        self.audio_model = "qwen-audio-turbo"
        
        # 重试配置
        self.max_retries = 3
        self.retry_delay = 1  # 基础重试延迟（秒）
        
        # 会话和缓存管理
        self._active_streams = {}
        self._analysis_sessions = {}  # 添加分析会话字典
        self._current_analysis_session_id = None  # 添加当前分析会话ID
        self._response_cache = cache_manager.get_cache('ai_responses')
        self.initialized_sessions = set()
        
        # API配置
        self.api_key = settings.QWEN_API_KEY
        self.api_url = settings.QWEN_API_URL
        self.api_timeout = settings.QWEN_API_TIMEOUT
        
        # Redis客户端
        self.redis_client = redis_client
        
        # 会话存储
        self.sessions = {}
        self.analysis_sessions = {}  # 分析会话存储
        self._analysis_sessions = {}
        self._current_analysis_session_id = None

    def is_session_initialized(self, session_id: str) -> bool:
        """检查会话是否已初始化"""
        return session_id in self.initialized_sessions

    async def init_session(self, session_id: str):
        """初始化会话"""
        if not self.is_session_initialized(session_id):
            # 可以在这里添加任何必要的会话初始化逻辑
            self.initialized_sessions.add(session_id)

    async def _make_api_call(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Any:
        """进行API调用"""
        try:
            # 移除不支持的参数
            api_params = {
                "model": model,
                "messages": messages,
                "stream": stream,
                "temperature": temperature,
            }
            
            # 只在有值时添加max_tokens参数
            if max_tokens is not None:
                api_params["max_tokens"] = max_tokens
                
            # 添加其他支持的参数
            for key, value in kwargs.items():
                if key not in ['session_id']:  # 排除不支持的参数
                    api_params[key] = value

            try:
                response = await self.client.chat.completions.create(**api_params)
                return response
            except Exception as e:
                app_logger.error(f"API调用出错: {str(e)}")
                raise APIError(f"API调用出错: {str(e)}")
                
        except Exception as e:
            app_logger.error(f"API调用失败: {str(e)}")
            raise APIError(f"API调用失败: {str(e)}")

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
            {"role": "user", "content": f"基于以下果，{query}\n\n{combined_analysis}"}
        ]
        return await self.generate_response(
            final_messages,
            system_prompt,
            use_cache=use_cache
        )

    async def analyze_image(
        self,
        image_url: str,
        query: str,
        system_prompt: Optional[str] = None,
        extracted_text: Optional[str] = None,
        use_cache: bool = True
    ) -> str:
        """增强的图片分析功能"""
        try:
            # 构建消息内容
            content = [
                {"type": "text", "text": query},
                {"type": "image_url", "image_url": {"url": image_url}}
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

            # 使用 qwen-vl-plus 模型，通过参数传递而不是kwargs
            response = await self._make_api_call(
                messages=messages,
                model=self.vision_model  # 使用类属性中定义的视觉模型
            )
            result = response.choices[0].message.content

            # 缓存响应
            if use_cache:
                await self._cache_response(cache_key, result)

            return result

        except Exception as e:
            app_logger.error(f"图片分析失败: {str(e)}")
            raise APIError(f"图片分析失败: {str(e)}")

    async def initialize_stream(self, session_id: str, messages: List[Dict[str, str]], model: Optional[str] = None):
        """初始化流式响应"""
        try:
            # 清理现有的流
            await self.cleanup_stream(session_id)
            
            # 创建新的流式响应
            stream = await self._make_api_call(
                messages=messages,
                model=model or self.model,  # 使用传入的model或默认model
                stream=True
            )
            
            # 存储流
            self._active_streams[session_id] = stream
            
        except Exception as e:
            app_logger.error(f"初始化流式响应失败: {str(e)}")
            raise APIError(f"初始化流式响应失败: {str(e)}")

    async def get_stream_response(self, session_id: str) -> AsyncGenerator[str, None]:
        """获取流式响应"""
        try:
            stream = self._active_streams.get(session_id)
            if not stream:
                raise APIError("未找到活动的流式响应")
            
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                
        except Exception as e:
            app_logger.error(f"获取流式响应失败: {str(e)}")
            raise APIError(f"获取流式响应失败: {str(e)}")
        
    async def cleanup_stream(self, session_id: str):
        """清理指定会话的流"""
        if session_id in self._active_streams:
            # 从活动流中移除
            del self._active_streams[session_id]

    async def analyze_image_stream(
        self,
        image_url: str,
        query: str,
        system_prompt: Optional[str] = None,
        extracted_text: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """流式图片分析功能"""
        try:
            content = [
                {"type": "text", "text": query},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]

            if extracted_text:
                content.append({
                    "type": "text",
                    "text": f"\n提取的文字内容：\n{extracted_text}"
                })

            messages = [{"role": "user", "content": content}]
            
            if system_prompt:
                messages.insert(0, {"role": "system", "content": system_prompt})

            # 使用流式响应
            stream = await self._make_api_call(
                messages=messages,
                model=self.vision_model,
                stream=True
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            app_logger.error(f"流式图片分析失败: {str(e)}")
            raise APIError(f"流式图片分析失败: {str(e)}")

    async def analyze_file_stream(
        self,
        file_id: str,
        query: str,
        file_type: str,
        system_prompt: Optional[str] = None,
        extracted_text: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """流式文件分析功能"""
        try:
            content = []
            
            if file_type == "image":
                content = [
                    {"type": "text", "text": query},
                    {"type": "image_url", "image_url": {"url": file_id}}
                ]
            else:
                content = [{"type": "text", "text": f"{query}\n\n文档内容：{extracted_text}"}]

            messages = [{"role": "user", "content": content}]
            
            if system_prompt:
                messages.insert(0, {"role": "system", "content": system_prompt})

            # 使用流式响应
            stream = await self._make_api_call(
                messages=messages,
                model=self.vision_model if file_type == "image" else self.model,
                stream=True
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            app_logger.error(f"流式文件分析失败: {str(e)}")
            raise APIError(f"流式文件分析失败: {str(e)}")

    async def initialize_image_stream(
        self, 
        session_id: str, 
        messages: List[Dict[str, str]], 
        image_data: str
    ):
        """初始化图片流式响应"""
        try:
            # 清理现有的流
            await self.cleanup_stream(session_id)
            
            # 创建新的流式响应
            stream = await self._make_api_call(
                messages=messages,
                model=self.vision_model,
                stream=True
            )
            
            # 存储流
            self._active_streams[session_id] = stream
            
        except Exception as e:
            app_logger.error(f"初始化图片流式响应失败: {str(e)}")
            raise APIError(f"初始化图片流式响应失败: {str(e)}")

    async def get_stream(self, session_id: str):
        """获取流式响应"""
        try:
            stream = self._active_streams.get(session_id)
            if not stream:
                raise APIError("未找到活动的流式响应")

            async for chunk in stream:
                if hasattr(chunk.choices[0].delta, "content"):
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content

            # 清理流
            await self.cleanup_stream(session_id)

        except Exception as e:
            app_logger.error(f"获流式响应失败: {str(e)}")
            raise APIError(f"获取流式响应失败: {str(e)}")

    async def initialize_analysis_stream(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """初始化消息分析流"""
        try:
            # 生成新的会话ID
            analysis_session_id = str(uuid.uuid4())
            
            
            # 创建流式响应
            stream = await self._make_api_call(
                messages=messages,
                model=self.model,
                stream=True,
                temperature=temperature,
                max_tokens=max_tokens,
                **{k: v for k, v in kwargs.items() if k != 'session_id'}
            )
            
            # 存储会话信息
            self._analysis_sessions[analysis_session_id] = {
                'stream': stream,
                'messages': messages
            }
            self._current_analysis_session_id = analysis_session_id
            
            # 将会话ID存储到Redis中，设置过期时间为5分钟
            await self.redis_client.set(
                f"analysis_session:{analysis_session_id}",
                "active",
                ex=300
            )
            
            app_logger.info(f"成功初始化分析流，会话ID: {analysis_session_id}")
            return analysis_session_id
            
        except Exception as e:
            app_logger.error(f"初始化分析流失败: {str(e)}")
            raise APIError(f"初始化分析流失败: {str(e)}")

    async def get_analysis_stream(self, analysis_session_id: str) -> AsyncGenerator[str, None]:
        """获取分析流式响应"""
        try:
            # 检查会话是否存在于Redis中
            is_active = await self.redis_client.get(f"analysis_session:{analysis_session_id}")
            if not is_active:
                raise APIError("分析会话不存在或已过期")

            session_data = self._analysis_sessions.get(analysis_session_id)
            if not session_data:
                raise APIError("分析会话不存在")

            stream = session_data['stream']
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            app_logger.error(f"获取分析流失败: {str(e)}")
            raise APIError(f"获取分析流失败: {str(e)}")
        finally:
            # 清理会话
            if analysis_session_id in self._analysis_sessions:
                del self._analysis_sessions[analysis_session_id]
                await self.redis_client.delete(f"analysis_session:{analysis_session_id}")

    async def get_current_analysis_session_id(self) -> Optional[str]:
        """获取当前分析会话ID"""
        app_logger.debug(f"当前分析会话ID: {self._current_analysis_session_id}")
        return self._current_analysis_session_id

    async def cleanup_analysis_session(self, analysis_session_id: str):
        """清理分析会话"""
        if analysis_session_id in self.analysis_sessions:
            del self.analysis_sessions[analysis_session_id]

    async def is_session_active(self, session_id: str) -> bool:
        """检查会话是否活跃
        
        Args:
            session_id: 会话ID
        
        Returns:
            bool: 会话是否活跃
        """
        try:
            # 从Redis中检查会话状态
            is_active = await self.redis_client.get(f"analysis_session:{session_id}")
            return bool(is_active)
        except Exception as e:
            app_logger.error(f"检查会话状态失败: {str(e)}")
            return False

    async def analyze_audio(
        self,
        audio_url: str,
        query: str,
        system_prompt: Optional[str] = None,
        timeout: int = 180
    ) -> str:
        """Analyze audio content using Qwen Audio model with timeout control"""
        try:
            # 按照测试文件的格式构建消息
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"audio": audio_url},
                        {"text": query}
                    ]
                }
            ]

            async def _make_audio_call():
                import dashscope
                response = await asyncio.to_thread(
                    dashscope.MultiModalConversation.call,
                    api_key=self.api_key,
                    model=self.audio_model,
                    messages=messages
                )
                return response

            try:
                app_logger.info("Starting audio analysis...")
                response = await asyncio.wait_for(_make_audio_call(), timeout=timeout)
                
                if hasattr(response, 'status_code') and response.status_code == 200:
                    if hasattr(response, 'output') and hasattr(response.output, 'choices'):
                        content = response.output.choices[0].message.content
                        # 处理返回的内容
                        if isinstance(content, list):
                            # 如果是列表，提取text字段
                            for item in content:
                                if isinstance(item, dict) and 'text' in item:
                                    return item['text']
                        elif isinstance(content, dict) and 'text' in content:
                            # 如果是字典，直接提取text字段
                            return content['text']
                        else:
                            # 如果是字符串，直接返回
                            return str(content)
                    else:
                        raise APIError("Invalid response structure: missing output or choices")
                else:
                    error_msg = getattr(response, 'message', 'Unknown error')
                    app_logger.error(f"Audio analysis failed: {error_msg}")
                    raise APIError(f"Audio analysis failed: {error_msg}")
                    
            except asyncio.TimeoutError:
                app_logger.error(f"Audio analysis timeout after {timeout} seconds")
                raise APIError(f"Audio analysis timeout after {timeout} seconds")

        except Exception as e:
            app_logger.error(f"Audio analysis failed: {str(e)}")
            raise APIError(f"Audio analysis failed: {str(e)}")

# 创建全局AI客户端实例
ai_client = AIClient() 