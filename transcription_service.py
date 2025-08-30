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
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import multiprocessing as mp

from flask import Flask, request, jsonify
from flask_cors import CORS
from faster_whisper import WhisperModel
from loguru import logger
import filetype
import librosa
import soundfile as sf
import torch
import numpy as np
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
        
        # ROBUST_MODE ya no fuerza CPU - permite GPU con configuración estable
        robust_mode = os.getenv('ROBUST_MODE', 'false').lower() == 'true'
        if robust_mode:
            logger.info("🛡️ ROBUST_MODE activado: usando configuración estable")
        
        # Probar GPU - aún en modo robusto podemos usar GPU
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

# Modelo por defecto - puede ser configurado por variable de entorno
DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'large-v3')
DEV_MODE = os.getenv('DEV_MODE', 'false').lower() in ['true', '1', 'yes']

# Si está en modo desarrollo, usar modelo más rápido
if DEV_MODE:
    DEFAULT_MODEL = 'medium'
    logger.info("🚧 Modo desarrollo: usando modelo 'medium' para carga rápida")

CONFIG = {
    'models_dir': './models',
    'uploads_dir': './uploads',
    'supported_formats': ['.mp3', '.wav', '.flac', '.m4a', '.ogg'],
    'max_file_size': 500 * 1024 * 1024,  # 500MB para archivos largos
    'default_model': DEFAULT_MODEL,
    'default_language': 'es',  # Español por defecto
    'device': device,
    'compute_type': compute_type,
    'robust_mode': ROBUST_MODE,
    # Optimizaciones para 32GB RAM
    'high_memory_mode': True,
    'segment_length': 600,  # 10 minutos por segmento (era 300)
    'parallel_workers': 3,  # Procesar 3 segmentos simultáneamente
    'preload_model': True,  # Mantener modelo en memoria
}

# Logger configuration
logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
logger.add("transcription.log", rotation="10 MB", level="DEBUG")

class TranscriptionService:
    """Servicio de transcripción optimizado para 32GB RAM con Faster-Whisper"""
    
    def __init__(self):
        self.models = {}
        self.preloaded_model = None
        self.model_lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=CONFIG['parallel_workers'])
        self.ensure_directories()
        
        # Preload del modelo por defecto si está habilitado
        if CONFIG.get('preload_model', False):
            self.preload_default_model()
        
    def ensure_directories(self):
        """Crear directorios necesarios"""
        Path(CONFIG['models_dir']).mkdir(exist_ok=True)
        Path(CONFIG['uploads_dir']).mkdir(exist_ok=True)
        Path('./segments').mkdir(exist_ok=True)
        
    def preload_default_model(self):
        """Precargar modelo por defecto en memoria"""
        try:
            default_model = CONFIG['default_model']
            logger.info(f"🚀 Precargando modelo {default_model} en memoria...")
            
            # Mostrar información sobre el modelo
            model_sizes = {
                'tiny': '39MB',
                'base': '74MB', 
                'small': '244MB',
                'medium': '769MB',
                'large-v3': '1550MB'
            }
            
            model_size = model_sizes.get(default_model, 'Desconocido')
            logger.info(f"📦 Modelo {default_model}: ~{model_size}")
            
            if default_model == 'large-v3':
                logger.info("⏳ Este es un modelo grande, puede tomar 1-3 minutos la primera vez...")
            
            model = WhisperModel(
                default_model,
                device=CONFIG['device'],
                compute_type=CONFIG['compute_type'],
                download_root=CONFIG['models_dir']
            )
            
            with self.model_lock:
                self.preloaded_model = model
                self.models[default_model] = model
                
            logger.success(f"✅ Modelo {default_model} precargado exitosamente")
        except Exception as e:
            logger.error(f"❌ Error precargando modelo: {e}")
            self.preloaded_model = None
        
    def get_model(self, model_name: str = None) -> WhisperModel:
        """Obtener o cargar modelo Whisper optimizado"""
        if model_name is None:
            model_name = CONFIG['default_model']
            
        # Si es el modelo por defecto y está precargado, usarlo
        if (model_name == CONFIG['default_model'] and 
            self.preloaded_model is not None):
            return self.preloaded_model
            
        # Thread-safe model loading
        with self.model_lock:
            if model_name not in self.models:
                logger.info(f"🔄 Cargando modelo Whisper: {model_name} en {CONFIG['device']}")
                try:
                    self.models[model_name] = WhisperModel(
                        model_name,
                        device=CONFIG['device'],
                        compute_type=CONFIG['compute_type'],
                        download_root=CONFIG['models_dir']
                    )
                    logger.success(f"✅ Modelo {model_name} cargado exitosamente en {CONFIG['device']}")
                except Exception as e:
                    logger.error(f"❌ Error cargando modelo {model_name}: {e}")
                    # Intentar fallback a CPU si falla GPU
                    if CONFIG['device'] == 'cuda':
                        logger.info("🔄 Intentando fallback a CPU...")
                        try:
                            self.models[model_name] = WhisperModel(
                                model_name,
                                device='cpu',
                                compute_type='int8',
                                download_root=CONFIG['models_dir']
                            )
                            logger.success(f"✅ Modelo {model_name} cargado en CPU como fallback")
                            # Actualizar configuración global para futuros modelos
                            CONFIG['device'] = 'cpu'
                            CONFIG['compute_type'] = 'int8'
                        except Exception as cpu_error:
                            logger.error(f"❌ Error también en CPU: {cpu_error}")
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
    
    def segment_audio(self, file_path: str, segment_duration: int = None) -> list:
        """Dividir audio en segmentos optimizados para 32GB RAM (defecto: 10 minutos)"""
        if segment_duration is None:
            segment_duration = CONFIG.get('segment_length', 600)  # 10 minutos por defecto
            
        try:
            # Cargar audio para obtener información
            audio, sr = librosa.load(file_path, sr=None)
            total_duration = len(audio) / sr
            
            logger.info(f"🎵 Audio cargado: {total_duration:.1f}s, segmentos de {segment_duration}s")
            
            # Calcular número de segmentos
            num_segments = int(np.ceil(total_duration / segment_duration))
            segment_paths = []
            
            logger.info(f"🧩 Dividiendo audio de {total_duration:.1f}s en {num_segments} segmentos de {segment_duration}s")
            
            segments_dir = os.path.join(os.path.dirname(file_path), '..', 'segments')
            os.makedirs(segments_dir, exist_ok=True)
            
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            
            for i in range(num_segments):
                start_time = i * segment_duration
                end_time = min((i + 1) * segment_duration, total_duration)
                
                # Calcular índices de muestras
                start_sample = int(start_time * sr)
                end_sample = int(end_time * sr)
                
                # Extraer segmento
                segment_audio = audio[start_sample:end_sample]
                
                # Guardar segmento
                segment_filename = f"{base_name}_segment_{i+1:03d}.wav"
                segment_path = os.path.join(segments_dir, segment_filename)
                
                sf.write(segment_path, segment_audio, sr)
                segment_paths.append(segment_path)
                
                logger.info(f"Segmento {i+1}/{num_segments} guardado: {segment_filename} ({end_time-start_time:.1f}s)")
            
            return segment_paths
            
        except Exception as e:
            logger.error(f"Error segmentando audio: {e}")
            return [file_path]  # Retornar archivo original si falla
    
    def transcribe_segments_parallel(self, segment_paths: list, job_id: str, model, language: str = None) -> list:
        """Transcribir segmentos en paralelo - Optimizado para 32GB RAM"""
        # Usar idioma por defecto si no se especifica
        if language is None:
            language = CONFIG['default_language']
            
        transcriptions = []
        total_segments = len(segment_paths)
        completed_segments = 0
        
        logger.info(f"🚀 Iniciando transcripción paralela de {total_segments} segmentos con {CONFIG['parallel_workers']} workers")
        
        def transcribe_single_segment(segment_info):
            segment_path, segment_index = segment_info
            segment_num = segment_index + 1
            
            try:
                logger.info(f"🎯 Worker iniciando segmento {segment_num}/{total_segments}: {os.path.basename(segment_path)}")
                
                # Actualizar progreso
                progress_percent = int((completed_segments / total_segments) * 70) + 20
                transcription_progress[job_id]['progress'] = progress_percent
                transcription_progress[job_id]['current_stage'] = f"Transcribiendo segmento {segment_num}/{total_segments} (paralelo)"
                transcription_progress[job_id]['segments_completed'] = completed_segments
                transcription_progress[job_id]['segments_total'] = total_segments
                
                # Transcribir segmento
                segments, info = model.transcribe(
                    segment_path,
                    language=language,
                    vad_filter=True,
                    vad_parameters=dict(min_silence_duration_ms=500),
                    beam_size=5,
                    best_of=5,
                    temperature=0.0,
                    compression_ratio_threshold=2.4,
                    log_prob_threshold=-1.0,
                    no_speech_threshold=0.6,
                    condition_on_previous_text=False,
                    initial_prompt=None
                )
                
                # Procesar transcripción
                segment_transcription = ""
                for segment in segments:
                    segment_transcription += segment.text
                    
                # Guardar transcripción temporal del segmento
                transcription_filename = f"transcription_{os.path.basename(segment_path).replace('.wav', '.txt')}"
                transcription_path = os.path.join('segments', transcription_filename)
                
                with open(transcription_path, 'w', encoding='utf-8') as f:
                    f.write(segment_transcription)
                
                logger.success(f"✅ Segmento {segment_num}/{total_segments} completado por worker")
                
                return {
                    'index': segment_index,
                    'transcription': segment_transcription,
                    'transcription_file': transcription_path,
                    'duration': info.duration,
                    'language': info.language,
                    'language_probability': info.language_probability
                }
                
            except Exception as e:
                logger.error(f"❌ Error en segmento {segment_num}: {e}")
                return {
                    'index': segment_index,
                    'transcription': f"[Error en segmento {segment_num}]",
                    'transcription_file': None,
                    'error': str(e)
                }
        
        # Crear lista de trabajo para ThreadPoolExecutor
        segment_work = [(path, idx) for idx, path in enumerate(segment_paths)]
        
        # Procesar segmentos en paralelo
        with ThreadPoolExecutor(max_workers=CONFIG['parallel_workers']) as executor:
            future_to_segment = {
                executor.submit(transcribe_single_segment, work): work 
                for work in segment_work
            }
            
            # Recopilar resultados
            results = [None] * total_segments  # Preservar orden
            
            for future in as_completed(future_to_segment):
                try:
                    result = future.result()
                    results[result['index']] = result
                    completed_segments += 1
                    
                    # Actualizar progreso global
                    progress_percent = int((completed_segments / total_segments) * 70) + 20
                    transcription_progress[job_id]['progress'] = progress_percent
                    transcription_progress[job_id]['segments_completed'] = completed_segments
                    
                    logger.info(f"📊 Progreso paralelo: {completed_segments}/{total_segments} segmentos completados")
                    
                except Exception as e:
                    logger.error(f"❌ Error procesando resultado: {e}")
        
        # Combinar resultados en orden
        transcriptions_data = []
        for i, result in enumerate(results):
            if result:
                transcriptions_data.append({
                    'segment_number': i + 1,
                    'text': result['transcription'],
                    'language': result.get('language', 'unknown'),
                    'duration': result.get('duration', 0),
                    'transcription_file': result.get('transcription_file')
                })
        
        logger.success(f"🎯 Transcripción paralela completada: {total_segments} segmentos procesados")
        return transcriptions_data

    def transcribe_segments(self, segment_paths: list, job_id: str, model, language: str = None) -> list:
        """Transcribir cada segmento - modo secuencial (fallback)"""
        # Usar idioma por defecto si no se especifica
        if language is None:
            language = CONFIG['default_language']
            
        # Si hay múltiples segmentos y modo de alta memoria está habilitado, usar procesamiento paralelo
        if len(segment_paths) > 1 and CONFIG.get('high_memory_mode', False):
            return self.transcribe_segments_parallel(segment_paths, job_id, model, language)
            
        transcriptions = []
        total_segments = len(segment_paths)
        
        for i, segment_path in enumerate(segment_paths):
            try:
                segment_num = i + 1
                logger.info(f"Transcribiendo segmento {segment_num}/{total_segments}: {os.path.basename(segment_path)}")
                
                # Actualizar progreso
                progress = 25 + int((i / total_segments) * 65)  # 25% a 90%
                transcription_progress[job_id].update({
                    'stage': f'Transcribiendo segmento {segment_num}/{total_segments}...',
                    'progress': progress,
                    'current_segment': segment_num,
                    'total_segments': total_segments
                })
                
                # Transcribir segmento
                segments, info = model.transcribe(
                    segment_path,
                    language=language,
                    beam_size=1 if CONFIG['robust_mode'] else 5,
                    patience=1.0,
                    word_timestamps=True,
                    initial_prompt=None
                )
                
                # Recopilar texto del segmento
                segment_text = ""
                for segment in segments:
                    segment_text += segment.text + " "
                
                segment_text = segment_text.strip()
                transcriptions.append({
                    'segment_number': segment_num,
                    'text': segment_text,
                    'file_path': segment_path,
                    'language': info.language,
                    'duration': info.duration
                })
                
                # Guardar transcripción del segmento
                segments_dir = os.path.dirname(segment_path)
                base_name = os.path.splitext(os.path.basename(segment_path))[0]
                transcription_file = os.path.join(segments_dir, f"transcription_{base_name}.txt")
                
                with open(transcription_file, 'w', encoding='utf-8') as f:
                    f.write(f"# Segmento {segment_num}/{total_segments}\n")
                    f.write(f"# Archivo: {os.path.basename(segment_path)}\n")
                    f.write(f"# Idioma: {info.language}\n")
                    f.write(f"# Duración: {info.duration:.1f}s\n\n")
                    f.write(segment_text)
                
                logger.info(f"✅ Segmento {segment_num} completado: {len(segment_text)} caracteres")
                
            except Exception as e:
                logger.error(f"❌ Error transcribiendo segmento {segment_num}: {e}")
                # Continuar con el siguiente segmento
                transcriptions.append({
                    'segment_number': segment_num,
                    'text': f"[ERROR: No se pudo transcribir el segmento {segment_num}]",
                    'file_path': segment_path,
                    'error': str(e)
                })
        
        return transcriptions
    
    def cleanup_segments(self, segment_paths: list):
        """Limpiar archivos de segmentos temporales"""
        try:
            segments_dir = os.path.dirname(segment_paths[0]) if segment_paths else None
            if not segments_dir:
                return
            
            # Eliminar archivos de segmentos
            for segment_path in segment_paths:
                try:
                    if os.path.exists(segment_path):
                        os.remove(segment_path)
                        logger.info(f"🗑️ Eliminado segmento: {os.path.basename(segment_path)}")
                except Exception as e:
                    logger.warning(f"No se pudo eliminar {segment_path}: {e}")
            
            # Eliminar archivos de transcripción de segmentos (mantener solo la final)
            for segment_path in segment_paths:
                base_name = os.path.splitext(os.path.basename(segment_path))[0]
                transcription_file = os.path.join(segments_dir, f"transcription_{base_name}.txt")
                try:
                    if os.path.exists(transcription_file):
                        os.remove(transcription_file)
                        logger.info(f"🗑️ Eliminada transcripción temporal: transcription_{base_name}.txt")
                except Exception as e:
                    logger.warning(f"No se pudo eliminar {transcription_file}: {e}")
            
            logger.info("🧹 Limpieza de segmentos completada")
            
        except Exception as e:
            logger.error(f"Error limpiando segmentos: {e}")
    
    def transcribe_audio(self, file_path: str, job_id: str = None, model_name: str = None, 
                        language: str = None, generate_summary: bool = False) -> Dict[str, Any]:
        """Transcribir archivo de audio con seguimiento de progreso"""
        start_time = time.time()
        
        # Usar idioma por defecto si no se especifica
        if language is None:
            language = CONFIG['default_language']
        
        # Generar ID único si no se proporciona
        if not job_id:
            job_id = f"job_{int(time.time() * 1000)}_{os.path.basename(file_path)}"
        
        # Inicializar progreso con información de modo optimizado
        transcription_progress[job_id] = {
            'status': 'iniciando',
            'progress': 0,
            'stage': 'Validando archivo...',
            'start_time': start_time,
            'estimated_time_remaining': None,
            'current_segment': 0,
            'total_segments': 0,
            'processed_duration': 0,
            'total_duration': 0,
            'optimization_mode': 'high_memory' if CONFIG.get('high_memory_mode', False) else 'standard',
            'parallel_workers': CONFIG.get('parallel_workers', 1),
            'model_preloaded': self.preloaded_model is not None,
            'segment_duration': CONFIG.get('segment_length', 600) // 60  # en minutos
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
            
            # Decidir si usar segmentación basado en duración - Optimizado para 32GB RAM
            segment_threshold = 600 if CONFIG.get('high_memory_mode', False) else 300  # 10 min vs 5 min
            use_segmentation = audio_info['duration'] > segment_threshold
            segment_paths = []
            
            if use_segmentation:
                segment_duration = CONFIG.get('segment_length', 600)  # 10 minutos por defecto
                logger.info(f"🚀 Audio largo detectado ({audio_info['duration']:.1f}s), usando segmentación optimizada de {segment_duration//60} minutos")
                transcription_progress[job_id].update({
                    'stage': f'Segmentando audio en bloques de {segment_duration//60} minutos...',
                    'progress': 22
                })
                
                # Segmentar audio con duración optimizada
                segment_paths = self.segment_audio(processed_path, segment_duration=segment_duration)
                
                expected_time = len(segment_paths) * (segment_duration // 60) * 0.4  # Estimación optimista
                transcription_progress[job_id].update({
                    'total_segments': len(segment_paths),
                    'stage': f'Audio segmentado en {len(segment_paths)} bloques (procesamiento paralelo)',
                    'progress': 25,
                    'status': 'transcribiendo',
                    'estimated_time_remaining': f"{expected_time:.1f} minutos"
                })
                
                # Transcribir segmentos con procesamiento paralelo
                transcriptions_data = self.transcribe_segments(segment_paths, job_id, model, language)
                
                # Combinar transcripciones
                transcription_progress[job_id].update({
                    'stage': 'Combinando transcripciones...',
                    'progress': 90
                })
                
                full_text = ""
                segments_info = []
                total_duration = 0
                
                for trans_data in transcriptions_data:
                    if 'error' not in trans_data:
                        full_text += trans_data['text'] + "\n\n"
                        segments_info.append({
                            'segment': trans_data['segment_number'],
                            'text': trans_data['text'],
                            'language': trans_data.get('language', 'unknown'),
                            'duration': trans_data.get('duration', 0)
                        })
                        total_duration += trans_data.get('duration', 0)
                    else:
                        full_text += trans_data['text'] + "\n\n"
                
                # Generar resumen si está solicitado y hay texto
                summary = None
                if generate_summary and full_text.strip():
                    logger.info("📝 Generando resumen automático...")
                    transcription_progress[job_id].update({
                        'stage': 'Generando resumen automático...',
                        'progress': 92
                    })
                    try:
                        summary = self.generate_summary(full_text)
                        logger.success("✅ Resumen generado exitosamente")
                    except Exception as e:
                        logger.error(f"❌ Error generando resumen: {e}")
                        summary = "Error al generar resumen automático."
                
                # Limpiar archivos temporales
                transcription_progress[job_id].update({
                    'stage': 'Limpiando archivos temporales...',
                    'progress': 95
                })
                self.cleanup_segments(segment_paths)
                
                # Crear resultado final
                info = type('obj', (object,), {
                    'language': segments_info[0]['language'] if segments_info else 'unknown',
                    'language_probability': 0.9,
                    'duration': total_duration,
                    'segments_count': len(segments_info)
                })()
                
                full_text = full_text.strip()
                
                # Crear transcription_segments para compatibilidad
                transcription_segments = []
                for i, trans_data in enumerate(transcriptions_data):
                    if 'error' not in trans_data:
                        transcription_segments.append({
                            'start': i * 300,  # 5 minutos por segmento
                            'end': min((i + 1) * 300, audio_info['duration']),
                            'text': trans_data['text'],
                            'confidence': 0.0
                        })
                
            else:
                # Transcripción normal para audios cortos
                logger.info(f"📝 Audio corto ({audio_info['duration']:.1f}s), transcripción directa")
                
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
                            continue
                        
                        # Si es el último intento, lanzar excepción
                        if attempt == max_retries - 1:
                            raise last_error
                
                # Procesar segmentos y ensamblar texto para transcripción normal
                transcription_progress[job_id].update({
                    'stage': 'Procesando segmentos...',
                    'progress': 50,
                    'status': 'transcribiendo'
                })
                
                full_text = ""
                transcription_segments = []
                segment_count = 0
                processed_duration = 0
                
                for i, segment in enumerate(segments):
                    segment_count += 1
                    processed_duration += segment.end - segment.start
                    full_text += segment.text
                    
                    # Crear datos del segmento
                    transcription_segments.append({
                        'start': segment.start,
                        'end': segment.end,
                        'text': segment.text.strip(),
                        'confidence': getattr(segment, 'avg_logprob', 0.0)
                    })
                    
                    # Actualizar progreso periódicamente
                    if i % 10 == 0:  # Cada 10 segmentos
                        progress = 50 + int((processed_duration / audio_info['duration']) * 40)
                        remaining_time = None
                        if processed_duration > 0:
                            elapsed = time.time() - start_time
                            rate = processed_duration / elapsed
                            remaining_duration = audio_info['duration'] - processed_duration
                            remaining_time = remaining_duration / rate / 60  # en minutos
                        
                        transcription_progress[job_id].update({
                            'progress': min(progress, 90),
                            'current_segment': segment_count,
                            'processed_duration': processed_duration,
                            'estimated_time_remaining': remaining_time
                        })
                
                logger.info(f"Progreso: {segment_count}/{segment_count} segmentos (90.0%, quedan ~0.0 min)")
                full_text = full_text.strip()
            
            # Código común para finalización
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
            
            # Incluir resumen si ya fue generado (para segmentos) o generarlo ahora (para audios cortos)
            if generate_summary and full_text.strip():
                if 'summary' in locals() and summary is not None:
                    # Resumen ya fue generado durante procesamiento de segmentos
                    result['summary'] = summary
                    logger.info("📝 Resumen incluido en resultado final")
                else:
                    # Generar resumen para audios cortos
                    logger.info("📝 Generando resumen para audio corto...")
                    transcription_progress[job_id].update({
                        'stage': 'Generando resumen...',
                        'progress': 97
                    })
                    try:
                        result['summary'] = self.generate_summary(full_text)
                        logger.success("✅ Resumen generado exitosamente")
                    except Exception as e:
                        logger.error(f"❌ Error generando resumen: {e}")
                        result['summary'] = "Error al generar resumen automático."
            
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
        """Generar resumen inteligente del texto transcrito"""
        if not text or not text.strip():
            return "No hay contenido para resumir."
            
        text = text.strip()
        
        # Dividir en oraciones
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        total_sentences = len(sentences)
        
        # Si es muy corto, devolver el texto original
        if total_sentences <= 3:
            return text
        
        # Calcular cuántas oraciones incluir en el resumen (25-30% del total)
        summary_length = max(3, min(total_sentences // 3, 10))
        
        # Estrategia de resumen:
        # 1. Primeras 2 oraciones (introducción)
        # 2. Algunas oraciones del medio (contenido principal)
        # 3. Última oración (conclusión)
        
        summary_sentences = []
        
        # Primeras oraciones
        summary_sentences.extend(sentences[:2])
        
        # Oraciones del medio (distribución uniforme)
        if total_sentences > 5:
            middle_start = 2
            middle_end = total_sentences - 1
            middle_count = summary_length - 3  # Reservar espacio para inicio y final
            
            if middle_count > 0:
                step = max(1, (middle_end - middle_start) // middle_count)
                for i in range(middle_start, middle_end, step):
                    if len(summary_sentences) < summary_length - 1:
                        summary_sentences.append(sentences[i])
        
        # Última oración
        if total_sentences > 1:
            summary_sentences.append(sentences[-1])
        
        # Eliminar duplicados manteniendo orden
        seen = set()
        unique_sentences = []
        for sentence in summary_sentences:
            if sentence not in seen:
                seen.add(sentence)
                unique_sentences.append(sentence)
        
        summary = '. '.join(unique_sentences) + '.'
        
        # Agregar estadísticas al final
        word_count = len(text.split())
        summary += f"\n\n📊 Estadísticas: {total_sentences} oraciones, ~{word_count} palabras en la transcripción original."
        
        return summary

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
    logger.info("🚀 Iniciando servicio de transcripción optimizado para 32GB RAM...")
    logger.info(f"📊 Configuración optimizada:")
    logger.info(f"   • Modelo por defecto: {CONFIG['default_model']}")
    logger.info(f"   • Modo alta memoria: {CONFIG.get('high_memory_mode', False)}")
    logger.info(f"   • Workers paralelos: {CONFIG.get('parallel_workers', 1)}")
    logger.info(f"   • Segmentos de: {CONFIG.get('segment_length', 600)//60} minutos")
    logger.info(f"   • Preload modelo: {CONFIG.get('preload_model', False)}")
    logger.info(f"   • Dispositivo: {CONFIG['device']} ({CONFIG['compute_type']})")
    
    # Precargar modelo por defecto
    try:
        if not transcription_service.preloaded_model:
            transcription_service.get_model()
        logger.success("✅ Modelo por defecto listo para transcripción")
    except Exception as e:
        logger.warning(f"⚠️ No se pudo precargar modelo: {e}")
    
    # Mostrar información de rendimiento esperado
    logger.info("📈 Rendimiento esperado con optimizaciones:")
    logger.info("   • Audio 30 min → ~8-10 minutos")
    logger.info("   • Audio 1 hora → ~12-15 minutos") 
    logger.info("   • Audio 1:30h → ~15-20 minutos")
    
    # Iniciar servidor
    port = int(os.getenv('TRANSCRIPTION_PORT', 5000))
    logger.success(f"🌐 Servidor iniciado en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=False)