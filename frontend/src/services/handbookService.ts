import { request } from '@/utils/request'
import type { Category, Handbook } from '@/types/handbook'

const API_BASE_URL = '/api/v1'

/**
 * 手册管理 API 类
 */
export class HandbookAPI {
  /**
   * 创建分类
   */
  static async createCategory(name: string): Promise<Category> {
    const response = await request.post(`${API_BASE_URL}/handbooks/categories`, { name })
    return response
  }

  /**
   * 获取所有分类
   */
  static async getCategories(): Promise<Category[]> {
    const response = await request.get(`${API_BASE_URL}/handbooks/categories`)
    return response
  }

  /**
   * 创建手册
   */
  static async createHandbook(name: string, category_id: number): Promise<Handbook> {
    const response = await request.post(`${API_BASE_URL}/handbooks`, { name, category_id })
    return response
  }

  /**
   * 获取手册列表
   */
  static async getHandbooks(categoryId?: number): Promise<Handbook[]> {
    const url = `${API_BASE_URL}/handbooks`
    const params = categoryId ? { category_id: categoryId } : undefined
    const response = await request.get(url, { params })
    return response
  }

  /**
   * 获取单个手册
   */
  static async getHandbook(handbookId: number): Promise<Handbook> {
    const response = await request.get(`${API_BASE_URL}/handbooks/${handbookId}`)
    return response
  }

  /**
   * 更新手册
   */
  static async updateHandbook(
    handbookId: number,
    data: { name?: string; category_id?: number }
  ): Promise<Handbook> {
    const response = await request.patch(`${API_BASE_URL}/handbooks/${handbookId}`, data)
    return response
  }

  /**
   * 删除手册
   */
  static async deleteHandbook(handbookId: number): Promise<void> {
    await request.delete(`${API_BASE_URL}/handbooks/${handbookId}`)
  }
}