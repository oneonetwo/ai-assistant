interface NotificationOptions {
  title: string
  body: string
  icon?: string
  tag?: string
  onClick?: () => void
}

export class NotificationManager {
  private static instance: NotificationManager
  private permission: NotificationPermission = 'default'

  private constructor() {
    this.init()
  }

  static getInstance(): NotificationManager {
    if (!NotificationManager.instance) {
      NotificationManager.instance = new NotificationManager()
    }
    return NotificationManager.instance
  }

  private async init() {
    if (!('Notification' in window)) {
      console.warn('该浏览器不支持系统通知')
      return
    }

    if (Notification.permission === 'granted') {
      this.permission = 'granted'
    } else if (Notification.permission !== 'denied') {
      this.permission = await Notification.requestPermission()
    }
  }

  async requestPermission(): Promise<boolean> {
    if (!('Notification' in window)) {
      return false
    }

    try {
      const permission = await Notification.requestPermission()
      this.permission = permission
      return permission === 'granted'
    } catch (error) {
      console.error('请求通知权限失败:', error)
      return false
    }
  }

  async show(options: NotificationOptions): Promise<boolean> {
    if (this.permission !== 'granted') {
      const granted = await this.requestPermission()
      if (!granted) return false
    }

    try {
      const notification = new Notification(options.title, {
        body: options.body,
        icon: options.icon,
        tag: options.tag
      })

      if (options.onClick) {
        notification.onclick = () => {
          options.onClick?.()
          notification.close()
        }
      }

      return true
    } catch (error) {
      console.error('显示通知失败:', error)
      return false
    }
  }
}

export const notificationManager = NotificationManager.getInstance() 