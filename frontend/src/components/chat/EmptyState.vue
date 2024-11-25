<template>
  <div class="empty-state">
    <div class="welcome">
      <h1>AI 助手</h1>
      <p>选择以下功能开始对话，或直接输入问题</p>
    </div>

    <div class="feature-tags">
      <div v-for="tag in tags" :key="tag.id" class="feature-tag">
        <svg-icon :name="tag.icon" class="tag-icon" />
        <span class="tag-text">{{ tag.label }}</span>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
  gap: 48px;

  .welcome {
    text-align: center;
    
    h1 {
      font-size: 32px;
      font-weight: 600;
      margin-bottom: 16px;
      background: linear-gradient(45deg, var(--van-primary-color), #4f46e5);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    
    p {
      color: var(--van-text-color-2);
      font-size: 16px;
    }
  }

  .feature-tags {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    max-width: 800px;
    width: 100%;
  }

  .feature-tag {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px;
    background: var(--van-background-2);
    border: 1px solid var(--van-border-color);
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.2s var(--bounce-timing);

    &:hover {
      transform: translateY(-2px);
      border-color: var(--van-primary-color);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    .tag-icon {
      width: 24px;
      height: 24px;
      color: var(--van-primary-color);
    }

    .tag-text {
      color: var(--van-text-color);
      font-size: 14px;
    }
  }
}
</style> 