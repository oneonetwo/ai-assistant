/**
 * AI聊天助手 API 调用示例
 * 包含会话管理和聊天功能的完整实现
 * 这个文件包含了：
详细的代码注释和文档字符串
清晰的代码结构和模块化设计
完整的错误处理
所有API的封装实现
实用的使用示例
主要特点：
1. 使用类封装相关功能，提高代码复用性
添加了完整的TypeScript风格的注释，便于维护
实现了优雅的错误处理机制
支持ESM模块导出，方便集成到现代前端项目
提供了完整的使用示例
使用方法：
直接引入需要的类或函数
按照示例代码调用相应的方法
根据实际需求自定义回调函数
注意处理可能的错误情况
这个文件可以作为与后端API交互的核心模块使用。
 */

// API基础配置
const API_BASE_URL = '/api/v1';

/**
 * 通用错误处理函数
 * @param {Error} error - 错误对象
 * @throws {Error} 抛出处理后的错误
 */
const handleError = (error) => {
    console.error('API请求错误:', error);
    throw error;
};

/**
 * 会话管理相关API
 */
class ConversationAPI {
    /**
     * 创建新会话
     * @param {string} [sessionId] - 可选的会话ID，不传则自动生成
     * @returns {Promise<Object>} 返回创建的会话信息
     */
    static async createConversation(sessionId = null) {
        try {
            const response = await fetch(`${API_BASE_URL}/context/conversations`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: sessionId
                })
            });
            
            if (!response.ok) {
                throw await response.json();
            }
            
            return await response.json();
        } catch (error) {
            handleError(error);
        }
    }

    /**
     * 获取会话信息
     * @param {string} sessionId - 会话ID
     * @returns {Promise<Object>} 返回会话详细信息
     */
    static async getConversation(sessionId) {
        try {
            const response = await fetch(`${API_BASE_URL}/context/conversations/${sessionId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (!response.ok) {
                throw await response.json();
            }
            
            return await response.json();
        } catch (error) {
            handleError(error);
        }
    }

    /**
     * 清除会话上下文
     * @param {string} sessionId - 会话ID
     * @returns {Promise<Object>} 返回操作结果
     */
    static async clearContext(sessionId) {
        try {
            const response = await fetch(`${API_BASE_URL}/context/conversations/${sessionId}/context`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (!response.ok) {
                throw await response.json();
            }
            
            return await response.json();
        } catch (error) {
            handleError(error);
        }
    }
}

/**
 * 聊天客户端类
 * 处理与AI的实时对话
 */
class ChatClient {
    /**
     * 创建聊天客户端实例
     * @param {string} sessionId - 会话ID
     */
    constructor(sessionId) {
        this.sessionId = sessionId;
        this.baseUrl = `${API_BASE_URL}/chat`;
    }

    /**
     * 发送消息并获取流式响应
     * @param {string} message - 用户消息
     * @param {Object} callbacks - 回调函数集合
     * @param {Function} [callbacks.onStart] - 开始回调
     * @param {Function} [callbacks.onChunk] - 收到数据块回调
     * @param {Function} [callbacks.onEnd] - 结束回调
     * @param {Function} [callbacks.onError] - 错误回调
     */
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

        // 处理服务器发送的事件
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

        // 处理连接错误
        eventSource.onerror = (error) => {
            onError(error);
            eventSource.close();
        };

        // 发送用户消息
        try {
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
        } catch (error) {
            eventSource.close();
            onError(error);
        }
    }
}

/**
 * 完整的聊天流程示例
 * 展示了如何使用上述所有API进行对话
 */
async function startChatting() {
    try {
        // 1. 创建新会话
        const conversation = await ConversationAPI.createConversation();
        const sessionId = conversation.session_id;
        console.log('会话创建成功:', sessionId);
        
        // 2. 创建聊天客户端
        const chat = new ChatClient(sessionId);
        
        // 3. 发送消息并处理流式响应
        await chat.streamChat('你好，请介绍一下你自己', {
            onStart: () => {
                console.log('AI开始回复...');
            },
            onChunk: (chunk, fullText) => {
                console.log('收到回复片段:', chunk);
                // 这里可以更新UI显示
                document.getElementById('response').textContent = fullText;
            },
            onEnd: (fullText) => {
                console.log('对话完成');
                console.log('完整回复:', fullText);
            },
            onError: (error) => {
                console.error('对话出错:', error);
            }
        });
        
        // 4. 获取会话信息
        const conversationInfo = await ConversationAPI.getConversation(sessionId);
        console.log('当前会话信息:', conversationInfo);
        
        // 5. 清除上下文（可选）
        await ConversationAPI.clearContext(sessionId);
        console.log('会话上下文已清除');
        
    } catch (error) {
        console.error('操作失败:', error);
    }
}

// 导出所有类和函数供其他模块使用
export {
    ConversationAPI,
    ChatClient,
    startChatting
};

// 使用示例
// startChatting();
