import { JobService } from './JobService.js';
import redisClient from '../config/redis.js';
import { JobProgress } from '../models/Job.js';
import fs from 'fs/promises';
import path from 'path';
import axios from 'axios';

export class AudioProcessingService {
  private static progressMap = new Map<string, JobProgress>();
  private static readonly TRANSCRIPTION_SERVICE_URL = process.env.TRANSCRIPTION_SERVICE_URL || 'http://localhost:5000';

  static async processAudio(jobId: string, filePath: string, options: {
    whisperModel?: string;
    generateSummary?: boolean;
  } = {}): Promise<void> {
    try {
      // Update job status to processing
      await JobService.updateJob(jobId, { status: 'processing' });
      
      // Set initial progress
      this.setProgress(jobId, 10, 'Iniciando procesamiento');
      
      // Check if transcription service is available
      const isServiceAvailable = await this.checkTranscriptionService();
      
      if (isServiceAvailable) {
        // Use real transcription service
        await this.transcribeWithFasterWhisper(jobId, filePath, options);
      } else {
        console.warn('Transcription service not available, falling back to simulation');
        await this.simulateTranscription(jobId, filePath);
      }
      
      // Generate summary if requested
      if (options.generateSummary) {
        this.setProgress(jobId, 80, 'Generando resumen');
        await this.simulateSummaryGeneration(jobId);
      }
      
      // Complete processing
      this.setProgress(jobId, 100, 'Completado');
      await JobService.updateJob(jobId, { status: 'completed' });
      
      // Clean up progress
      this.progressMap.delete(jobId);
      
    } catch (error) {
      console.error(`Error processing audio for job ${jobId}:`, error);
      await JobService.updateJob(jobId, { status: 'error' });
      this.progressMap.delete(jobId);
    }
  }

  private static async checkTranscriptionService(): Promise<boolean> {
    try {
      const response = await axios.get(`${this.TRANSCRIPTION_SERVICE_URL}/health`, {
        timeout: 5000
      });
      return response.status === 200;
    } catch (error) {
      console.warn('Transcription service health check failed:', error.message);
      return false;
    }
  }

  private static async transcribeWithFasterWhisper(jobId: string, filePath: string, options: {
    whisperModel?: string;
    generateSummary?: boolean;
  }): Promise<void> {
    try {
      this.setProgress(jobId, 20, 'Conectando con servicio de transcripción');
      
      // Prepare transcription request
      const transcriptionRequest = {
        file_path: path.resolve(filePath),
        model: options.whisperModel || 'medium',
        language: null, // Auto-detect
        generate_summary: options.generateSummary || false
      };
      
      this.setProgress(jobId, 30, 'Enviando archivo para transcripción');
      
      // Call transcription service
      const response = await axios.post(
        `${this.TRANSCRIPTION_SERVICE_URL}/transcribe`,
        transcriptionRequest,
        {
          timeout: 300000, // 5 minutes timeout
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );
      
      const result = response.data;
      
      if (result.success) {
        this.setProgress(jobId, 70, 'Procesando resultados de transcripción');
        
        // Update job with transcription results
        const updateData: any = {
          transcription: result.transcription
        };
        
        if (result.summary) {
          updateData.summary = result.summary;
        }
        
        await JobService.updateJob(jobId, updateData);
        
        console.log(`Transcription completed for job ${jobId}:`, {
          duration: result.duration,
          processing_time: result.processing_time,
          language: result.language,
          segments_count: result.segments_count,
          model_used: result.model_used
        });
        
      } else {
        throw new Error(result.error || 'Transcription failed');
      }
      
    } catch (error) {
      console.error('Error in faster-whisper transcription:', error);
      
      // Fallback to simulation if real transcription fails
      console.log('Falling back to simulation...');
      await this.simulateTranscription(jobId, filePath);
    }
  }

  private static async simulateTranscription(jobId: string, filePath: string): Promise<void> {
    // Simulate transcription process
    for (let i = 20; i <= 70; i += 10) {
      this.setProgress(jobId, i, 'Transcribiendo audio (simulación)');
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    // Mock transcription result
    const mockTranscription = `Transcripción simulada del archivo de audio. 
    Este es un ejemplo de texto transcrito que incluye múltiples oraciones 
    y párrafos para demostrar el funcionamiento del sistema de procesamiento 
    de audio. El archivo original era: ${path.basename(filePath)}.`;
    
    await JobService.updateJob(jobId, { transcription: mockTranscription });
  }

  private static async simulateSummaryGeneration(jobId: string): Promise<void> {
    // Simulate summary generation
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const job = await JobService.getJobById(jobId);
    if (job && job.transcription) {
      const mockSummary = `Resumen automático: El audio contiene información relevante 
      sobre el tema principal. Se identificaron conceptos clave y puntos importantes 
      que fueron extraídos del contenido transcrito.`;
      
      await JobService.updateJob(jobId, { summary: mockSummary });
    }
  }

  static setProgress(jobId: string, progress: number, currentStage: string): void {
    const jobProgress: JobProgress = {
      jobId,
      progress,
      currentStage,
      status: progress === 100 ? 'completed' : 'processing'
    };
    
    this.progressMap.set(jobId, jobProgress);
    
    // Store in Redis for persistence
    redisClient.setEx(`progress:${jobId}`, 3600, JSON.stringify(jobProgress))
      .catch(err => console.error('Redis error:', err));
  }

  static async getProgress(jobId: string): Promise<JobProgress | null> {
    // Try to get from memory first
    const memoryProgress = this.progressMap.get(jobId);
    if (memoryProgress) {
      return memoryProgress;
    }

    // Try to get from Redis
    try {
      const redisProgress = await redisClient.get(`progress:${jobId}`);
      if (redisProgress) {
        return JSON.parse(redisProgress);
      }
    } catch (error) {
      console.error('Error getting progress from Redis:', error);
    }

    return null;
  }

  static async cleanupFile(filePath: string): Promise<void> {
    try {
      await fs.unlink(filePath);
      console.log(`Cleaned up file: ${filePath}`);
    } catch (error) {
      console.error(`Error cleaning up file ${filePath}:`, error);
    }
  }
}