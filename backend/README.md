# AI 聊天助手后端
Python 3.10.7 
FastAPI 2.4.0
SQLAlchemy 2.0.30
Alembic 1.11.1  
Pydantic 2.5.2
# 启动项目
uvicorn app.main:app --reload    

## 项目结构 
├── app/
│ ├── init.py
│ ├── main.py
│ ├── core/
│ │ ├── init.py
│ │ ├── config.py # 配置管理
│ │ └── logging.py # 日志配置
│ ├── api/
│ │ ├── init.py
│ │ ├── v1/
│ │ │ ├── init.py
│ │ │ ├── chat.py # 聊天相关路由
│ │ │ └── context.py # 上下文管理路由
│ ├── models/
│ │ ├── init.py
│ │ └── schemas.py # Pydantic模型
│ ├── services/
│ │ ├── init.py
│ │ ├── ai_client.py # AI服务客户端
│ │ ├── chat.py # 聊天业务逻辑
│ │ └── context.py # 上下文管理逻辑
│ ├── db/
│ │ ├── init.py
│ │ ├── database.py # 数据库连接
│ │ └── models.py # SQLAlchemy模型
│ └── utils/
│ ├── init.py
│ └── exceptions.py # 自定义异常
├── tests/
│ └── init.py
├── alembic/ # 数据库迁移
│ └── versions/
├── requirements.txt
├── .env
└── README.md

## 开发日志

### 2024-03-21
#### 初始化项目结构
- [x] 创建基础目录结构
- [x] 设置依赖管理
- [x] 配置文件模板

#### 基础配置管理实现
- [x] 实现配置管理模块
  - 支持环境变量配置
  - 添加类型安全的配置管理
  - 实现配置单例模式
- [x] 添加自定义异常处理
- [x] 创建环境变量模板
- [x] 配置日志系统

#### 数据库连接设置
- [x] 配置数据库迁移环境
- [x] 创建初始数据库表结构
- [x] 实现数据库连接生命周期管理
- [x] 添加数据库会话依赖注入

#### 用户会话管理实现
- [x] 实现会话服务层
  - 创建和获取会话
  - 添加消息到会话
  - 获取上下文消息
  - 清除会话上下文
- [x] 实现会话管理API

#### 通义千问API集成
- [x] 实现AI服务客户端
  - 封装OpenAI兼容接口
  - 处理API调用错误
  - 支持系统提示词配置
- [x] 实现聊天服务层
  - 集成上下文管理
  - 消息持久化
  - 异步处理流程
- [x] 实现聊天API接口
  - 支持会话管理
  - 错误处理
  - 日志记录

## API文档

### 会话管理
- GET /api/v1/context/conversations - 获取所有会话列表
- POST /api/v1/context/conversations - 创建新会话
- GET /api/v1/context/conversations/{session_id} - 获取会话信息
- DELETE /api/v1/context/conversations/{session_id}/context - 清除会话上下文

### 聊天功能
- POST /api/v1/chat/{session_id} - 发送聊天消息
  - 请求体:
    ```json
    {
        "message": "用户消息内容"
    }
    ```
  - 响应体:
    ```json
    {
        "session_id": "会话ID",
        "response": "AI回复内容"
    }
    ```

## 使用示例

### 创建会话


```js
class ChatClient {
    constructor(sessionId) {
        this.sessionId = sessionId;
        this.baseUrl = '/api/v1/chat';
    }

    async streamChat(message, {
        onStart = () => {},
        onChunk = () => {},
        onEnd = () => {},
        onError = () => {}
    } = {}) {
        const eventSource = new EventSource(
            `${this.baseUrl}/${this.sessionId}/stream`
        );

        let fullText = '';

        eventSource.onmessage = (event) => {
            const response = JSON.parse(event.data);
            
            switch (response.type) {
                case 'start':
                    onStart();
                    break;
                    
                case 'chunk':
                    fullText += response.data.content;
                    onChunk(response.data.content, fullText);
                    break;
                    
                case 'end':
                    onEnd(response.data.full_text);
                    eventSource.close();
                    break;
                    
                case 'error':
                    onError(new Error(response.data.message));
                    eventSource.close();
                    break;
            }
        };

        eventSource.onerror = (error) => {
            onError(error);
            eventSource.close();
        };

        // 发送消息
        const response = await fetch(`${this.baseUrl}/${this.sessionId}/stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail);
        }
    }
}

// 使用示例
const chat = new ChatClient('test-session');

chat.streamChat('请给我讲个故事', {
    onStart: () => {
        console.log('开始生成回复...');
    },
    onChunk: (chunk, fullText) => {
        // 更新UI显示
        console.log('收到新chunk:', chunk);
    },
    onEnd: (fullText) => {
        console.log('回复完成:', fullText);
    },
    onError: (error) => {
        console.error('发生错误:', error);
    }
});

```