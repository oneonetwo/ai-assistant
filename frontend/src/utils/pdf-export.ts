import { jsPDF } from 'jspdf'
import html2canvas from 'html2canvas'
import { marked } from 'marked'

interface ExportOptions {
  title?: string
  author?: string
  subject?: string
  keywords?: string[]
}

export async function exportToPDF(messages: Message[], options: ExportOptions = {}) {
  const pdf = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4'
  })
  
  // 设置文档属性
  pdf.setProperties({
    title: options.title || 'Chat Export',
    author: options.author || 'AI Assistant',
    subject: options.subject || 'Chat History',
    keywords: options.keywords?.join(', ') || 'chat,export'
  })
  
  // 创建临时 DOM 元素来渲染消息
  const container = document.createElement('div')
  container.style.padding = '20px'
  container.style.width = '210mm' // A4 宽度
  container.style.position = 'absolute'
  container.style.left = '-9999px'
  document.body.appendChild(container)
  
  // 添加标题
  if (options.title) {
    const titleEl = document.createElement('h1')
    titleEl.textContent = options.title
    titleEl.style.textAlign = 'center'
    titleEl.style.marginBottom = '20px'
    container.appendChild(titleEl)
  }
  
  // 渲染消息
  for (const msg of messages) {
    const messageEl = document.createElement('div')
    messageEl.style.marginBottom = '20px'
    messageEl.style.pageBreakInside = 'avoid'
    
    // 添加时间戳
    const timeEl = document.createElement('div')
    timeEl.textContent = new Date(msg.timestamp).toLocaleString()
    timeEl.style.fontSize = '12px'
    timeEl.style.color = '#666'
    timeEl.style.marginBottom = '5px'
    messageEl.appendChild(timeEl)
    
    // 添加角色标识
    const roleEl = document.createElement('div')
    roleEl.textContent = msg.role === 'user' ? '用户' : 'AI助手'
    roleEl.style.fontWeight = 'bold'
    roleEl.style.marginBottom = '5px'
    messageEl.appendChild(roleEl)
    
    // 渲染消息内容
    const contentEl = document.createElement('div')
    contentEl.innerHTML = marked(msg.content)
    contentEl.querySelectorAll('pre code').forEach((block) => {
      block.style.whiteSpace = 'pre-wrap'
      block.style.wordBreak = 'break-all'
    })
    messageEl.appendChild(contentEl)
    
    container.appendChild(messageEl)
  }
  
  try {
    // 将 DOM 转换为 canvas
    const canvas = await html2canvas(container, {
      scale: 2,
      useCORS: true,
      logging: false
    })
    
    const imgData = canvas.toDataURL('image/jpeg', 0.95)
    
    // 计算页面数量
    const pageHeight = pdf.internal.pageSize.getHeight()
    const imgHeight = (canvas.height * 210) / canvas.width // 按 A4 宽度缩放
    const pageCount = Math.ceil(imgHeight / pageHeight)
    
    // 分页添加图片
    for (let i = 0; i < pageCount; i++) {
      if (i > 0) {
        pdf.addPage()
      }
      
      pdf.addImage(
        imgData,
        'JPEG',
        0,
        -(i * pageHeight),
        210,
        imgHeight
      )
    }
  } catch (error) {
    console.error('导出 PDF 失败:', error)
  } finally {
    // 清理临时 DOM 元素
    document.body.removeChild(container)
  }
} 