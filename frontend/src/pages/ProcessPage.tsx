import React, { useState, useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileAudio, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import SegmentProgressDisplay from '@/components/SegmentProgressDisplay';
import LanguageSelector from '@/components/LanguageSelector';

interface ProcessingJob {
  jobId: string;
  filename: string;
  status: 'processing' | 'completed' | 'error';
  progress: number;
  currentStage: string;
  // Agregar campos adicionales para progreso detallado
  estimated_time_remaining?: number;
  current_segment?: number;
  total_segments?: number;
  processed_duration?: number;
  total_duration?: number;
  use_segmentation?: boolean;
  start_time?: number;
}

const ProcessPage: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [currentJob, setCurrentJob] = useState<ProcessingJob | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedLanguage, setSelectedLanguage] = useState<string>('es');
  const [generateSummary, setGenerateSummary] = useState(false);
  const navigate = useNavigate();

  // Cargar configuración guardada al montar el componente
  useEffect(() => {
    const config = JSON.parse(localStorage.getItem('audioProcessingConfig') || '{}');
    if (config.language) {
      setSelectedLanguage(config.language);
    }
  }, []);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setSelectedFile(acceptedFiles[0]);
      setError(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'audio/*': ['.mp3', '.wav', '.flac', '.m4a', '.ogg']
    },
    maxFiles: 1,
    maxSize: 100 * 1024 * 1024, // 100MB
    onDropRejected: (rejectedFiles) => {
      const rejection = rejectedFiles[0];
      if (rejection.errors[0]?.code === 'file-too-large') {
        setError('El archivo es demasiado grande. Máximo 100MB.');
      } else if (rejection.errors[0]?.code === 'file-invalid-type') {
        setError('Tipo de archivo no soportado. Use MP3, WAV, FLAC, M4A u OGG.');
      } else {
        setError('Error al cargar el archivo.');
      }
    }
  });

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('audioFile', selectedFile);
      
      // Get config from localStorage
      const config = JSON.parse(localStorage.getItem('audioProcessingConfig') || '{}');
      formData.append('whisperModel', config.whisperModel || 'medium');
      formData.append('language', selectedLanguage || config.language || 'es');
      formData.append('generateSummary', String(generateSummary));

      const response = await fetch('/api/audio/upload', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (result.success) {
        const job: ProcessingJob = {
          jobId: result.data.jobId,
          filename: result.data.filename,
          status: result.data.status,
          progress: 0,
          currentStage: 'Iniciando procesamiento'
        };
        setCurrentJob(job);
        startPolling(job.jobId);
      } else {
        setError(result.error || 'Error al subir el archivo');
      }
    } catch (err) {
      setError('Error de conexión. Verifique que el servidor esté ejecutándose.');
    } finally {
      setIsUploading(false);
    }
  };

  const startPolling = (jobId: string) => {
    const pollInterval = setInterval(async () => {
      try {
        // Obtener estado del backend Express (que ahora incluye datos del servicio Python)
        const response = await fetch(`/api/audio/status/${jobId}`);
        const result = await response.json();

        if (result.success) {
          const updatedJob: ProcessingJob = {
            jobId,
            filename: currentJob?.filename || '',
            status: result.data.status,
            progress: result.data.progress,
            currentStage: result.data.currentStage,
            estimated_time_remaining: result.data.estimated_time_remaining,
            current_segment: result.data.current_segment,
            total_segments: result.data.total_segments,
            processed_duration: result.data.processed_duration,
            total_duration: result.data.total_duration,
            use_segmentation: result.data.use_segmentation,
            start_time: result.data.start_time
          };
          setCurrentJob(updatedJob);

          if (result.data.status === 'completed' || result.data.status === 'error') {
            clearInterval(pollInterval);
            if (result.data.status === 'completed') {
              setTimeout(() => {
                navigate(`/results/${jobId}`);
              }, 2000);
            }
          }
        }
      } catch (err) {
        console.error('Error polling status:', err);
      }
    }, 2000);
  };

  const resetForm = () => {
    setSelectedFile(null);
    setCurrentJob(null);
    setError(null);
    setIsUploading(false);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 p-6">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-4 animate-fade-in">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-2xl shadow-lg mb-4">
            <FileAudio className="h-10 w-10 text-white" />
          </div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
            Procesamiento de Audio
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Transforma tu audio en texto con tecnología de IA avanzada. Sube tu archivo y obtén transcripciones precisas al instante.
          </p>
        </div>

        {/* Upload Section */}
        {!currentJob && (
          <Card className="glass-effect rounded-3xl animate-slide-up">
            <CardHeader className="text-center">
              <CardTitle className="text-2xl font-bold text-gray-800">Subir Archivo de Audio</CardTitle>
              <CardDescription className="text-gray-600">Arrastra tu archivo o haz clic para seleccionar</CardDescription>
            </CardHeader>
            <CardContent>
            
            {/* Dropzone */}
            <div
              {...getRootProps()}
              className={`relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-300 group ${
                isDragActive
                  ? 'border-primary-400 bg-gradient-to-br from-primary-50 to-secondary-50 scale-105 shadow-xl'
                  : 'border-gray-300 hover:border-primary-400 hover:bg-gradient-to-br hover:from-primary-50 hover:to-secondary-50 hover:scale-102 hover:shadow-lg'
              }`}
            >
              <input {...getInputProps()} />
              <div className="relative z-10">
                <div className={`mx-auto w-16 h-16 rounded-full flex items-center justify-center mb-6 transition-all duration-300 ${
                  isDragActive 
                    ? 'bg-gradient-to-br from-primary-500 to-secondary-500 shadow-lg scale-110' 
                    : 'bg-gradient-to-br from-gray-400 to-gray-500 group-hover:from-primary-500 group-hover:to-secondary-500 group-hover:shadow-lg group-hover:scale-110'
                }`}>
                  <Upload className="h-8 w-8 text-white" />
                </div>
                {isDragActive ? (
                  <div className="space-y-2">
                    <p className="text-xl font-semibold text-primary-600 animate-pulse">¡Suelta el archivo aquí!</p>
                    <p className="text-primary-500">Procesaremos tu audio al instante</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <p className="text-xl font-semibold text-gray-700 group-hover:text-primary-600 transition-colors">
                      Arrastra y suelta tu archivo de audio
                    </p>
                    <p className="text-gray-500 group-hover:text-primary-500 transition-colors">
                      o haz clic para seleccionar desde tu dispositivo
                    </p>
                    <div className="flex flex-wrap justify-center gap-2 mt-4">
                      {['MP3', 'WAV', 'FLAC', 'M4A', 'OGG'].map((format) => (
                        <span key={format} className="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm font-medium group-hover:bg-primary-100 group-hover:text-primary-600 transition-colors">
                          {format}
                        </span>
                      ))}
                    </div>
                    <p className="text-xs text-gray-400 mt-2">Máximo 100MB</p>
                  </div>
                )}
              </div>
              
              {/* Animated background */}
              <div className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <div className="absolute inset-0 bg-gradient-to-r from-primary-400/10 to-secondary-400/10 rounded-2xl animate-pulse"></div>
              </div>
            </div>

            {/* Selected File Info */}
            {selectedFile && (
              <Card className="mt-8 bg-gradient-to-r from-success-50 to-primary-50 border border-success-200 animate-slide-up">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 bg-gradient-to-br from-success-500 to-primary-500 rounded-xl flex items-center justify-center shadow-lg">
                        <FileAudio className="h-6 w-6 text-white" />
                      </div>
                      <div>
                        <p className="font-semibold text-gray-800 text-lg">{selectedFile.name}</p>
                        <div className="flex items-center space-x-2 mt-1">
                          <Badge variant="secondary" className="bg-white text-xs">
                            {formatFileSize(selectedFile.size)}
                          </Badge>
                          <Badge variant="secondary" className="bg-white text-xs">
                            {selectedFile.type.split('/')[1]?.toUpperCase() || 'AUDIO'}
                          </Badge>
                        </div>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => setSelectedFile(null)}
                      className="w-8 h-8 bg-white rounded-full text-gray-400 hover:text-gray-600 hover:bg-gray-50 shadow-sm hover:shadow-md"
                    >
                      ✕
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Error Message */}
            {error && (
              <Alert variant="destructive" className="mt-6 bg-gradient-to-r from-danger-50 to-warning-50 border border-danger-200 animate-slide-up">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Error al procesar archivo</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {/* Language Selector */}
            {selectedFile && !currentJob && (
              <Card className="mt-6 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 animate-slide-up">
                <CardContent className="p-6">
                  <div className="max-w-sm mx-auto">
                    <LanguageSelector
                      value={selectedLanguage}
                      onChange={setSelectedLanguage}
                      className="space-y-3"
                    />
                  </div>
                </CardContent>
              </Card>
            )}

            {/* AI Summary Option */}
            {selectedFile && !currentJob && (
              <Card className="mt-6 bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 animate-slide-up">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between max-w-sm mx-auto">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center shadow-lg">
                        <span className="text-white text-sm">🤖</span>
                      </div>
                      <div>
                        <label htmlFor="generateSummary" className="text-lg font-semibold text-gray-800 cursor-pointer">
                          Generar Resumen AI
                        </label>
                        <p className="text-sm text-gray-600">Crear un resumen inteligente del contenido</p>
                      </div>
                    </div>
                    <div className="relative">
                      <input
                        id="generateSummary"
                        type="checkbox"
                        checked={generateSummary}
                        onChange={(e) => setGenerateSummary(e.target.checked)}
                        className="sr-only"
                      />
                      <label 
                        htmlFor="generateSummary" 
                        className={`block w-12 h-6 rounded-full cursor-pointer transition-all duration-300 ${
                          generateSummary 
                            ? 'bg-gradient-to-r from-purple-500 to-pink-500 shadow-lg' 
                            : 'bg-gray-300 hover:bg-gray-400'
                        }`}
                      >
                        <div 
                          className={`w-5 h-5 bg-white rounded-full shadow-md transform transition-transform duration-300 mt-0.5 ${
                            generateSummary ? 'translate-x-6' : 'translate-x-0.5'
                          }`}
                        />
                      </label>
                    </div>
                  </div>
                  {generateSummary && (
                    <div className="mt-4 p-3 bg-white rounded-xl border border-purple-200 animate-fade-in">
                      <p className="text-sm text-purple-700 flex items-center space-x-2">
                        <span className="text-purple-500">✨</span>
                        <span>Se generará un resumen inteligente usando IA que destacará los puntos clave del contenido.</span>
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Upload Button */}
            <div className="mt-8 flex justify-center">
              <Button
                onClick={handleUpload}
                disabled={!selectedFile || isUploading}
                size="lg"
                className="group relative px-8 py-4 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-2xl font-semibold text-lg shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 disabled:hover:scale-100 overflow-hidden"
              >
                {/* Animated background */}
                <div className="absolute inset-0 bg-gradient-to-r from-primary-600 to-secondary-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                
                {/* Button content */}
                <div className="relative flex items-center space-x-3">
                  {isUploading ? (
                    <>
                      <Loader2 className="h-6 w-6 animate-spin" />
                      <span>Procesando Audio...</span>
                      <div className="w-2 h-2 bg-white rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    </>
                  ) : (
                    <>
                      <Upload className="h-6 w-6 group-hover:scale-110 transition-transform duration-200" />
                      <span>Procesar Audio</span>
                      <div className="w-2 h-2 bg-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-200"></div>
                    </>
                  )}
                </div>
                
                {/* Shine effect */}
                <div className="absolute inset-0 -skew-x-12 bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-0 group-hover:opacity-100 group-hover:animate-shine"></div>
              </Button>
            </div>
            </CardContent>
          </Card>
        )}

        {/* Processing Status */}
        {currentJob && (
          <div className="animate-slide-up">
            <SegmentProgressDisplay 
              progressData={{
                jobId: currentJob.jobId,
                status: currentJob.status === 'processing' ? 'transcribiendo' : 
                        currentJob.status === 'completed' ? 'completado' : 'error',
                progress: currentJob.progress,
                stage: currentJob.currentStage,
                start_time: currentJob.start_time || Date.now() / 1000,
                estimated_time_remaining: currentJob.estimated_time_remaining,
                current_segment: currentJob.current_segment || 0,
                total_segments: currentJob.total_segments || 0,
                processed_duration: currentJob.processed_duration || 0,
                total_duration: currentJob.total_duration || 0,
                use_segmentation: currentJob.use_segmentation || false
              }}
              filename={currentJob.filename}
            />
            
            {/* Actions */}
            <div className="mt-6 flex justify-center space-x-4">
              {currentJob.status === 'completed' && (
                <button
                  onClick={() => navigate(`/results/${currentJob.jobId}`)}
                  className="group relative px-8 py-4 bg-gradient-to-r from-green-500 to-blue-500 text-white rounded-2xl font-semibold text-lg shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 overflow-hidden"
                >
                  <div className="relative flex items-center space-x-3">
                    <CheckCircle className="h-6 w-6 group-hover:scale-110 transition-transform duration-200" />
                    <span>Ver Resultados</span>
                  </div>
                </button>
              )}

              {currentJob.status === 'error' && (
                <button
                  onClick={resetForm}
                  className="group relative px-8 py-4 bg-gradient-to-r from-red-500 to-orange-500 text-white rounded-2xl font-semibold text-lg shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105"
                >
                  <div className="relative flex items-center space-x-3">
                    <AlertCircle className="h-6 w-6 group-hover:scale-110 transition-transform duration-200" />
                    <span>Intentar de Nuevo</span>
                  </div>
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProcessPage;