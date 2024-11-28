# AI 聊天助手后端

## 项目概述
使用 FastAPI 提供 REST API 接口，接收前端请求。支持多模态对话、文档分析和图片处理。
使用 SQLAlchemy 进行数据库操作，Pydantic 进行请求数据验证。
Redis 用于缓存流式对话数据，加速交互体验。
支持与通义千问大模型的 API 调用，处理用户输入并返回模型生成的结果。


### 技术栈
- Python 3.10.7 
- FastAPI 2.4.0
- SQLAlchemy 2.0.30
- Alembic 1.11.1  
- Pydantic 2.5.2
- Redis 7.0+
- OpenAI API Compatible Client
Python 3.10.7：应用主语言，运行后端服务。
FastAPI 2.4.0：Web 框架，用于快速构建 RESTful API 接口，支持异步请求和高性能。
SQLAlchemy 2.0.30：ORM（对象关系映射）框架，处理数据库操作。
Alembic 1.11.1：数据库迁移工具，帮助管理数据库模式的变更。
Pydantic 2.5.2：数据验证工具，主要用于请求数据的校验和序列化。
Redis 7.0+：用于会话缓存，存储 AI 流式对话的缓存数据，提升响应速度。
MySQL 8.0+：关系型数据库，存储用户数据、会话信息等。


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


v1.2.0 开发知识手册管理功能

id：该笔记的唯一标识符。
title：笔记标题，可由用户自定义。
content：笔记的摘要或简短说明。
message_ids：记录AI对话内容id数组。
tags：标签数组，用户可以为笔记添加多个标签，便于搜索和分类。
category：笔记的分类，用于大类的归类（例如，学习、工作等）。
created_at 和 modified_at：记录笔记创建和最后修改的时间。
author：创建笔记的用户ID，用于区分不同用户的笔记。
priority：笔记的优先级（例如高、中、低），可以帮助用户识别重点内容。
times: 复习次数
status：笔记的状态，如是否已完成，或是否待复习。
attachments：附件字段，是个数组，用于存储笔记相关的文件（如图片或文档）的引用。
is_shared：是否共享

## v1.2.0 新功能：知识手册管理

### 功能特性
1. 知识手册管理
   - 创建、重命名、删除手册
   - 手册分类管理
   - 按分类浏览手册

2. 笔记管理
   - 在手册中创建笔记
   - 支持标签系统
   - 笔记优先级管理
   - 笔记状态跟踪
   - 复习次数统计
   - 附件管理
   - 笔记共享功能
### 知识手册管理
- **手册管理**
  - 创建、重命名、删除手册
  - 手册分类管理
  - 按分类浏览手册

- **笔记管理**
  - 在手册中创建笔记
  - 支持标签系统
  - 笔记优先级管理
  - 笔记状态跟踪
  - 复习次数统计
  - 附件管理
  - 笔记共享功能

- **标签管理**
  - 创建、删除标签
  - 获取所有标签
  - 获取最常用标签
  - 搜索标签

- **附件管理**
  - 为笔记添加附件
  - 获取笔记的所有附件
  - 移除附件

- **笔记搜索**
  - 关键词搜索（标题和内容）
  - 按手册、标签、分类、状态、优先级筛选
  - 按日期范围筛选
  - 灵活的排序选项
  - 分页支持

### API 端点

#### 手册管理
- POST /api/v1/handbooks - 创建新手册
- GET /api/v1/handbooks - 获取手册列表
- GET /api/v1/handbooks/{id} - 获取手册详情
- PATCH /api/v1/handbooks/{id} - 更新手册信息
- DELETE /api/v1/handbooks/{id} - 删除手册

#### 笔记管理
- POST /api/v1/handbooks/{id}/notes - 创建笔记
- GET /api/v1/handbooks/{id}/notes - 获取笔记列表
- GET /api/v1/notes/{id} - 获取笔记详情
- PATCH /api/v1/notes/{id} - 更新笔记
- DELETE /api/v1/notes/{id} - 删除笔记

#### 标签管理
- POST /api/v1/tags - 创建新标签
- GET /api/v1/tags - 获取所有标签
- GET /api/v1/tags/popular - 获取最常用的标签
- DELETE /api/v1/tags/{id} - 删除标签
- GET /api/v1/tags/search - 搜索标签

#### 附件管理
- POST /api/v1/attachments/notes/{note_id} - 为笔记添加附件
- GET /api/v1/attachments/notes/{note_id} - 获取笔记的所有附件
- DELETE /api/v1/attachments/{id} - 移除附件

#### 笔记搜索
- GET /api/v1/search/notes - 搜索笔记