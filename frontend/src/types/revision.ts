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
  id: number
  note_id: number
  scheduled_date: string
  mastery_level: 'not_mastered' | 'partially_mastered' | 'mastered'
  revision_count: number
  created_at: string
  completed_at: string | null
  note: Note
}

export type RevisionStatus = 'not_started' | 'in_progress' | 'completed' 