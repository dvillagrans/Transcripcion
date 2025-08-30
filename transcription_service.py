#!/usr/bin/env python3
"""
Servicio de Transcripción con Faster-Whisper
Procesa archivos de audio y genera transcripciones usando modelos Whisper optimizados.
"""

import os
import sys
import json
import time
import signal
import traceback
from pathlib import Path
from typing import Dict, Any, Optional

from flask import Flask, request, jsonify
from flask_cors import CORS
from faster_whisper import WhisperModel
from loguru import logger
import filetype
import librosa
import soundfile as sf
import torch
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
CORS(app)

# Almacén global para el progreso de transcripciones
transcription_progress = {}

# Configuración
def get_device_config():
    """Configurar dispositivo y parámetros de procesamiento optimizados para audios largos"""
    try:
        # Verificar CUDA disponible
        if not torch.cuda.is_available():
            logger.warning("CUDA no disponible, usando CPU")
            return {
                'device': 'cpu',
                'compute_type': 'float32',
                'cpu_threads': min(8, os.cpu_count() or 4),
                'num_workers': 1
            }
        
        # Información de GPU
        gpu_count = torch.cuda.device_count()
        current_device = torch.cuda.current_device()
        gpu_name = torch.cuda.get_device_name(current_device)
        gpu_memory = torch.cuda.get_device_properties(current_device).total_memory / (1024**3)
        
        logger.info(f"GPU detectada: {gpu_name} ({gpu_memory:.1f}GB)")
        
        # Probar cuDNN si está habilitado
        force_cpu = os.getenv('FORCE_CPU', 'false').lower() == 'true'
        if force_cpu:
            logger.info("FORCE_CPU activado, usando CPU")
            return {
                'device': 'cpu',
                'compute_type': 'float32',
                'cpu_threads': min(8, os.cpu_count() or 4),
                'num_workers': 1
            }
        
        # En modo robusto, usar CPU directamente si hay problemas conocidos
        robust_mode = os.getenv('ROBUST_MODE', 'false').lower() == 'true'
        if robust_mode:
            logger.info("🛡️ ROBUST_MODE activado: usando CPU para máxima estabilidad")
            return {
                'device': 'cpu',
                'compute_type': 'float32',
                'cpu_threads': min(8, os.cpu_count() or 4),
                'num_workers': 1
            }
        
        # Probar cuDNN solo si no estamos en modo robusto
        try:
            # Test básico de cuDNN con timeout
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("Timeout en prueba cuDNN")
            
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(5)  # 5 segundos de timeout
            
            try:
                x = torch.randn(1, 1, 4, 4, device='cuda')
                conv = torch.nn.Conv2d(1, 1, 3, padding=1).cuda()
                _ = conv(x)
                torch.cuda.synchronize()
                signal.alarm(0)  # Cancelar timeout
                
                logger.info("✅ Prueba de cuDNN exitosa, usando GPU")
                return {
                    'device': 'cuda',
                    'compute_type': 'float16',
                    'cpu_threads': 0,
                    'num_workers': 1
                }
            finally:
                signal.signal(signal.SIGALRM, old_handler)
                signal.alarm(0)
            
        except Exception as cudnn_error:
            logger.warning(f"⚠️ Error en cuDNN: {cudnn_error}")
            logger.info("Cayendo a CPU por problemas de cuDNN")
            return {
                'device': 'cpu',
                'compute_type': 'float32',
                'cpu_threads': min(8, os.cpu_count() or 4),
                'num_workers': 1
            }
            
    except Exception as e:
        logger.error(f"Error configurando dispositivo: {e}")
        return {
            'device': 'cpu',
            'compute_type': 'float32',
            'cpu_threads': min(8, os.cpu_count() or 4),
            'num_workers': 1
        }

device_config = get_device_config()
device = device_config['device']
compute_type = device_config['compute_type']

# Permitir forzar CPU a través de variable de entorno
if os.getenv('FORCE_CPU', '').lower() in ['true', '1', 'yes']:
    logger.info("🔧 Forzando uso de CPU por variable de entorno FORCE_CPU")
    device, compute_type = 'cpu', 'int8'

# Modo robusto para archivos largos (usa configuración más conservadora)
ROBUST_MODE = os.getenv('ROBUST_MODE', 'true').lower() in ['true', '1', 'yes']

CONFIG = {
    'models_dir': './models',
    'uploads_dir': './uploads',
    'supported_formats': ['.mp3', '.wav', '.flac', '.m4a', '.ogg'],
    'max_file_size': 500 * 1024 * 1024,  # 500MB para archivos largos
    'default_model': 'medium',
    'device': device,
    'compute_type': compute_type,
    'robust_mode': ROBUST_MODE
}

# Logger configuration
logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
logger.add("transcription.log", rotation="10 MB", level="DEBUG")

class TranscriptionService:
    """Servicio de transcripción con Faster-Whisper"""
    
    def __init__(self):
        self.models = {}
        self.ensure_directories()
        
    def ensure_directories(self):
        """Crear directorios necesarios"""
        Path(CONFIG['models_dir']).mkdir(exist_ok=True)
        Path(CONFIG['uploads_dir']).mkdir(exist_ok=True)
        
    def get_model(self, model_name: str = None) -> WhisperModel:
        """Obtener o cargar modelo Whisper"""
        if model_name is None:
            model_name = CONFIG['default_model']
            
        if model_name not in self.models:
            logger.info(f"Cargando modelo Whisper: {model_name} en {CONFIG['device']}")
            try:
                self.models[model_name] = WhisperModel(
                    model_name,
                    device=CONFIG['device'],
                    compute_type=CONFIG['compute_type'],
                    download_root=CONFIG['models_dir']
                )
                logger.success(f"Modelo {model_name} cargado exitosamente en {CONFIG['device']}")
            except Exception as e:
                logger.error(f"Error cargando modelo {model_name}: {e}")
                # Intentar fallback a CPU si falla GPU
                if CONFIG['device'] == 'cuda':
                    logger.info("Intentando fallback a CPU...")
                    try:
                        self.models[model_name] = WhisperModel(
                            model_name,
                            device='cpu',
                            compute_type='int8',
                            download_root=CONFIG['models_dir']
                        )
                        logger.success(f"Modelo {model_name} cargado en CPU como fallback")
                        # Actualizar configuración global para futuros modelos
                        CONFIG['device'] = 'cpu'
                        CONFIG['compute_type'] = 'int8'
                    except Exception as cpu_error:
                        logger.error(f"Error también en CPU: {cpu_error}")
                        raise
                else:
                    raise
                
        return self.models[model_name]
    
    def validate_audio_file(self, file_path: str) -> Dict[str, Any]:
        """Validar archivo de audio"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
            
        # Verificar tamaño
        file_size = os.path.getsize(file_path)
        if file_size > CONFIG['max_file_size']:
            raise ValueError(f"Archivo demasiado grande: {file_size / 1024 / 1024:.1f}MB")
            
        # Verificar formato
        file_ext = Path(file_path).suffix.lower()
        if file_ext not in CONFIG['supported_formats']:
            raise ValueError(f"Formato no soportado: {file_ext}")
            
        # Obtener información del audio
        try:
            duration = librosa.get_duration(path=file_path)
            sample_rate = librosa.get_samplerate(file_path)
            
            return {
                'file_path': file_path,
                'file_size': file_size,
                'duration': duration,
                'sample_rate': sample_rate,
                'format': file_ext
            }
        except Exception as e:
            raise ValueError(f"Error leyendo archivo de audio: {e}")
    
    def preprocess_audio(self, file_path: str) -> str:
        """Preprocesar archivo de audio si es necesario"""
        try:
            # Cargar audio
            audio, sr = librosa.load(file_path, sr=16000)  # Whisper usa 16kHz
            
            # Si el archivo ya está en formato correcto, devolverlo
            if sr == 16000 and file_path.endswith('.wav'):
                return file_path
                
            # Crear archivo temporal procesado
            processed_path = file_path.replace(Path(file_path).suffix, '_processed.wav')
            sf.write(processed_path, audio, 16000)
            
            logger.info(f"Audio preprocesado: {processed_path}")
            return processed_path
            
        except Exception as e:
            logger.error(f"Error preprocesando audio: {e}")
            return file_path  # Devolver original si falla
    
    def transcribe_audio(self, file_path: str, job_id: str = None, model_name: str = None, 
                        language: str = None, generate_summary: bool = False) -> Dict[str, Any]:
        """Transcribir archivo de audio con seguimiento de progreso"""
        start_time = time.time()
        
        # Generar ID único si no se proporciona
        if not job_id:
            job_id = f"job_{int(time.time() * 1000)}_{os.path.basename(file_path)}"
        
        # Inicializar progreso
        transcription_progress[job_id] = {
            'status': 'iniciando',
            'progress': 0,
            'stage': 'Validando archivo...',
            'start_time': start_time,
            'estimated_time_remaining': None,
            'current_segment': 0,
            'total_segments': 0,
            'processed_duration': 0,
            'total_duration': 0
        }
        
        try:
            # Validar archivo
            transcription_progress[job_id].update({
                'stage': 'Validando archivo de audio...',
                'progress': 5
            })
            audio_info = self.validate_audio_file(file_path)
            logger.info(f"Transcribiendo: {audio_info['file_path']} ({audio_info['duration']:.1f}s)")
            
            transcription_progress[job_id].update({
                'total_duration': audio_info['duration'],
                'stage': 'Preprocesando audio...',
                'progress': 10
            })
            
            # Preprocesar audio
            processed_path = self.preprocess_audio(file_path)
            logger.info(f"Audio preprocesado: {processed_path}")
            
            transcription_progress[job_id].update({
                'stage': 'Cargando modelo...',
                'progress': 20
            })
            
            # Obtener modelo
            model = self.get_model(model_name)
            
            # Limpiar memoria GPU antes de transcripción larga
            if CONFIG['device'] == 'cuda':
                try:
                    import torch
                    torch.cuda.empty_cache()
                    logger.info("Memoria GPU limpiada antes de transcripción")
                except:
                    pass
            
            transcription_progress[job_id].update({
                'stage': 'Iniciando transcripción...',
                'progress': 25,
                'status': 'transcribiendo'
            })
            
            # Intentar transcripción con manejo de errores robusto
            max_retries = 2 if CONFIG['robust_mode'] else 1
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    if attempt > 0:
                        logger.info(f"Reintentando transcripción (intento {attempt + 1}/{max_retries})")
                        transcription_progress[job_id].update({
                            'stage': f'Reintentando transcripción (intento {attempt + 1})...',
                        })
                        
                        # En reintento, forzar CPU si el primer intento falló con GPU
                        if CONFIG['device'] == 'cuda' and attempt == 1:
                            logger.info("🔄 Cambiando a CPU para mayor estabilidad en archivo largo")
                            model = self.get_model(model_name)  # Recargar modelo, puede usar CPU fallback
                    
                    # Configurar parámetros según el dispositivo y modo robusto
                    if CONFIG['device'] == 'cuda' and not CONFIG['robust_mode']:
                        # Configuración optimizada para GPU
                        beam_size, best_of = 3, 3
                        vad_params = dict(
                            min_silence_duration_ms=1000,
                            threshold=0.5,
                            min_speech_duration_ms=250,
                            max_speech_duration_s=float('inf')
                        )
                    else:
                        # Configuración conservadora para CPU o modo robusto
                        beam_size, best_of = 1, 1
                        vad_params = dict(
                            min_silence_duration_ms=500,
                            threshold=0.5,
                            min_speech_duration_ms=250
                        )
                    
                    # Transcribir con configuración adaptativa
                    segments, info = model.transcribe(
                        processed_path,
                        language=language,
                        beam_size=beam_size,
                        best_of=best_of,
                        temperature=0.0,
                        condition_on_previous_text=False,
                        vad_filter=True,
                        vad_parameters=vad_params,
                        word_timestamps=True,
                        compression_ratio_threshold=2.4,
                        log_prob_threshold=-1.0,
                        no_speech_threshold=0.6
                    )
                    
                    # Si llegamos aquí, la transcripción fue exitosa
                    break
                    
                except Exception as e:
                    last_error = e
                    error_msg = str(e)
                    logger.warning(f"Error en intento {attempt + 1}: {error_msg}")
                    
                    # Si es un error de CUDA/cuDNN y tenemos más intentos
                    if attempt < max_retries - 1 and ('cudnn' in error_msg.lower() or 'cuda' in error_msg.lower()):
                        logger.info("🔄 Error relacionado con CUDA, reintentando con CPU...")
                        CONFIG['device'] = 'cpu'
                        CONFIG['compute_type'] = 'int8'
                        continue
                    else:
                        # Si no hay más intentos o no es error de CUDA, lanzar error
                        raise last_error
            
            transcription_progress[job_id].update({
                'stage': 'Procesando segmentos...',
                'progress': 30
            })
            
            # Procesar segmentos con progreso
            transcription_segments = []
            full_text = ""
            segments_list = list(segments)  # Convertir a lista para contar
            total_segments = len(segments_list)
            
            transcription_progress[job_id].update({
                'total_segments': total_segments
            })
            
            for i, segment in enumerate(segments_list):
                segment_data = {
                    'start': segment.start,
                    'end': segment.end,
                    'text': segment.text.strip(),
                    'confidence': getattr(segment, 'avg_logprob', 0.0)
                }
                transcription_segments.append(segment_data)
                full_text += segment.text.strip() + " "
                
                # Actualizar progreso (30% a 90% durante procesamiento de segmentos)
                segment_progress = 30 + (60 * (i + 1) / total_segments)
                processed_time = segment.end
                
                # Calcular tiempo estimado restante
                elapsed_time = time.time() - start_time
                if processed_time > 0:
                    estimated_total_time = elapsed_time * (audio_info['duration'] / processed_time)
                    estimated_remaining = max(0, estimated_total_time - elapsed_time)
                else:
                    estimated_remaining = None
                
                transcription_progress[job_id].update({
                    'progress': int(segment_progress),
                    'current_segment': i + 1,
                    'processed_duration': processed_time,
                    'estimated_time_remaining': estimated_remaining,
                    'stage': f'Procesando segmento {i + 1}/{total_segments} ({processed_time:.1f}s/{audio_info["duration"]:.1f}s)'
                })
                
                # Log progreso más frecuente para archivos largos
                log_interval = min(10, max(1, total_segments // 20))  # Log cada 5% aprox
                if (i + 1) % log_interval == 0 or i == total_segments - 1:
                    remaining_str = f", quedan ~{estimated_remaining/60:.1f} min" if estimated_remaining else ""
                    logger.info(f"Progreso: {i + 1}/{total_segments} segmentos ({segment_progress:.1f}%{remaining_str})")
                    
                    # Limpiar memoria cada cierto número de segmentos en GPU
                    if CONFIG['device'] == 'cuda' and (i + 1) % 50 == 0:
                        try:
                            import torch
                            torch.cuda.empty_cache()
                        except:
                            pass
            
            transcription_progress[job_id].update({
                'stage': 'Finalizando...',
                'progress': 95
            })
            
            # Limpiar archivo temporal si se creó
            if processed_path != file_path and os.path.exists(processed_path):
                os.remove(processed_path)
            
            processing_time = time.time() - start_time
            
            result = {
                'success': True,
                'job_id': job_id,
                'transcription': full_text.strip(),
                'segments': transcription_segments,
                'language': info.language,
                'language_probability': info.language_probability,
                'duration': audio_info['duration'],
                'processing_time': processing_time,
                'model_used': model_name or CONFIG['default_model'],
                'segments_count': len(transcription_segments)
            }
            
            # Generar resumen si se solicita
            if generate_summary and full_text.strip():
                result['summary'] = self.generate_summary(full_text)
            
            # Actualizar progreso final
            transcription_progress[job_id].update({
                'status': 'completado',
                'progress': 100,
                'stage': 'Transcripción completada',
                'estimated_time_remaining': 0
            })
            
            # Limpiar memoria GPU al finalizar
            if CONFIG['device'] == 'cuda':
                try:
                    import torch
                    torch.cuda.empty_cache()
                    logger.info("Memoria GPU limpiada después de transcripción")
                except:
                    pass
            
            logger.success(f"Transcripción completada en {processing_time:.1f}s")
            return result
            
        except Exception as e:
            error_msg = f"Error en transcripción: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            
            # Actualizar progreso con error
            transcription_progress[job_id].update({
                'status': 'error',
                'stage': f'Error: {error_msg}',
                'error': error_msg
            })
            
            return {
                'success': False,
                'job_id': job_id,
                'error': error_msg,
                'processing_time': time.time() - start_time
            }
    
    def generate_summary(self, text: str) -> str:
        """Generar resumen básico del texto (placeholder para LLM futuro)"""
        # Por ahora, un resumen simple basado en longitud
        sentences = text.split('. ')
        if len(sentences) <= 3:
            return text
        
        # Tomar las primeras y últimas oraciones
        summary_sentences = sentences[:2] + sentences[-1:]
        return '. '.join(summary_sentences) + '.'

# Instancia global del servicio
transcription_service = TranscriptionService()

@app.route('/health', methods=['GET'])
def health_check():
    """Verificar estado del servicio"""
    return jsonify({
        'status': 'healthy',
        'service': 'transcription-service',
        'models_loaded': list(transcription_service.models.keys()),
        'timestamp': time.time()
    })

@app.route('/transcribe', methods=['POST'])
def transcribe():
    """Endpoint principal de transcripción"""
    try:
        data = request.get_json()
        
        if not data or 'file_path' not in data:
            return jsonify({
                'success': False,
                'error': 'file_path requerido'
            }), 400
        
        file_path = data['file_path']
        model_name = data.get('model', CONFIG['default_model'])
        language = data.get('language')
        generate_summary = data.get('generate_summary', False)
        job_id = data.get('job_id')  # Permitir job_id personalizado
        
        # Transcribir
        result = transcription_service.transcribe_audio(
            file_path=file_path,
            job_id=job_id,
            model_name=model_name,
            language=language,
            generate_summary=generate_summary
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error en endpoint transcribe: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/progress/<job_id>', methods=['GET'])
def get_progress(job_id):
    """Obtener progreso de transcripción"""
    try:
        if job_id not in transcription_progress:
            return jsonify({
                'success': False,
                'error': 'Job ID no encontrado'
            }), 404
        
        progress_data = transcription_progress[job_id].copy()
        
        # Calcular tiempo transcurrido
        elapsed_time = time.time() - progress_data['start_time']
        progress_data['elapsed_time'] = elapsed_time
        
        # Remover start_time del response (info interna)
        progress_data.pop('start_time', None)
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'progress': progress_data
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo progreso: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/progress', methods=['GET'])
def list_progress():
    """Listar todos los trabajos en progreso"""
    try:
        current_time = time.time()
        progress_list = {}
        
        for job_id, data in transcription_progress.items():
            progress_data = data.copy()
            progress_data['elapsed_time'] = current_time - data['start_time']
            progress_data.pop('start_time', None)
            progress_list[job_id] = progress_data
        
        return jsonify({
            'success': True,
            'jobs': progress_list,
            'total_jobs': len(progress_list)
        })
        
    except Exception as e:
        logger.error(f"Error listando progreso: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/models', methods=['GET'])
def list_models():
    """Listar modelos disponibles"""
    available_models = ['tiny', 'base', 'small', 'medium', 'large-v1', 'large-v2', 'large-v3']
    loaded_models = list(transcription_service.models.keys())
    
    return jsonify({
        'available_models': available_models,
        'loaded_models': loaded_models,
        'default_model': CONFIG['default_model']
    })

@app.route('/cleanup', methods=['POST'])
def cleanup_jobs():
    """Limpiar trabajos completados o con error"""
    try:
        data = request.get_json() or {}
        older_than_minutes = data.get('older_than_minutes', 30)  # Por defecto, trabajos de más de 30 minutos
        
        current_time = time.time()
        cutoff_time = current_time - (older_than_minutes * 60)
        
        jobs_to_remove = []
        for job_id, job_data in transcription_progress.items():
            job_start_time = job_data['start_time']
            job_status = job_data['status']
            
            # Remover trabajos completados/error que sean más antiguos que el cutoff
            if (job_status in ['completado', 'error']) and (job_start_time < cutoff_time):
                jobs_to_remove.append(job_id)
        
        # Remover trabajos
        for job_id in jobs_to_remove:
            del transcription_progress[job_id]
        
        return jsonify({
            'success': True,
            'removed_jobs': len(jobs_to_remove),
            'removed_job_ids': jobs_to_remove,
            'remaining_jobs': len(transcription_progress)
        })
        
    except Exception as e:
        logger.error(f"Error en cleanup: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Crear instancia del servicio

if __name__ == '__main__':
    logger.info("Iniciando servicio de transcripción...")
    logger.info(f"Configuración: {CONFIG}")
    
    # Precargar modelo por defecto
    try:
        transcription_service.get_model()
        logger.success("Modelo por defecto precargado")
    except Exception as e:
        logger.warning(f"No se pudo precargar modelo: {e}")
    
    # Iniciar servidor
    port = int(os.getenv('TRANSCRIPTION_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)