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
}