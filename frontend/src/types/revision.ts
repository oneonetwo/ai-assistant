export interface RevisionPlan {
  id: number
  title: string
  handbook_ids: number[]
  category_ids?: number[]
  tag_ids?: number[]
  duration: number
  priority: 'high' | 'medium' | 'low'
  created_at: string
  updated_at: string
}

export interface RevisionTask {
  id: number
  plan_id: number
  note_id: number
  title: string
  status: 'not_mastered' | 'partially_mastered' | 'mastered'
  due_date: string
  completed_at?: string
}

export type RevisionStatus = 'not_started' | 'in_progress' | 'completed' 