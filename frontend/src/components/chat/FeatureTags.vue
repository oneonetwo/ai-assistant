<template>
  <div class="feature-tag" :class="{ active }">
    <div class="icon">
      <component :is="icon" />
    </div>
    <span class="text">{{ title }}</span>
  </div>
</template>

<style lang="scss" scoped>
.feature-tag {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: var(--van-padding-sm) var(--van-padding-md);
  background: var(--tag-bg);
  border-radius: var(--van-radius-md);
  cursor: pointer;
  transition: all 0.2s var(--bounce-timing);
  
  &:hover {
    background: var(--tag-hover-bg);
    transform: translateY(-2px);
  }
  
  .icon {
    width: 20px;
    height: 20px;
    color: var(--van-text-color-2);
  }
  
  .text {
    color: var(--van-text-color-2);
    font-size: var(--van-font-size-sm);
  }
}

.feature-tags {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--van-padding-md);
  max-width: 800px;
  width: 100%;
  
  .feature-tag {
    display: flex;
    align-items: center;
    gap: var(--van-padding-xs);
    padding: var(--van-padding-md);
    background: var(--van-background-2);
    border-radius: var(--radius-md);
    border: 1px solid var(--van-border-color);
    transition: all 0.2s var(--bounce-timing);
    
    &:hover {
      transform: translateY(-2px);
      border-color: var(--van-primary-color);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .svg-icon {
      width: 24px;
      height: 24px;
      color: var(--van-primary-color);
    }
  }
}
</style> 