import { onMounted, onUnmounted } from 'vue'

interface ShortcutConfig {
  key: string
  ctrl?: boolean
  shift?: boolean
  alt?: boolean
  handler: () => void
  description: string
}

export function useShortcuts(shortcuts: ShortcutConfig[]) {
  function handleKeydown(event: KeyboardEvent) {
    const matchedShortcut = shortcuts.find(shortcut => {
      return shortcut.key.toLowerCase() === event.key.toLowerCase() &&
        !!shortcut.ctrl === event.ctrlKey &&
        !!shortcut.shift === event.shiftKey &&
        !!shortcut.alt === event.altKey
    })

    if (matchedShortcut) {
      event.preventDefault()
      matchedShortcut.handler()
    }
  }

  onMounted(() => {
    window.addEventListener('keydown', handleKeydown)
  })

  onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown)
  })

  // 返回快捷键说明
  return shortcuts.map(shortcut => {
    const keys = []
    if (shortcut.ctrl) keys.push('Ctrl')
    if (shortcut.shift) keys.push('Shift')
    if (shortcut.alt) keys.push('Alt')
    keys.push(shortcut.key.toUpperCase())
    
    return {
      keys: keys.join(' + '),
      description: shortcut.description
    }
  })
} 