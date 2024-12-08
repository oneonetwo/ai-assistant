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
1. 智���对话
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
DATABASE_URL=mysql+
://user:pass@localhost/dbname

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

mysql -u root -p
DROP DATABASE ai_assistant;
CREATE DATABASE ai_assistant;
exit;
# 1. 删除所有迁移文件（保留 env.py 和 script.py.mako）
rm -f alembic/versions/*

# 2. 重新生成初始迁移
alembic revision --autogenerate -m "initial migration"

# 3. 执行迁移
alembic upgrade head


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

### 2024-12-01
#### v1.2.1 消息分析功能开发
- [ ] 新增消息分析接口
  - 支持单条/多条消息内容分析
  - 生成精简标题(≤30字)
  - 提供完整分析内容
  - 实现流式响应
- [ ] 实现消息分析服务
  - 消息内容预处理
  - AI模型调用封装
  - 流式响应处理
- [ ] 单元测试
- [ ] 接口文档更新
POST /api/v1/chat/analyze/stream
GET /api/v1/chat/analyze/stream
参数
{
"messages": ["消息1", "消息2", ...],
"system_prompt": "可选的系统提示词"
}

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



## v1.2.0 新功能：知识手册管理
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

## V1.2.0 知识手册管理功能

### 新增功能
- 知识手册管理
  - 支持创建、编辑、删除手册
  - 支持手册分类管理
  - 支持在手册中添加笔记
- 笔记管理
  - 支持创建、编辑、删除笔记
  - 支持添加标签
  - 支持添加附件
  - 支持设置优先级和状态
  - 支持笔记复习计数

### 数据结构说明

#### 优先级（priority）
- `high`: 高优先级
- `medium`: 中优先级
- `low`: 低优先级

#### 状态（status）
可自定义，建议值：
- `待复习`: 需要复习的笔记
- `已完成`: 已完成的笔记
- `进行中`: 正在学习的笔记

### 注意事项
1. 所有时间字段均使用 ISO 8601 格式的 UTC 时间
2. 笔记优先级必须是预定义的三个级别之一
3. 附件上传支持通过 URL 方式添加，系统会自动下载并保存
4. 标签支持多个，使用数组格式
5. 默认使用系统用户(user_id=1)
6. 删除手册时会级联删除所有相关笔记
7. 文件上传大小限制为 10MB


### V1.3.0 复习任务管理
现在进行V1.3.0任务的开发：开发针对手册和笔记的复习任务管理系统


一、复习计划模块设计
1. 复习计划的核心逻辑
  1.1 基于艾宾浩斯遗忘曲线： 每个笔记的复习时间点遵循遗忘曲线的时间节点（如1天、2天、7天、30天），并可自定义调整。
  1.2 计划范围： 用户可以按以下维度选择需要复习的内容：
    手册：选择一个或多个知识手册。
    分类：按手册内的分类筛选笔记。
    标签：按标签筛选（如“重点”、“难点”等）。
    状态：按状态筛选（如“未掌握”、“部分掌握”）。
  1.3 复习优先级： 根据笔记的优先级（如“高”、“中”、“低”）自动排布复习顺序，确保用户先复习重要内容。
2. 复习计划的创建流程
  2.1 用户选择复习范围（手册、分类、标签、状态）。
  2.2 选择计划周期（如7天、14天、30天）或自定义周期。
  2.3 系统生成每日复习任务列表，并提示每日任务量（如10条笔记）。
  2.4 用户可调整任务的优先级和顺序。
二、复习任务管理设计
1. 每日任务清单
  1.1 任务推送：每日复习任务以列表形式展示，按优先级排序。
  1.2 任务内容： 每个任务包含：
    笔记信息
    掌握状态选择（“���掌握”、“部分掌握”、“完全掌握”）。
  1.3 复习进度显示： 显示当天任务的复习进度（如“已完成5/10条”）。
2. 任务执行
  2.1 逐条复习： 用户逐条查看笔记内容，可以选择“标记为掌握”或“跳过”。
  2.2 快速复习模式： 支持快速复习功能（如闪卡模式），用户可以快速浏览标题并回忆内容，提升复习效率。
3. 任务记录与调整
  3.1 记录复习结果： 系统记录每条笔记的复习状态（完成时间、掌握状态）。
  3.2 智能调整任务： 未掌握或部分掌握的笔记会自动��入下一次复习计划，并适当提前复习时间。
三、复习提醒设计
1. 提醒机制
  1.1 多渠道提醒：
    App内提醒：通过首页消息、任务卡片提示复习任务。
    系统通知：每日设定时间推送复习任务提醒。
  1.2 自定义提醒时间： 用户可以选择提醒时间（如早上8点、晚上8点），也可关闭提醒功能。
2. 提醒内容
  2.1 提醒用户当日复习任务的内容摘要（如“今天有10条笔记需要复习”）。
  2.2 提供快捷按钮跳转至复习任务页面。
四、掌握状态与数据记录设计
  1. 笔记的掌握状态
    1.1 状态分类：
      未掌握：用户完全未记住笔记内容。
      部分掌握：用户能回忆部分内容，但不完整。
      完全掌握：用户能够完整回忆笔记内容。
    1.2 状态变更：
      用户可在复习任务中手动修改掌握状态。
      状态变更会影响笔记的下一次复习时间。
2. 复习历史记录
  2.1 记录内容：
      每条笔记的复习次数。
      最近一次复习时间。
      每次复习的掌握状态。
  2.2 可视化展示：
      显示复习曲线（如掌握状态随时间的变化）。
      展示复习次数统计（如“已复习10次”）。
      提供复习记录日志（如“2024-12-02 完���掌握”）。


## V1.3.0 复习任务管理系统 (2024-12-15)

### 功能概述
1. 复习计划管理
   - 基于艾宾浩斯遗忘曲线的复习计划生成
   - 支持按手册、分类、标签筛选复习内容
   - 自定义复习周期和任务优先级

2. 复习任务系统
   - 每日任务清单管理
   - 任务状态追踪（待复习、已完成、已跳过）
   - 掌握程度评估（未掌握、部分掌握、完全掌握）

3. 提醒机制
   - 每日任务提醒
   - 自定义提醒时间
   - 任务摘要生成

4. 历史记录系统
   - 复习历史记录
   - 掌握状态追踪
   - 复习统计数据

### API 接口
1. 复习计划接口 (/api/v1/revisions)
   - POST /plans - 创建复习计划
   - GET /plans - 获取计划列表
   - GET /plans/{plan_id} - 获取计划详情
   - GET /plans/{plan_id}/tasks - 获取计划任务
   - PATCH /tasks/{task_id} - 更新任务状态
   - GET /daily-tasks - 获取每日任务

2. 复习设置接口 (/api/v1/revision-settings)
   - GET /notifications/summary - 获取任务摘要
   - GET /settings - 获取提醒设置
   - PATCH /settings - 更新提醒设置
   - GET /history/note/{note_id} - 获取笔记历史
   - GET /statistics/note/{note_id} - 获取统计数据

### 数据模型
1. RevisionPlan - 复习计划
2. RevisionTask - 复习任务
3. RevisionSettings - 提醒设置
4. RevisionHistory - 复习历史

### 技术特性
- 异步任务处理
- 基于SQLAlchemy的数据持久化
- FastAPI路由系统
- Pydantic数据验证


### V1.3.3 统计功能

### 新增功能
1. 整体学习数据统计
   - 学习时长趋势分析
   - 知识点掌握情况统计
   - 复习计划完成率追踪
   - 标签使用分布分析

### API 接口
- GET /api/v1/statistics/study-time - 获取学习时长统计
- GET /api/v1/statistics/mastery - 获取知识点掌握统计  
- GET /api/v1/statistics/revision - 获取复习计划统计
- GET /api/v1/statistics/tags - 获取标签分布统计
- GET /api/v1/statistics/overall - 获取整体统计数据

### 统计指标
1. 学习时长
   - 总学习时长
   - 日均学习时长
   - 每周学习趋势
   - 学习高峰时段

2. 知识掌握
   - 知识点总数
   - 已掌握数量
   - 正在学习数量
   - 需要加强数量
   - 掌握率
   - 分类分布

3. 复习计划
   - 总计划数
   - 活跃计划数
   - 完成率
   - 逾期任务数
   - 待完成任务数
   - 每日完成趋势

4. 标签分布
   - 标签总数
   - 使用最多的标签
   - 分类标签统计
   - 最近使用的标签




