export interface RevisionHistory {
  id: number
  note_id: number
  task_id: number
  mastery_level: string
  revision_date: string
  comments: string
}

export interface NoteStatistics {
  total_revisions: number
  mastery_levels: Record<string, number>
  revision_dates: string[]
} 