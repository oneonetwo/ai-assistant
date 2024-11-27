from typing import Dict, Any, Optional, List, Tuple
import asyncio
from pathlib import Path
from PIL import Image
import pytesseract
from app.core.logging import app_logger
from app.services.ai_client import ai_client
from app.db.models import File, AnalysisRecord
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import base64
import io
from app.core.config import settings
import aiohttp

class ImageService:
    """图片处理服务"""
    
    async def process_image(self, file_path: Path) -> Tuple[str, Dict[str, Any]]:
        """处理图片并返回base64编码和元数据"""
        try:
            # 在线程池中执行同步图片处理
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._process_image_worker, file_path)
        except Exception as e:
            app_logger.error(f"图片处理失败: {str(e)}")
            raise

    def _process_image_worker(self, file_path: Path) -> Tuple[str, Dict[str, Any]]:
        """图片处理工作函数"""
        with Image.open(file_path) as img:
            # 获图片元数据
            metadata = {
                "format": img.format,
                "mode": img.mode,
                "size": img.size,
                "width": img.width,
                "height": img.height,
            }
            
            # 转换为RGB模式（如果需要）
            if img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')
            
            # 调整图片大小（如果太大）
            max_size = (1920, 1080)
            if img.width > max_size[0] or img.height > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # 转换为base64
            buffered = io.BytesIO()
            img.save(buffered, format=img.format or 'JPEG')
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            return img_base64, metadata

    async def extract_text(self, file_path: Path) -> str:
        """从图片中提取文字"""
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._extract_text_worker, file_path)
        except Exception as e:
            app_logger.error(f"文字提取失败: {str(e)}")
            raise

    def _extract_text_worker(self, file_path: Path) -> str:
        """OCR文字提取工作函数"""
        try:
            with Image.open(file_path) as img:
                # 转换为RGB模式（如果需要）
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                
                # 使用pytesseract进行OCR
                text = pytesseract.image_to_string(img, lang='chi_sim+eng')
                return text.strip()
        except Exception as e:
            raise ValueError(f"OCR处理失败: {str(e)}")

    async def analyze_image(
        self,
        db: AsyncSession,
        file_id: str,
        query: Optional[str] = None,
        extract_text: bool = False,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """分析图片内容"""
        try:
            # 获取文件记录
            file_query = select(File).where(File.file_id == file_id)
            result = await db.execute(file_query)
            file_record = result.scalar_one_or_none()
            
            if not file_record:
                raise ValueError(f"File not found: {file_id}")
            
            # 获取文件路径
            file_path = Path(settings.UPLOAD_DIR) / file_record.file_path
            
            # 处理图片
            img_base64, metadata = await self.process_image(file_path)
            
            # 提取文字（如果需要）
            extracted_text = None
            if extract_text:
                extracted_text = await self.extract_text(file_path)
            
            # 构建分析提示
            if not query:
                query = "请描述这张图片的内容，包括主要对象、场景、活动和其他显著特征。"
                
            if not system_prompt:
                system_prompt = """你是一个专业的图片分析助手。请仔细分析图片内容，提供准确、详细的描述。
                分析应该包括：
                1. 图片主要内容
                2. 重要细节
                3. 场景或背景
                4. 整体氛围或风格
                请用清晰的语言描述你的观察。"""
            
            # 调用AI进行分析
            analysis_result = await ai_client.analyze_image(
                image_base64=img_base64,
                query=query,
                system_prompt=system_prompt,
                extracted_text=extracted_text
            )
            
            # 保存分析记录
            analysis_record = AnalysisRecord(
                file_id=file_id,
                analysis_type="image",
                result=analysis_result
            )
            db.add(analysis_record)
            await db.commit()
            
            return {
                "file_id": file_id,
                "original_name": file_record.original_name,
                "metadata": metadata,
                "analysis": analysis_result,
                "extracted_text": extracted_text if extract_text else None
            }
            
        except Exception as e:
            app_logger.error(f"图片分析失败: {str(e)}")
            raise

    async def analyze_image_from_url(
        self,
        db: AsyncSession,
        image_url: str,
        query: Optional[str] = None,
        extract_text: bool = False,
        system_prompt: Optional[str] = None,
        session_id: str = None,
        file_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """从URL分析图片内容"""
        try:
            # 构建分析提示
            if not query:
                query = "请描述这张图片的内容，包括主要对象、场景、活动和其他显著特征。"
                
            if not system_prompt:
                system_prompt = """你是一个专业的图片分析助手。请仔细分析图片内容，提供准确、详细的描述。
                分析应该包括：
                1. 图片主要内容
                2. 重要细节
                3. 场景或背景
                4. 整体氛围或风格
                请用清晰的语言描述你的观察。"""
            
            # 直接使用URL调用AI进行分析
            analysis_result = await ai_client.analyze_image(
                image_url=image_url,
                query=query,
                system_prompt=system_prompt
            )

            # 如果提供了file_id，创建分析记录
            if file_id:
                analysis_record = AnalysisRecord(
                    file_id=file_id,
                    analysis_type="image",
                    result=analysis_result
                )
                db.add(analysis_record)
                await db.commit()
            
            return {
                "url": image_url,
                "file_id": file_id,
                "analysis": analysis_result,
                "extracted_text": None
            }

        except Exception as e:
            app_logger.error(f"从URL分析图片失败: {str(e)}")
            raise ValueError(f"图片分析失败: {str(e)}")

# 创建图片服务实例
image_service = ImageService() 