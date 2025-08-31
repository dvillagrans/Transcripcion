export interface Job {
  id: string;
  filename: string;
  status: 'processing' | 'completed' | 'error';
  transcription?: string;
  summary?: string;
  created_at: Date;
}

export interface CreateJobData {
  filename: string;
  status?: 'processing' | 'completed' | 'error';
  transcription?: string;
  summary?: string;
}

export interface UpdateJobData {
  status?: 'processing' | 'completed' | 'error';
  transcription?: string;
  summary?: string;
}

export interface JobProgress {
  jobId: string;
  progress: number;
  currentStage: string;
  status: 'processing' | 'completed' | 'error';
  estimated_time_remaining?: number;
  current_segment?: number;
  total_segments?: number;
  processed_duration?: number;
  total_duration?: number;
  use_segmentation?: boolean;
  start_time?: number;
}