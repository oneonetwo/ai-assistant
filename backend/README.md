# AI 聊天助手后端

## 项目概述
基于 FastAPI 和通义千问API的智能助手后端服务，支持多模态对话、文档分析和图片处理。

### 技术栈
- Python 3.10.7 
- FastAPI 2.4.0
- SQLAlchemy 2.0.30
- Alembic 1.11.1  
- Pydantic 2.5.2
- Redis 7.0+
- OpenAI API Compatible Client

### 主要功能
1. 智能对话
   - 上下文管理
   - 流式响应
   - 会话持久化

2. 文档分析
   - 支持多种格式 (txt, pdf, docx, epub, md)
   - 文本提取和分析
   - 多文档对比
   - 智能总结

3. 图片分析
   - 图片内容识别
   - OCR文字提取
   - 场景描述
   - 图片问答

4. 系统特性
   - 响应缓存
   - 性能监控
   - 错误处理
   - 文件管理

## 快速开始

### 环境要求
- Python 3.10+
- Redis 7.0+
- MySQL 8.0+
- Tesseract OCR

### 安装依赖
```bash
pip install -r requirements.txt
```

### 配置环境变量
创建 .env 文件：
```env
# API配置
QWEN_API_KEY=your_api_key
QWEN_API_URL=https://api.example.com
QWEN_API_TIMEOUT=30

# 数据库配置
DATABASE_URL=mysql+asyncmy://user:pass@localhost/dbname

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_password
REDIS_PREFIX=ai_assistant

# 文件上传配置
MAX_UPLOAD_SIZE=10485760  # 10MB
```

### 启动服务
```bash
uvicorn app.main:app --reload
```

## API文档

### 文档分析
#### 分析单个文件
```http
POST /api/v1/document-analysis/analyze-file
```
请求参数：
- `file`: 文件（multipart/form-data）
- `query`: 分析问题（可选）
- `system_prompt`: 系统提示词（可选）
- `session_id`: 会话ID

响应示例：
```json
{
    "file_id": "uuid",
    "original_name": "document.pdf",
    "analysis": "文档分析结果...",
}
```

#### 分析多个文件
```http
POST /api/v1/document-analysis/analyze-multiple-files
```
请求参数：
- `files`: 文件列表（multipart/form-data）
- `query`: 分析问题（可选）
- `system_prompt`: 系统提示词（可选）
- `session_id`: 会话ID

### 图片分析
#### 分析图片
```http
POST /api/v1/image-analysis/analyze
```
请求参数：
- `file`: 图片文件（multipart/form-data）
- `query`: 分析问题（可选）
- `extract_text`: 是否提取文字（布尔值）
- `system_prompt`: 系统提示词（可选）
- `session_id`: 会话ID

响应示例：
```json
{
    "file_id": "uuid",
    "original_name": "image.jpg",
    "metadata": {
        "format": "JPEG",
        "mode": "RGB",
        "size": [800, 600],
        "width": 800,
        "height": 600
    },
    "analysis": "图片分析结果...",
    "extracted_text": "提取的文字内容..."
}
```

#### 提取图片文字
```http
POST /api/v1/image-analysis/extract-text
```
请求参数：
- `file`: 图片文件（multipart/form-data）
- `session_id`: 会话ID

### 聊天功能
```http
POST /api/v1/chat/{session_id}
```
请求体：
```json
{
    "message": "用户消息",
    "system_prompt": "可选的系统提示词"
}
```

## 开发日志

### 2024-03-21
#### 初始化项目结构
- [x] 创建基础目录结构
- [x] 设置依赖管理
- [x] 配置文件模板

#### 基础配置管理实现
- [x] 实现配置管理模块
- [x] 添加自定义异常处理
- [x] 创建环境变量模板
- [x] 配置日志系统

#### 数据库连接设置
- [x] 配置数据库迁移环境
- [x] 创建初始数据库表结构
- [x] 实现数据库连接生命周期管理
- [x] 添加数据库会话依赖注入

### 2024-03-22
#### 文档分析功能
- [x] 实现文档服务层
  - 多格式支持
  - 文本提取
  - 内容分析
- [x] 实现文档分析API
  - 单文件分析
  - 多文件对比
  - 文本摘要

#### 图片分析功能
- [x] 实现图片服务层
  - 图片预处理
  - OCR支持
  - 内容分析
- [x] 实现图片分析API
  - 图片描述
  - 文字提取
  - 场景识别

#### AI集成优化
- [x] 增强AI客户端
  - 重试机制
  - 响应缓存
  - 长文本处理
- [x] 性能优化
  - Redis缓存
  - 性能监控
  - 资源管理

## 使用示例

### 文档分析
```python
import requests

def analyze_document(file_path, session_id):
    url = "http://localhost:8000/api/v1/document-analysis/analyze-file"
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        params = {'session_id': session_id}
        
        response = requests.post(url, files=files, params=params)
        return response.json()

# 使用示例
result = analyze_document('example.pdf', 'session123')
print(result['analysis'])
```

### 图片分析
```python
import requests

def analyze_image(image_path, session_id, extract_text=False):
    url = "http://localhost:8000/api/v1/image-analysis/analyze"
    
    with open(image_path, 'rb') as f:
        files = {'file': f}
        params = {
            'session_id': session_id,
            'extract_text': extract_text
        }
        
        response = requests.post(url, files=files, params=params)
        return response.json()

# 使用示例
result = analyze_image('example.jpg', 'session123', extract_text=True)
print(result['analysis'])
print(result['extracted_text'])
```

## 部署说明

### Docker部署
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 性能优化建议
1. 使用Redis缓存频繁请求的响应
2. 对大文件进行分块处理
3. 使用异步操作处理I/O密集型任务
4. 启用响应压缩
5. 配置适当的工作进程数

### 安全建议
1. 启用文件类型验证
2. 限制上传文件大小
3. 实现速率限制
4. 配置CORS策略
5. 使用HTTPS

## 贡献指南
1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证
MIT License

