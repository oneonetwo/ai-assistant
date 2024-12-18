export interface RevisionPlan {
  id: number
  name: string
  start_date: string
  end_date: string
  handbook_ids: number[]
  category_ids: number[]
  tag_ids: number[]
  note_statuses: string[]
  status: 'active' | 'completed' | 'cancelled'
  created_at: string
  updated_at: string
}

export interface Note {
  id: number
  title: string
  content: string
  status: string
  priority: 'low' | 'medium' | 'high'
}

export interface RevisionTask {
  task_id: number
  scheduled_date: string
  priority: number
  status: 'completed' | 'pending'
  note_id: number
  note_title: string
  note_content: string
}

export interface RevisionSummary {
  date: string
  total_tasks: number
  message: string
  tasks: RevisionTask[]
  has_tasks: boolean
  pending_tasks: number
  upcoming_tasks: number
  completed_tasks: number
}

export type RevisionStatus = 'not_started' | 'in_progress' | 'completed' 