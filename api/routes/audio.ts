import express, { Request, Response } from 'express';
import multer from 'multer';
import path from 'path';
import { JobService } from '../services/JobService.js';
import { AudioProcessingService } from '../services/AudioProcessingService.js';
import fs from 'fs/promises';

const router = express.Router();

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: async (req, file, cb) => {
    const uploadDir = process.env.UPLOAD_DIR || './uploads';
    try {
      await fs.mkdir(uploadDir, { recursive: true });
      cb(null, uploadDir);
    } catch (error) {
      cb(error, uploadDir);
    }
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({
  storage,
  limits: {
    fileSize: parseInt(process.env.MAX_FILE_SIZE || '100000000') // 100MB default
  },
  fileFilter: (req, file, cb) => {
    const allowedTypes = ['.mp3', '.wav', '.flac', '.m4a', '.ogg'];
    const ext = path.extname(file.originalname).toLowerCase();
    
    if (allowedTypes.includes(ext)) {
      cb(null, true);
    } else {
      cb(new Error('Tipo de archivo no soportado. Use: MP3, WAV, FLAC, M4A, OGG'));
    }
  }
});

/**
 * POST /api/audio/upload
 * Upload and process audio file
 */
router.post('/upload', upload.single('audioFile'), async (req: Request, res: Response) => {
  try {
    if (!req.file) {
      return res.status(400).json({
        success: false,
        error: 'No se proporcionó archivo de audio'
      });
    }

    const { whisperModel = 'medium', generateSummary = false, language = 'es' } = req.body;
    
    // Create job in database
    const job = await JobService.createJob({
      filename: req.file.originalname,
      status: 'processing'
    });

    // Start processing asynchronously
    AudioProcessingService.processAudio(job.id, req.file.path, {
      whisperModel,
      language,
      generateSummary: generateSummary === 'true' || generateSummary === true
    }).catch(error => {
      console.error('Audio processing error:', error);
    });

    res.json({
      success: true,
      data: {
        jobId: job.id,
        status: job.status,
        filename: job.filename
      }
    });

  } catch (error) {
    console.error('Upload error:', error);
    res.status(500).json({
      success: false,
      error: 'Error al procesar el archivo'
    });
  }
});

/**
 * GET /api/audio/status/:jobId
 * Get processing status of a job
 */
router.get('/status/:jobId', async (req: Request, res: Response) => {
  try {
    const { jobId } = req.params;
    
    const job = await JobService.getJobById(jobId);
    if (!job) {
      return res.status(404).json({
        success: false,
        error: 'Trabajo no encontrado'
      });
    }

    const progress = await AudioProcessingService.getProgress(jobId);
    
    res.json({
      success: true,
      data: {
        jobId: job.id,
        status: job.status,
        progress: progress?.progress || (job.status === 'completed' ? 100 : 0),
        currentStage: progress?.currentStage || job.status
      }
    });

  } catch (error) {
    console.error('Status error:', error);
    res.status(500).json({
      success: false,
      error: 'Error al obtener el estado'
    });
  }
});

/**
 * GET /api/audio/results/:jobId
 * Get transcription results
 */
router.get('/results/:jobId', async (req: Request, res: Response) => {
  try {
    const { jobId } = req.params;
    
    const job = await JobService.getJobById(jobId);
    if (!job) {
      return res.status(404).json({
        success: false,
        error: 'Trabajo no encontrado'
      });
    }

    res.json({
      success: true,
      data: {
        jobId: job.id,
        filename: job.filename,
        status: job.status,
        transcription: job.transcription,
        summary: job.summary,
        createdAt: job.created_at
      }
    });

  } catch (error) {
    console.error('Results error:', error);
    res.status(500).json({
      success: false,
      error: 'Error al obtener los resultados'
    });
  }
});

/**
 * GET /api/audio/jobs
 * Get list of all jobs
 */
router.get('/jobs', async (req: Request, res: Response) => {
  try {
    const limit = parseInt(req.query.limit as string) || 50;
    const offset = parseInt(req.query.offset as string) || 0;
    
    const jobs = await JobService.getAllJobs(limit, offset);
    
    res.json({
      success: true,
      data: {
        jobs: jobs.map(job => ({
          jobId: job.id,
          filename: job.filename,
          status: job.status,
          createdAt: job.created_at,
          hasTranscription: !!job.transcription,
          hasSummary: !!job.summary
        }))
      }
    });

  } catch (error) {
    console.error('Jobs list error:', error);
    res.status(500).json({
      success: false,
      error: 'Error al obtener la lista de trabajos'
    });
  }
});

/**
 * DELETE /api/audio/jobs/:jobId
 * Delete a job
 */
router.delete('/jobs/:jobId', async (req: Request, res: Response) => {
  try {
    const { jobId } = req.params;
    
    const deleted = await JobService.deleteJob(jobId);
    if (!deleted) {
      return res.status(404).json({
        success: false,
        error: 'Trabajo no encontrado'
      });
    }

    res.json({
      success: true,
      message: 'Trabajo eliminado correctamente'
    });

  } catch (error) {
    console.error('Delete job error:', error);
    res.status(500).json({
      success: false,
      error: 'Error al eliminar el trabajo'
    });
  }
});

export default router;