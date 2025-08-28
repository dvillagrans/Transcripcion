import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { FileText, Download, ArrowLeft, Copy, CheckCircle, AlertCircle } from 'lucide-react';

interface JobResult {
  jobId: string;
  filename: string;
  status: string;
  transcription: string;
  summary: string;
  createdAt: string;
}

const ResultsPage: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const [result, setResult] = useState<JobResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState<'transcription' | 'summary' | null>(null);

  useEffect(() => {
    if (jobId) {
      fetchResults(jobId);
    }
  }, [jobId]);

  const fetchResults = async (id: string) => {
    try {
      const response = await fetch(`/api/audio/results/${id}`);
      const data = await response.json();

      if (data.success) {
        setResult(data.data);
      } else {
        setError(data.error || 'Error al cargar los resultados');
      }
    } catch (err) {
      setError('Error de conexión');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async (text: string, type: 'transcription' | 'summary') => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(type);
      setTimeout(() => setCopied(null), 2000);
    } catch (err) {
      console.error('Error copying to clipboard:', err);
    }
  };

  const downloadText = (text: string, filename: string) => {
    const element = document.createElement('a');
    const file = new Blob([text], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = filename;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 flex items-center justify-center p-6">
        <div className="glass-effect rounded-3xl p-12 text-center animate-fade-in">
          <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-2xl flex items-center justify-center mx-auto mb-6 animate-pulse">
            <FileText className="h-8 w-8 text-white" />
          </div>
          <div className="loading-spinner mx-auto mb-6"></div>
          <h3 className="text-xl font-semibold text-gray-800 mb-2">Cargando Resultados</h3>
          <p className="text-gray-600">Preparando tu transcripción...</p>
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
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Oops! Algo salió mal</h2>
          <p className="text-gray-600 mb-8">{error}</p>
          <Link
            to="/process"
            className="group relative px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-2xl font-semibold shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 overflow-hidden"
          >
            {/* Animated background */}
            <div className="absolute inset-0 bg-gradient-to-r from-primary-600 to-secondary-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            
            {/* Button content */}
            <div className="relative flex items-center space-x-3">
              <ArrowLeft className="h-5 w-5 group-hover:scale-110 transition-transform duration-200" />
              <span>Volver al Procesamiento</span>
            </div>
            
            {/* Shine effect */}
            <div className="absolute inset-0 -skew-x-12 bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-0 group-hover:opacity-100 group-hover:animate-shine"></div>
          </Link>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">No se encontraron resultados</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 p-6">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-4 animate-fade-in">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-success-500 to-primary-500 rounded-2xl shadow-lg mb-4">
            <FileText className="h-10 w-10 text-white" />
          </div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-success-600 to-primary-600 bg-clip-text text-transparent">
            ¡Transcripción Completada!
          </h1>
          <div className="bg-white rounded-2xl p-6 shadow-lg border border-success-200 max-w-2xl mx-auto">
            <p className="text-lg font-semibold text-gray-800">{result.filename}</p>
            <p className="text-gray-600 mt-1">Procesado el {formatDate(result.createdAt)}</p>
          </div>
        </div>

        {/* Status */}
        <div className="flex justify-center animate-slide-up">
          {result.status === 'completed' ? (
            <div className="flex items-center space-x-3 px-8 py-4 bg-gradient-to-r from-success-100 to-primary-100 rounded-2xl border border-success-200">
              <CheckCircle className="h-6 w-6 text-success-600" />
              <span className="text-success-700 font-semibold text-lg">¡Procesamiento Completado!</span>
              <div className="w-2 h-2 bg-success-500 rounded-full animate-ping"></div>
            </div>
          ) : (
            <div className="flex items-center space-x-3 px-8 py-4 bg-gradient-to-r from-warning-100 to-secondary-100 rounded-2xl border border-warning-200">
              <AlertCircle className="h-6 w-6 text-warning-600" />
              <span className="text-warning-700 font-semibold text-lg">Estado: {result.status}</span>
            </div>
          )}
        </div>

        {/* Transcription */}
        {result.transcription && (
          <div className="glass-effect rounded-3xl p-8 animate-slide-up">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-xl flex items-center justify-center">
                  <FileText className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-gray-800">📝 Transcripción</h2>
                  <p className="text-gray-600">Texto completo extraído del audio</p>
                </div>
              </div>
              <div className="flex space-x-3">
                <button
                  onClick={() => copyToClipboard(result.transcription, 'transcription')}
                  className={`group relative px-4 py-2 rounded-xl font-medium transition-all duration-300 hover:scale-105 ${
                    copied === 'transcription'
                      ? 'bg-gradient-to-r from-success-500 to-primary-500 text-white shadow-lg'
                      : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200 hover:shadow-md'
                  }`}
                >
                  <div className="flex items-center space-x-2">
                    {copied === 'transcription' ? (
                      <>
                        <CheckCircle className="h-4 w-4" />
                        <span>¡Copiado!</span>
                      </>
                    ) : (
                      <>
                        <Copy className="h-4 w-4 group-hover:scale-110 transition-transform" />
                        <span>Copiar</span>
                      </>
                    )}
                  </div>
                </button>
                <button
                  onClick={() => downloadText(result.transcription, `transcripcion_${result.filename}.txt`)}
                  className="group relative px-4 py-2 bg-gradient-to-r from-accent-500 to-primary-500 text-white rounded-xl font-medium shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 overflow-hidden"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-accent-600 to-primary-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  <div className="relative flex items-center space-x-2">
                    <Download className="h-4 w-4 group-hover:scale-110 transition-transform" />
                    <span>Descargar</span>
                  </div>
                  <div className="absolute inset-0 -skew-x-12 bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-0 group-hover:opacity-100 group-hover:animate-shine"></div>
                </button>
              </div>
            </div>
            <div className="bg-gradient-to-br from-gray-50 to-primary-50 rounded-2xl p-6 border border-gray-200 max-h-96 overflow-y-auto">
              <p className="text-gray-800 whitespace-pre-wrap leading-relaxed text-lg">
                {result.transcription}
              </p>
            </div>
          </div>
        )}

        {/* Summary */}
        {result.summary && (
          <div className="glass-effect rounded-3xl p-8 animate-slide-up">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-gradient-to-br from-secondary-500 to-accent-500 rounded-xl flex items-center justify-center">
                  <span className="text-white text-xl">🤖</span>
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-gray-800">✨ Resumen Inteligente</h2>
                  <p className="text-gray-600">Puntos clave generados por IA</p>
                </div>
              </div>
              <div className="flex space-x-3">
                <button
                  onClick={() => copyToClipboard(result.summary, 'summary')}
                  className={`group relative px-4 py-2 rounded-xl font-medium transition-all duration-300 hover:scale-105 ${
                    copied === 'summary'
                      ? 'bg-gradient-to-r from-success-500 to-primary-500 text-white shadow-lg'
                      : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200 hover:shadow-md'
                  }`}
                >
                  <div className="flex items-center space-x-2">
                    {copied === 'summary' ? (
                      <>
                        <CheckCircle className="h-4 w-4" />
                        <span>¡Copiado!</span>
                      </>
                    ) : (
                      <>
                        <Copy className="h-4 w-4 group-hover:scale-110 transition-transform" />
                        <span>Copiar</span>
                      </>
                    )}
                  </div>
                </button>
                <button
                  onClick={() => downloadText(result.summary, `resumen_${result.filename}.txt`)}
                  className="group relative px-4 py-2 bg-gradient-to-r from-secondary-500 to-accent-500 text-white rounded-xl font-medium shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 overflow-hidden"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-secondary-600 to-accent-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  <div className="relative flex items-center space-x-2">
                    <Download className="h-4 w-4 group-hover:scale-110 transition-transform" />
                    <span>Descargar</span>
                  </div>
                  <div className="absolute inset-0 -skew-x-12 bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-0 group-hover:opacity-100 group-hover:animate-shine"></div>
                </button>
              </div>
            </div>
            <div className="bg-gradient-to-br from-secondary-50 to-accent-50 rounded-2xl p-6 border border-secondary-200">
              <p className="text-gray-800 whitespace-pre-wrap leading-relaxed text-lg">
                {result.summary}
              </p>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-8">
          <Link
            to="/process"
            className="group relative px-8 py-4 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-2xl font-semibold text-lg shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 overflow-hidden"
          >
            {/* Animated background */}
            <div className="absolute inset-0 bg-gradient-to-r from-primary-600 to-secondary-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            
            {/* Button content */}
            <div className="relative flex items-center space-x-3">
              <span className="text-xl">🎵</span>
              <span>Procesar Nuevo Archivo</span>
            </div>
            
            {/* Shine effect */}
            <div className="absolute inset-0 -skew-x-12 bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-0 group-hover:opacity-100 group-hover:animate-shine"></div>
          </Link>
          
          <Link
            to="/history"
            className="group relative px-8 py-4 bg-gradient-to-r from-gray-500 to-gray-600 text-white rounded-2xl font-semibold text-lg shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 overflow-hidden"
          >
            {/* Animated background */}
            <div className="absolute inset-0 bg-gradient-to-r from-gray-600 to-gray-700 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            
            {/* Button content */}
            <div className="relative flex items-center space-x-3">
              <span className="text-xl">📚</span>
              <span>Ver Historial</span>
            </div>
            
            {/* Shine effect */}
            <div className="absolute inset-0 -skew-x-12 bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-0 group-hover:opacity-100 group-hover:animate-shine"></div>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ResultsPage;