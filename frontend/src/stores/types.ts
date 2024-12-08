export interface NoteStatistics {
  total_revisions: number;
  mastery_levels: {
    low: number;
    medium: number;
    high: number;
  };
  revision_trends: {
    date: string;
    count: number;
    duration: number;
    quality: number;
  }[];
  average_duration: number;
  average_quality: number;
} 