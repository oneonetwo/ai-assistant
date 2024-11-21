<script setup lang="ts">
import { ref, computed } from 'vue'
import { useChatStore } from '@/stores/chat'
import { useVirtualList } from '@vueuse/core'

const chatStore = useChatStore()
const searchKeyword = ref('')
const showSearch = ref(false)

const searchResults = computed(() => {
  if (!searchKeyword.value) return []
  
  const keyword = searchKeyword.value.toLowerCase()
  const results: Array<{
    conversationId: string
    messageId: string
    content: string
    timestamp: number
    matchIndex: number
  }> = []
  
  chatStore.conversations.forEach(conv => {
    conv.messages.forEach(msg => {
      const content = msg.content.toLowerCase()
      const index = content.indexOf(keyword)
      if (index !== -1) {
        results.push({
          conversationId: conv.id,
          messageId: msg.id,
          content: msg.content,
          timestamp: msg.timestamp,
          matchIndex: index
        })
      }
    })
  })
  
  return results.sort((a, b) => b.timestamp - a.timestamp)
})

const { list, containerProps, wrapperProps } = useVirtualList(
  searchResults,
  {
    itemHeight: 80,
    overscan: 5
  }
)

function handleResultClick(result: typeof searchResults.value[0]) {
  chatStore.setCurrentConversation(result.conversationId)
  // 滚动到对应消息
  const messageEl = document.getElementById(`message-${result.messageId}`)
  messageEl?.scrollIntoView({ behavior: 'smooth' })
  showSearch.value = false
}
</script>

<template>
  <div class="message-search">
    <van-button
      class="search-button"
      icon="search"
      @click="showSearch = true"
    />
    
    <van-popup
      v-model:show="showSearch"
      position="right"
      :style="{ width: '80%', height: '100%' }"
    >
      <div class="search-container">
        <div class="search-header">
          <van-search
            v-model="searchKeyword"
            placeholder="搜索消息内容"
            shape="round"
            autofocus
          />
          <van-button
            plain
            size="small"
            @click="showSearch = false"
          >
            取消
          </van-button>
        </div>
        
        <div 
          v-if="searchResults.length"
          class="search-results"
          v-bind="containerProps"
        >
          <div v-bind="wrapperProps">
            <div
              v-for="item in list"
              :key="`${item.conversationId}-${item.messageId}`"
              class="search-result-item"
              @click="handleResultClick(item)"
            >
              <div class="result-content">
                <p class="result-text">
                  {{ 
                    item.content.slice(
                      Math.max(0, item.matchIndex - 20),
                      item.matchIndex
                    ) 
                  }}
                  <span class="highlight">
                    {{ item.content.slice(
                      item.matchIndex,
                      item.matchIndex + searchKeyword.length
                    ) }}
                  </span>
                  {{ 
                    item.content.slice(
                      item.matchIndex + searchKeyword.length,
                      item.matchIndex + searchKeyword.length + 20
                    ) 
                  }}...
                </p>
                <span class="result-time">
                  {{ new Date(item.timestamp).toLocaleString() }}
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <van-empty
          v-else-if="searchKeyword"
          description="没有找到相关消息"
        />
      </div>
    </van-popup>
  </div>
</template>

<style lang="scss" scoped>
.message-search {
  position: fixed;
  right: var(--van-padding-md);
  bottom: 80px;
  z-index: 100;
}

.search-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.search-header {
  display: flex;
  align-items: center;
  padding: var(--van-padding-xs);
  border-bottom: 1px solid var(--van-border-color);
}

.search-results {
  flex: 1;
  overflow-y: auto;
}

.search-result-item {
  padding: var(--van-padding-sm);
  cursor: pointer;
  
  &:hover {
    background: var(--van-background-2);
  }
}

.result-content {
  .result-text {
    margin: 0;
    font-size: 14px;
    line-height: 1.5;
    color: var(--van-text-color);
  }
  
  .highlight {
    color: var(--van-primary-color);
    font-weight: 500;
  }
  
  .result-time {
    font-size: 12px;
    color: var(--van-text-color-2);
  }
}
</style> 