<template>
  <div class="chat-messages" ref="messagesRef">
    <div v-for="message in messages" :key="message.id" class="message-item" :class="message.role">
      <div class="message-avatar">
        <template v-if="message.role === 'user'">
          <div class="user-avatar">JY</div>
        </template>
        <template v-else>
          <div class="ai-avatar">AI</div>
        </template>
      </div>
      
      <div class="message-content">
        <div class="message-text" v-html="renderMessage(message.content)"></div>
        <div class="message-actions">
          <button class="action-btn">
            <svg-icon name="copy" />
          </button>
          <button class="action-btn">
            <svg-icon name="edit" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  
  .message-item {
    display: flex;
    gap: 16px;
    margin-bottom: 24px;
    
    &.user {
      flex-direction: row-reverse;
      
      .message-content {
        .bubble {
          background: var(--chat-user-bg);
          border-radius: var(--chat-border-radius) 0 var(--chat-border-radius) var(--chat-border-radius);
          margin-left: auto;
        }
        
        .message-actions {
          justify-content: flex-end;
        }
      }
    }
    
    &.assistant {
      .bubble {
        background: var(--chat-ai-bg);
        border-radius: 0 var(--chat-border-radius) var(--chat-border-radius) var(--chat-border-radius);
      }
    }
  }
  
  .message-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 500;
    flex-shrink: 0;
    
    &.user {
      background: var(--primary-color);
      color: white;
    }
    
    &.assistant {
      background: var(--ai-avatar-bg);
      color: var(--ai-avatar-color);
    }
  }
  
  .message-content {
    flex: 1;
    max-width: 80%;
    
    .bubble {
      padding: 12px 16px;
      line-height: 1.5;
      word-break: break-word;
      
      pre {
        margin: 8px 0;
        padding: 12px;
        border-radius: 4px;
        background: var(--van-background);
        overflow-x: auto;
      }
    }
    
    .message-actions {
      display: none;
      gap: 8px;
      margin-top: 8px;
      
      .van-button {
        padding: 0 12px;
        height: 28px;
        font-size: 13px;
      }
    }
    
    &:hover .message-actions {
      display: flex;
    }
  }
}
</style> 