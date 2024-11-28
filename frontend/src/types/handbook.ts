interface Handbook {
  id: string;
  title: string;
  description?: string;
  category?: string;
  created_at: number;
  updated_at: number;
}

interface Note {
  id: string;
  handbook_id: string;
  title: string;
  content: string;
  tags: string[];
  priority: 'low' | 'medium' | 'high';
  status: 'draft' | 'published' | 'archived';
  review_count: number;
  attachments: Attachment[];
  created_at: number;
  updated_at: number;
}

interface Tag {
  id: string;
  name: string;
  count: number;
}

interface Attachment {
  id: string;
  note_id: string;
  name: string;
  type: string;
  size: number;
  url: string;
  created_at: number;
} 