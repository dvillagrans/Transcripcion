import React from 'react';
import { Clock, FileAudio, Zap, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';

interface SegmentInfo {
  segment_number: number;
  status: 'pending' | 'processing' | 'completed' | 'error';
  progress: number;
  text?: string;
  duration?: number;
}

interface ProgressData {
  jobId: string;
  status: 'iniciando' | 'transcribiendo' | 'completado' | 'error';
  progress: number;
  stage: string;
  start_time: number;
  estimated_time_remaining?: number;
  current_segment: number;
  total_segments: number;
  processed_duration: number;
  total_duration: number;
  segments?: SegmentInfo[];
  use_segmentation?: boolean;
  optimization_mode?: string;
  parallel_workers?: number;
  model_preloaded?: boolean;
  segment_duration?: number;
}

interface SegmentProgressDisplayProps {
  progressData: ProgressData;
  filename: string;
}

const SegmentProgressDisplay: React.FC<SegmentProgressDisplayProps> = ({
  progressData,
  filename
}) => {
  const {
    status,
    progress,
    stage,
    estimated_time_remaining,
    current_segment,
    total_segments,
    processed_duration,
    total_duration,
    use_segmentation = false
  } = progressData;

  const formatTime = (seconds: number) => {
    if (!seconds || isNaN(seconds) || seconds < 0) return '0s';
    
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
      return `${hours}h ${mins}m ${secs}s`;
    } else if (mins > 0) {
      return `${mins}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };

  const formatTimeRemaining = (minutes?: number) => {
    if (!minutes || isNaN(minutes) || minutes <= 0) return 'Calculando...';
    if (minutes < 1) return 'Menos de 1 minuto';
    if (minutes < 60) return `${Math.ceil(minutes)} minutos`;
    const hours = Math.floor(minutes / 60);
    const mins = Math.ceil(minutes % 60);
    return `${hours}h ${mins > 0 ? mins + 'm' : ''}`;
  };

  const getStatusIcon = (currentStatus: string) => {
    switch (currentStatus) {
      case 'completado':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      case 'transcribiendo':
        return <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />;
      default:
        return <Clock className="h-5 w-5 text-gray-500" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header con información general */}
      <Card className="border-l-4 border-l-blue-500">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <FileAudio className="h-6 w-6 text-blue-500" />
              <div>
                <CardTitle className="text-lg">{filename}</CardTitle>
                <CardDescription>{stage}</CardDescription>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              {getStatusIcon(status)}
              <Badge variant={status === 'completado' ? 'default' : status === 'error' ? 'destructive' : 'secondary'}>
                {status}
              </Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Barra de progreso principal */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="font-medium">Progreso General</span>
              <span className="text-gray-600">{progress}%</span>
            </div>
            <Progress value={progress} className="h-3" />
          </div>

          {/* Información de duración y tiempo */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div className="space-y-1">
              <div className="text-gray-500">Duración Total</div>
              <div className="font-medium">{formatTime(total_duration)}</div>
            </div>
            <div className="space-y-1">
              <div className="text-gray-500">Procesado</div>
              <div className="font-medium">{formatTime(processed_duration)}</div>
            </div>
            <div className="space-y-1">
              <div className="text-gray-500">Tiempo Restante</div>
              <div className="font-medium text-blue-600">
                {formatTimeRemaining(estimated_time_remaining)}
              </div>
            </div>
            <div className="space-y-1">
              <div className="text-gray-500">Método</div>
              <div className="font-medium">
                {use_segmentation ? (
                  <span className="inline-flex items-center space-x-1">
                    <Zap className="h-4 w-4 text-orange-500" />
                    <span>Segmentado</span>
                  </span>
                ) : (
                  <span className="inline-flex items-center space-x-1">
                    <FileAudio className="h-4 w-4 text-blue-500" />
                    <span>Directo</span>
                  </span>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Mostrar progreso de segmentos si está usando segmentación */}
      {use_segmentation && total_segments > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Zap className="h-5 w-5 text-orange-500" />
              <span>Progreso por Segmentos</span>
              <Badge variant="outline">
                {current_segment}/{total_segments}
              </Badge>
            </CardTitle>
            <CardDescription>
              Audio dividido en {total_segments} segmentos de 5 minutos para procesamiento optimizado
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {/* Barra de progreso de segmentos */}
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Segmento {current_segment} de {total_segments}</span>
                  <span>{Math.round((current_segment / total_segments) * 100)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-orange-500 to-amber-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${(current_segment / total_segments) * 100}%` }}
                  />
                </div>
              </div>

              {/* Grid de segmentos individuales */}
              <div className="grid grid-cols-5 md:grid-cols-10 lg:grid-cols-14 gap-2 mt-4">
                {Array.from({ length: total_segments }, (_, i) => {
                  const segmentNum = i + 1;
                  let segmentStatus: 'completed' | 'current' | 'pending' = 'pending';
                  
                  if (segmentNum < current_segment) {
                    segmentStatus = 'completed';
                  } else if (segmentNum === current_segment) {
                    segmentStatus = 'current';
                  }

                  return (
                    <div
                      key={segmentNum}
                      className={`
                        aspect-square rounded-lg border-2 flex items-center justify-center text-xs font-medium
                        transition-all duration-300
                        ${segmentStatus === 'completed' 
                          ? 'bg-green-100 border-green-300 text-green-700' 
                          : segmentStatus === 'current'
                          ? 'bg-blue-100 border-blue-300 text-blue-700 animate-pulse' 
                          : 'bg-gray-100 border-gray-300 text-gray-500'
                        }
                      `}
                      title={`Segmento ${segmentNum} (${(segmentNum - 1) * 5}-${Math.min(segmentNum * 5, Math.ceil(total_duration / 60))} min)`}
                    >
                      {segmentStatus === 'completed' ? (
                        <CheckCircle className="h-3 w-3" />
                      ) : segmentStatus === 'current' ? (
                        <Loader2 className="h-3 w-3 animate-spin" />
                      ) : (
                        segmentNum
                      )}
                    </div>
                  );
                })}
              </div>

              {/* Leyenda */}
              <div className="flex items-center justify-center space-x-6 text-xs text-gray-600 pt-3 border-t">
                <div className="flex items-center space-x-1">
                  <div className="w-3 h-3 bg-green-100 border border-green-300 rounded"></div>
                  <span>Completado</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-3 h-3 bg-blue-100 border border-blue-300 rounded animate-pulse"></div>
                  <span>Procesando</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-3 h-3 bg-gray-100 border border-gray-300 rounded"></div>
                  <span>Pendiente</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Información técnica adicional */}
      <Card className="bg-gray-50">
        <CardHeader>
          <CardTitle className="text-sm text-gray-700">Información Técnica</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-xs">
            <div>
              <div className="text-gray-500">Job ID</div>
              <div className="font-mono text-gray-700 break-all">{progressData.jobId}</div>
            </div>
            <div>
              <div className="text-gray-500">Velocidad de Procesamiento</div>
              <div className="font-medium">
                {processed_duration > 0 
                  ? `${(processed_duration / ((Date.now() / 1000) - progressData.start_time)).toFixed(1)}x tiempo real`
                  : 'Calculando...'
                }
              </div>
            </div>
            <div>
              <div className="text-gray-500">Método de Procesamiento</div>
              <div className="font-medium">
                {use_segmentation ? `Segmentación (${progressData.segment_duration || 10} min)` : 'Transcripción directa'}
              </div>
            </div>
          </div>

          {/* Información de optimización */}
          {progressData.optimization_mode && (
            <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200">
              <CardContent className="p-4">
                <div className="flex items-center space-x-2 mb-3">
                  <Zap className="h-4 w-4 text-blue-600" />
                  <span className="font-semibold text-blue-800">
                    Optimizaciones para 32GB RAM Activadas
                  </span>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                  <div className="space-y-1">
                    <div className="text-gray-600">Modo</div>
                    <Badge variant="secondary" className="text-xs">
                      {progressData.optimization_mode === 'high_memory' ? '🚀 Alto Rendimiento' : '⚡ Estándar'}
                    </Badge>
                  </div>
                  <div className="space-y-1">
                    <div className="text-gray-600">Workers Paralelos</div>
                    <div className="font-medium text-blue-700">
                      {progressData.parallel_workers || 1}x
                    </div>
                  </div>
                  <div className="space-y-1">
                    <div className="text-gray-600">Modelo Precargado</div>
                    <div className="font-medium">
                      {progressData.model_preloaded ? '✅ Sí' : '⏳ No'}
                    </div>
                  </div>
                  <div className="space-y-1">
                    <div className="text-gray-600">Duración Segmento</div>
                    <div className="font-medium text-green-700">
                      {progressData.segment_duration || 10} min
                    </div>
                  </div>
                </div>
                <div className="mt-3 text-xs text-gray-600">
                  🎯 Rendimiento esperado: ~3x más rápido que modo estándar
                </div>
              </CardContent>
            </Card>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default SegmentProgressDisplay;