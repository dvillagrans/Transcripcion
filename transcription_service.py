#!/usr/bin/env python3
"""
Servicio de Transcripción con Faster-Whisper
Procesa archivos de audio y genera transcripciones usando modelos Whisper optimizados.
"""

import os
import sys
import json
import time
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
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuración
CONFIG = {
    'models_dir': './models',
    'uploads_dir': './uploads',
    'supported_formats': ['.mp3', '.wav', '.flac', '.m4a', '.ogg'],
    'max_file_size': 500 * 1024 * 1024,  # 500MB
    'default_model': 'medium',
    'device': 'cuda',  # Usar GPU exclusivamente
    'compute_type': 'float16'  # Usar float16 para mejor rendimiento en GPU
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
            logger.info(f"Cargando modelo Whisper: {model_name}")
            try:
                self.models[model_name] = WhisperModel(
                    model_name,
                    device=CONFIG['device'],
                    compute_type=CONFIG['compute_type'],
                    download_root=CONFIG['models_dir']
                )
                logger.success(f"Modelo {model_name} cargado exitosamente")
            except Exception as e:
                logger.error(f"Error cargando modelo {model_name}: {e}")
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
    
    def transcribe_audio(self, file_path: str, model_name: str = None, 
                        language: str = None, generate_summary: bool = False) -> Dict[str, Any]:
        """Transcribir archivo de audio"""
        start_time = time.time()
        
        try:
            # Validar archivo
            audio_info = self.validate_audio_file(file_path)
            logger.info(f"Transcribiendo: {audio_info['file_path']} ({audio_info['duration']:.1f}s)")
            
            # Preprocesar audio
            processed_path = self.preprocess_audio(file_path)
            
            # Obtener modelo
            model = self.get_model(model_name)
            
            # Transcribir
            segments, info = model.transcribe(
                processed_path,
                language=language,
                beam_size=5,
                best_of=5,
                temperature=0.0,
                condition_on_previous_text=False,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            
            # Procesar segmentos
            transcription_segments = []
            full_text = ""
            
            for segment in segments:
                segment_data = {
                    'start': segment.start,
                    'end': segment.end,
                    'text': segment.text.strip(),
                    'confidence': getattr(segment, 'avg_logprob', 0.0)
                }
                transcription_segments.append(segment_data)
                full_text += segment.text.strip() + " "
            
            # Limpiar archivo temporal si se creó
            if processed_path != file_path and os.path.exists(processed_path):
                os.remove(processed_path)
            
            processing_time = time.time() - start_time
            
            result = {
                'success': True,
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
            
            logger.success(f"Transcripción completada en {processing_time:.1f}s")
            return result
            
        except Exception as e:
            error_msg = f"Error en transcripción: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            
            return {
                'success': False,
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
        
        # Transcribir
        result = transcription_service.transcribe_audio(
            file_path=file_path,
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