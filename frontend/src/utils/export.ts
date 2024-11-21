interface ExportOptions {
  format: 'markdown' | 'json' | 'txt'
  fileName?: string
}

export function exportMessages(messages: Message[], options: ExportOptions) {
  const { format, fileName = `chat-export-${new Date().toISOString()}` } = options
  
  let content = ''
  
  switch (format) {
    case 'markdown':
      content = messages.map(msg => {
        const role = msg.role === 'user' ? '用户' : 'AI助手'
        const time = new Date(msg.timestamp).toLocaleString()
        return `### ${role} (${time})\n\n${msg.content}\n\n---\n`
      }).join('\n')
      break
      
    case 'json':
      content = JSON.stringify(messages, null, 2)
      break
      
    case 'txt':
      content = messages.map(msg => {
        const role = msg.role === 'user' ? '用户' : 'AI助手'
        const time = new Date(msg.timestamp).toLocaleString()
        return `[${time}] ${role}:\n${msg.content}\n\n`
      }).join('')
      break
  }
  
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  
  const link = document.createElement('a')
  link.href = url
  link.download = `${fileName}.${format}`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
} 