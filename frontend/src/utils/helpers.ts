export function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}

export function formatDate(timestamp: number): string {
  const date = new Date(timestamp)
  const now = new Date()
  
  if (isSameDay(date, now)) {
    return '今天'
  }
  
  if (isYesterday(date, now)) {
    return '昨天'
  }
  
  if (isWithinDays(date, now, 7)) {
    return '前7天'
  }
  
  return '更早'
}

export function groupConversationsByDate(conversations: Conversation[]): ConversationGroup[] {
  const groups: Record<string, Conversation[]> = {}
  
  conversations.forEach(conversation => {
    const date = formatDate(conversation.createdAt)
    if (!groups[date]) {
      groups[date] = []
    }
    groups[date].push(conversation)
  })
  
  return Object.entries(groups).map(([date, items]) => ({
    date,
    items
  }))
} 