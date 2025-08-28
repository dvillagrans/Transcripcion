import pool from '../config/database.js';
import { Job, CreateJobData, UpdateJobData } from '../models/Job.js';
import { v4 as uuidv4 } from 'uuid';

export class JobService {
  static async createJob(data: CreateJobData): Promise<Job> {
    const id = uuidv4();
    const query = `
      INSERT INTO jobs (id, filename, status, transcription, summary)
      VALUES ($1, $2, $3, $4, $5)
      RETURNING *
    `;
    
    const values = [
      id,
      data.filename,
      data.status || 'processing',
      data.transcription || null,
      data.summary || null
    ];
    
    const result = await pool.query(query, values);
    return result.rows[0];
  }

  static async getJobById(id: string): Promise<Job | null> {
    const query = 'SELECT * FROM jobs WHERE id = $1';
    const result = await pool.query(query, [id]);
    return result.rows[0] || null;
  }

  static async updateJob(id: string, data: UpdateJobData): Promise<Job | null> {
    const fields = [];
    const values = [];
    let paramCount = 1;

    if (data.status !== undefined) {
      fields.push(`status = $${paramCount++}`);
      values.push(data.status);
    }
    if (data.transcription !== undefined) {
      fields.push(`transcription = $${paramCount++}`);
      values.push(data.transcription);
    }
    if (data.summary !== undefined) {
      fields.push(`summary = $${paramCount++}`);
      values.push(data.summary);
    }

    if (fields.length === 0) {
      return this.getJobById(id);
    }

    values.push(id);
    const query = `
      UPDATE jobs 
      SET ${fields.join(', ')}
      WHERE id = $${paramCount}
      RETURNING *
    `;

    const result = await pool.query(query, values);
    return result.rows[0] || null;
  }

  static async getAllJobs(limit: number = 50, offset: number = 0): Promise<Job[]> {
    const query = `
      SELECT * FROM jobs 
      ORDER BY created_at DESC 
      LIMIT $1 OFFSET $2
    `;
    const result = await pool.query(query, [limit, offset]);
    return result.rows;
  }

  static async deleteJob(id: string): Promise<boolean> {
    const query = 'DELETE FROM jobs WHERE id = $1';
    const result = await pool.query(query, [id]);
    return result.rowCount > 0;
  }

  static async getJobsByStatus(status: string): Promise<Job[]> {
    const query = 'SELECT * FROM jobs WHERE status = $1 ORDER BY created_at DESC';
    const result = await pool.query(query, [status]);
    return result.rows;
  }
}