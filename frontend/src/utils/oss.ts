import OSS from 'ali-oss'
import { generateUUID } from './generateUUID'

// OSS 客户端配置
const ossConfig = {
  region: import.meta.env.VITE_OSS_REGION,
  accessKeyId: import.meta.env.VITE_OSS_ACCESS_KEY_ID,
  accessKeySecret: import.meta.env.VITE_OSS_ACCESS_KEY_SECRET,
  bucket: import.meta.env.VITE_OSS_BUCKET,
  secure: false // 使用 HTTPS
}

/**
 * 获取文件扩展名
 */
function getFileExtension(filename: string): string {
  return filename.slice(((filename.lastIndexOf('.') - 1) >>> 0) + 2)
}

/**
 * 生成 OSS 文件路径
 */
function generateOSSPath(file: File): string {
  const ext = getFileExtension(file.name)
  const timestamp = new Date().getTime()
  const uuid = generateUUID()
  return `chat/uploads/${timestamp}-${uuid}.${ext}`
}

/**
 * 上传文件到 OSS
 */
export async function uploadToOSS(
  file: File,
  options: {
    onProgress?: (progress: number) => void
    signal?: AbortSignal
  } = {}
): Promise<string> {
  try {
    console.log('上传文件到 OSS', file)
    console.log('OSS 配置', ossConfig)
    // 创建 OSS 客户端
    const client = new OSS(ossConfig)
    console.log('OSS 客户端创建成功', client)
    // 生成文件路径
    const ossPath = generateOSSPath(file)

    // 检查是否已取消
    if (options.signal?.aborted) {
      throw new Error('上传已取消')
    }

    // 简单上传
    const result = await client.put(ossPath, file)

    // 上传完成时回调100%进度
    options.onProgress?.(100)

    // 返回文件访问链接
    return `https://${ossConfig.bucket}.${ossConfig.region}.aliyuncs.com/${ossPath}`

  } catch (error) {
    console.error('OSS上传失败:', error)
    throw new Error('文件上传失败')
  }
} 