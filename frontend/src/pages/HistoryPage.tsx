import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { History, FileText, Calendar, Trash2, Eye, AlertCircle } from 'lucide-react';

interface JobSummary {
  jobId: string;
  filename: string;
  status: string;
  createdAt: string;
  hasTranscription: boolean;
  hasSummary: boolean;
}

const HistoryPage: React.FC = () => {
  const [jobs, setJobs] = useState<JobSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingJob, setDeletingJob] = useState<string | null>(null);

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    try {
      const response = await fetch('/api/audio/jobs');
      const data = await response.json();

      if (data.success) {
        setJobs(data.data.jobs);
      } else {
        setError(data.error || 'Error al cargar el historial');
      }
    } catch (err) {
      setError('Error de conexión');
    } finally {
      setLoading(false);
    }
  };

  const deleteJob = async (jobId: string) => {
    if (!confirm('¿Estás seguro de que quieres eliminar este trabajo?')) {
      return;
    }

    setDeletingJob(jobId);
    try {
      const response = await fetch(`/api/audio/jobs/${jobId}`, {
        method: 'DELETE'
      });
      const data = await response.json();

      if (data.success) {
        setJobs(jobs.filter(job => job.jobId !== jobId));
      } else {
        alert('Error al eliminar el trabajo');
      }
    } catch (err) {
      alert('Error de conexión');
    } finally {
      setDeletingJob(null);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return 'Completado';
      case 'processing':
        return 'Procesando';
      case 'error':
        return 'Error';
      default:
        return status;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 flex items-center justify-center p-6">
        <div className="glass-effect rounded-3xl p-12 text-center animate-fade-in">
          <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-2xl flex items-center justify-center mx-auto mb-6 animate-pulse">
            <History className="h-8 w-8 text-white" />
          </div>
          <div className="loading-spinner mx-auto mb-6"></div>
          <h3 className="text-xl font-semibold text-gray-800 mb-2">Cargando Historial</h3>
          <p className="text-gray-600">Recuperando tus trabajos...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 flex items-center justify-center p-6">
        <div className="glass-effect rounded-3xl p-12 text-center animate-fade-in max-w-md">
          <div className="w-16 h-16 bg-gradient-to-br from-danger-500 to-warning-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <AlertCircle className="h-8 w-8 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Error al cargar</h2>
          <p className="text-gray-600 mb-8">{error}</p>
          <button
            onClick={fetchJobs}
            className="group relative px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-2xl font-semibold shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 overflow-hidden"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-primary-600 to-secondary-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <div className="relative">Reintentar</div>
            <div className="absolute inset-0 -skew-x-12 bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-0 group-hover:opacity-100 group-hover:animate-shine"></div>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-4 animate-fade-in">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-2xl shadow-lg mb-4">
            <History className="h-10 w-10 text-white" />
          </div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
            Historial de Trabajos
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Explora y gestiona todos tus archivos de audio procesados con IA
          </p>
        </div>

        {/* Jobs List */}
        {jobs.length === 0 ? (
          <div className="glass-effect rounded-3xl p-12 text-center animate-slide-up">
            <div className="w-16 h-16 bg-gradient-to-br from-gray-400 to-gray-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <FileText className="h-8 w-8 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-gray-800 mb-4">¡Comienza tu primera transcripción!</h2>
            <p className="text-gray-600 mb-8 max-w-md mx-auto">
              Aún no has procesado ningún archivo de audio. Sube tu primer archivo y descubre el poder de la IA.
            </p>
            <Link
              to="/process"
              className="group relative px-8 py-4 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-2xl font-semibold text-lg shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 overflow-hidden"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-primary-600 to-secondary-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              <div className="relative flex items-center space-x-3">
                <span className="text-xl">🎵</span>
                <span>Procesar tu primer archivo</span>
              </div>
              <div className="absolute inset-0 -skew-x-12 bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-0 group-hover:opacity-100 group-hover:animate-shine"></div>
            </Link>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 animate-slide-up">
            {jobs.map((job, index) => (
              <div
                key={job.jobId}
                className="glass-effect rounded-3xl p-6 hover:shadow-xl transition-all duration-300 hover:scale-105 group"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                {/* Card Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center shadow-lg ${
                      job.status === 'completed' 
                        ? 'bg-gradient-to-br from-success-500 to-primary-500'
                        : job.status === 'processing'
                        ? 'bg-gradient-to-br from-warning-500 to-secondary-500'
                        : 'bg-gradient-to-br from-danger-500 to-warning-500'
                    }`}>
                      <FileText className="h-6 w-6 text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-gray-800 truncate group-hover:text-primary-600 transition-colors">
                        {job.filename}
                      </h3>
                      <p className="text-xs text-gray-500 font-mono">
                        ID: {job.jobId.substring(0, 8)}...
                      </p>
                    </div>
                  </div>
                  
                  {/* Status Badge */}
                  <div className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    job.status === 'completed'
                      ? 'bg-gradient-to-r from-success-100 to-primary-100 text-success-700 border border-success-200'
                      : job.status === 'processing'
                      ? 'bg-gradient-to-r from-warning-100 to-secondary-100 text-warning-700 border border-warning-200'
                      : 'bg-gradient-to-r from-danger-100 to-warning-100 text-danger-700 border border-danger-200'
                  }`}>
                    {getStatusText(job.status)}
                  </div>
                </div>

                {/* Content Tags */}
                <div className="flex flex-wrap gap-2 mb-4">
                  {job.hasTranscription && (
                    <span className="inline-flex items-center px-3 py-1 text-xs bg-gradient-to-r from-primary-100 to-secondary-100 text-primary-700 rounded-full border border-primary-200">
                      📝 Transcripción
                    </span>
                  )}
                  {job.hasSummary && (
                    <span className="inline-flex items-center px-3 py-1 text-xs bg-gradient-to-r from-accent-100 to-primary-100 text-accent-700 rounded-full border border-accent-200">
                      🤖 Resumen IA
                    </span>
                  )}
                  {!job.hasTranscription && !job.hasSummary && (
                    <span className="text-xs text-gray-500 italic">Sin contenido disponible</span>
                  )}
                </div>

                {/* Date */}
                <div className="flex items-center text-sm text-gray-600 mb-6">
                  <Calendar className="h-4 w-4 mr-2" />
                  {formatDate(job.createdAt)}
                </div>

                {/* Actions */}
                <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                  {job.status === 'completed' && (job.hasTranscription || job.hasSummary) ? (
                    <Link
                      to={`/results/${job.jobId}`}
                      className="group/btn relative px-4 py-2 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-xl font-medium shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 overflow-hidden flex-1 mr-3"
                    >
                      <div className="absolute inset-0 bg-gradient-to-r from-primary-600 to-secondary-600 opacity-0 group-hover/btn:opacity-100 transition-opacity duration-300"></div>
                      <div className="relative flex items-center justify-center space-x-2">
                        <Eye className="h-4 w-4" />
                        <span>Ver Resultados</span>
                      </div>
                      <div className="absolute inset-0 -skew-x-12 bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-0 group-hover/btn:opacity-100 group-hover/btn:animate-shine"></div>
                    </Link>
                  ) : (
                    <div className="flex-1 mr-3 flex items-center justify-center py-2 text-gray-400 text-sm">
                      {job.status === 'processing' ? 'Procesando...' : 'No disponible'}
                    </div>
                  )}
                  
                  <button
                    onClick={() => deleteJob(job.jobId)}
                    disabled={deletingJob === job.jobId}
                    className="w-10 h-10 bg-gradient-to-r from-danger-500 to-warning-500 text-white rounded-xl hover:shadow-lg transition-all duration-300 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                    title="Eliminar trabajo"
                  >
                    {deletingJob === job.jobId ? (
                      <div className="w-4 h-4 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                    ) : (
                      <Trash2 className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>
            ))}
          </div>
      )}

        {/* Summary Stats */}
        {jobs.length > 0 && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 animate-slide-up">
            <div className="glass-effect rounded-3xl p-6 text-center hover:shadow-xl transition-all duration-300 hover:scale-105">
              <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-xl flex items-center justify-center mx-auto mb-4">
                <span className="text-white text-xl">📊</span>
              </div>
              <div className="text-3xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent mb-2">
                {jobs.length}
              </div>
              <div className="text-sm text-gray-600 font-medium">Total de trabajos</div>
            </div>
            
            <div className="glass-effect rounded-3xl p-6 text-center hover:shadow-xl transition-all duration-300 hover:scale-105">
              <div className="w-12 h-12 bg-gradient-to-br from-success-500 to-primary-500 rounded-xl flex items-center justify-center mx-auto mb-4">
                <span className="text-white text-xl">✅</span>
              </div>
              <div className="text-3xl font-bold bg-gradient-to-r from-success-600 to-primary-600 bg-clip-text text-transparent mb-2">
                {jobs.filter(job => job.status === 'completed').length}
              </div>
              <div className="text-sm text-gray-600 font-medium">Completados</div>
            </div>
            
            <div className="glass-effect rounded-3xl p-6 text-center hover:shadow-xl transition-all duration-300 hover:scale-105">
              <div className="w-12 h-12 bg-gradient-to-br from-warning-500 to-secondary-500 rounded-xl flex items-center justify-center mx-auto mb-4">
                <span className="text-white text-xl">⏳</span>
              </div>
              <div className="text-3xl font-bold bg-gradient-to-r from-warning-600 to-secondary-600 bg-clip-text text-transparent mb-2">
                {jobs.filter(job => job.status === 'processing').length}
              </div>
              <div className="text-sm text-gray-600 font-medium">En proceso</div>
            </div>
            
            <div className="glass-effect rounded-3xl p-6 text-center hover:shadow-xl transition-all duration-300 hover:scale-105">
              <div className="w-12 h-12 bg-gradient-to-br from-accent-500 to-primary-500 rounded-xl flex items-center justify-center mx-auto mb-4">
                <span className="text-white text-xl">📝</span>
              </div>
              <div className="text-3xl font-bold bg-gradient-to-r from-accent-600 to-primary-600 bg-clip-text text-transparent mb-2">
                {jobs.filter(job => job.hasTranscription).length}
              </div>
              <div className="text-sm text-gray-600 font-medium">Con transcripción</div>
            </div>
          </div>
        )}
        
        {/* Quick Action */}
        <div className="flex justify-center pt-8">
          <Link
            to="/process"
            className="group relative px-8 py-4 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-2xl font-semibold text-lg shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 overflow-hidden"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-primary-600 to-secondary-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <div className="relative flex items-center space-x-3">
              <span className="text-xl">🎵</span>
              <span>Procesar Nuevo Archivo</span>
            </div>
            <div className="absolute inset-0 -skew-x-12 bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-0 group-hover:opacity-100 group-hover:animate-shine"></div>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default HistoryPage;