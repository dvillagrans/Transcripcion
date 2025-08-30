import React, { useState } from 'react';
import { Settings, Save, RotateCcw } from 'lucide-react';
import LanguageSelector from '../components/LanguageSelector';

interface ConfigState {
  whisperModel: string;
  language: string;
  generateSummary: boolean;
  maxFileSize: number;
  autoProcess: boolean;
}

const ConfigPage: React.FC = () => {
  const [config, setConfig] = useState<ConfigState>({
    whisperModel: 'medium',
    language: 'es',
    generateSummary: true,
    maxFileSize: 100,
    autoProcess: false
  });

  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    // Save configuration to localStorage
    localStorage.setItem('audioProcessingConfig', JSON.stringify(config));
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const handleReset = () => {
    const defaultConfig: ConfigState = {
      whisperModel: 'medium',
      language: 'es',
      generateSummary: true,
      maxFileSize: 100,
      autoProcess: false
    };
    setConfig(defaultConfig);
  };

  const updateConfig = (key: keyof ConfigState, value: any) => {
    setConfig(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 p-6">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-4 animate-fade-in">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-2xl shadow-lg mb-4">
            <Settings className="h-10 w-10 text-white" />
          </div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
            Configuración
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Personaliza tu experiencia de transcripción con configuraciones avanzadas de IA
          </p>
        </div>

        {/* Configuration Form */}
        <div className="glass-effect rounded-3xl p-8 animate-slide-up">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-2">Configuración de Modelos</h2>
            <p className="text-gray-600">Optimiza el rendimiento según tus necesidades</p>
          </div>

          <div className="grid gap-8 md:gap-6">
            {/* Whisper Model Selection */}
            <div className="space-y-4">
              <div className="text-center">
                <h3 className="text-lg font-semibold text-gray-800 mb-2">🎯 Modelo de Transcripción</h3>
                <p className="text-sm text-gray-600">Elige el equilibrio perfecto entre velocidad y precisión</p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {[
                  { value: 'tiny', label: 'Tiny', desc: 'Ultra rápido', speed: '⚡⚡⚡', accuracy: '⭐⭐' },
                  { value: 'base', label: 'Base', desc: 'Equilibrado', speed: '⚡⚡', accuracy: '⭐⭐⭐' },
                  { value: 'small', label: 'Small', desc: 'Buena precisión', speed: '⚡⚡', accuracy: '⭐⭐⭐⭐' },
                  { value: 'medium', label: 'Medium', desc: 'Recomendado', speed: '⚡', accuracy: '⭐⭐⭐⭐⭐' },
                  { value: 'large-v3', label: 'Large-v3', desc: 'Máxima precisión', speed: '⚡', accuracy: '⭐⭐⭐⭐⭐' }
                ].map((model) => (
                  <div
                    key={model.value}
                    onClick={() => updateConfig('whisperModel', model.value)}
                    className={`relative p-4 rounded-2xl border-2 cursor-pointer transition-all duration-300 hover:scale-105 ${
                      config.whisperModel === model.value
                        ? 'border-primary-400 bg-gradient-to-br from-primary-50 to-secondary-50 shadow-lg'
                        : 'border-gray-200 bg-white hover:border-primary-300 hover:shadow-md'
                    }`}
                  >
                    {config.whisperModel === model.value && (
                      <div className="absolute -top-2 -right-2 w-6 h-6 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center">
                        <span className="text-white text-xs">✓</span>
                      </div>
                    )}
                    <div className="text-center space-y-2">
                      <h4 className="font-semibold text-gray-800">{model.label}</h4>
                      <p className="text-sm text-gray-600">{model.desc}</p>
                      <div className="flex justify-between text-xs">
                        <span>Velocidad: {model.speed}</span>
                        <span>Precisión: {model.accuracy}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Language Selection */}
            <div className="space-y-4">
              <div className="text-center">
                <h3 className="text-lg font-semibold text-gray-800 mb-2">🌍 Idioma de Transcripción</h3>
                <p className="text-sm text-gray-600">Selecciona el idioma principal del audio para mejorar la precisión</p>
              </div>
              
              <div className="max-w-md mx-auto">
                <LanguageSelector
                  value={config.language}
                  onChange={(language) => updateConfig('language', language)}
                />
              </div>
            </div>

            {/* Advanced Settings */}
            <div className="grid md:grid-cols-2 gap-6">
              {/* Generate Summary Toggle */}
              <div className="p-6 bg-gradient-to-br from-accent-50 to-primary-50 rounded-2xl border border-accent-200">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h4 className="font-semibold text-gray-800 flex items-center">
                      🤖 Resumen Automático
                    </h4>
                    <p className="text-sm text-gray-600 mt-1">
                      IA genera resúmenes inteligentes
                    </p>
                  </div>
                  <button
                    onClick={() => updateConfig('generateSummary', !config.generateSummary)}
                    className={`relative inline-flex h-8 w-14 items-center rounded-full transition-colors duration-300 ${
                      config.generateSummary ? 'bg-gradient-to-r from-primary-500 to-secondary-500' : 'bg-gray-300'
                    }`}
                  >
                    <span
                      className={`inline-block h-6 w-6 transform rounded-full bg-white shadow-lg transition-transform duration-300 ${
                        config.generateSummary ? 'translate-x-7' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>
              </div>

              {/* Auto Process Toggle */}
              <div className="p-6 bg-gradient-to-br from-secondary-50 to-accent-50 rounded-2xl border border-secondary-200">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h4 className="font-semibold text-gray-800 flex items-center">
                      ⚡ Procesamiento Automático
                    </h4>
                    <p className="text-sm text-gray-600 mt-1">
                      Inicia al subir archivos
                    </p>
                  </div>
                  <button
                    onClick={() => updateConfig('autoProcess', !config.autoProcess)}
                    className={`relative inline-flex h-8 w-14 items-center rounded-full transition-colors duration-300 ${
                      config.autoProcess ? 'bg-gradient-to-r from-secondary-500 to-accent-500' : 'bg-gray-300'
                    }`}
                  >
                    <span
                      className={`inline-block h-6 w-6 transform rounded-full bg-white shadow-lg transition-transform duration-300 ${
                        config.autoProcess ? 'translate-x-7' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>
              </div>
            </div>

            {/* Max File Size */}
            <div className="space-y-4">
              <div className="text-center">
                <h3 className="text-lg font-semibold text-gray-800 mb-2">📁 Límite de Archivo</h3>
                <p className="text-sm text-gray-600">Configura el tamaño máximo permitido</p>
              </div>
              
              <div className="bg-gradient-to-r from-warning-50 to-primary-50 rounded-2xl p-6 border border-warning-200">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-lg font-semibold text-gray-800">{config.maxFileSize} MB</span>
                  <div className="flex space-x-2">
                    {[50, 100, 200, 500].map((size) => (
                      <button
                        key={size}
                        onClick={() => updateConfig('maxFileSize', size)}
                        className={`px-3 py-1 rounded-full text-sm font-medium transition-all duration-200 ${
                          config.maxFileSize === size
                            ? 'bg-gradient-to-r from-primary-500 to-secondary-500 text-white shadow-lg'
                            : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
                        }`}
                      >
                        {size}MB
                      </button>
                    ))}
                  </div>
                </div>
                
                <div className="relative">
                  <input
                    type="range"
                    min="1"
                    max="500"
                    value={config.maxFileSize}
                    onChange={(e) => updateConfig('maxFileSize', parseInt(e.target.value))}
                    className="w-full h-3 bg-gray-200 rounded-full appearance-none cursor-pointer slider"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-2">
                    <span>1MB</span>
                    <span>125MB</span>
                    <span>250MB</span>
                    <span>375MB</span>
                    <span>500MB</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Performance Info */}
        <div className="glass-effect rounded-3xl p-8 animate-slide-up">
          <div className="text-center mb-6">
            <h3 className="text-2xl font-bold text-gray-800 mb-2">💡 Guía de Rendimiento</h3>
            <p className="text-gray-600">Elige el modelo perfecto para tu caso de uso</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-6">
            <div className="p-6 bg-gradient-to-br from-success-50 to-primary-50 rounded-2xl border border-success-200">
              <div className="text-center space-y-3">
                <div className="w-12 h-12 bg-gradient-to-br from-success-500 to-primary-500 rounded-xl flex items-center justify-center mx-auto">
                  <span className="text-white text-xl">⚡</span>
                </div>
                <h4 className="font-semibold text-gray-800">Velocidad</h4>
                <p className="text-sm text-gray-600">Tiny/Base: Ideal para pruebas rápidas y transcripciones en tiempo real</p>
              </div>
            </div>
            
            <div className="p-6 bg-gradient-to-br from-warning-50 to-secondary-50 rounded-2xl border border-warning-200">
              <div className="text-center space-y-3">
                <div className="w-12 h-12 bg-gradient-to-br from-warning-500 to-secondary-500 rounded-xl flex items-center justify-center mx-auto">
                  <span className="text-white text-xl">⚖️</span>
                </div>
                <h4 className="font-semibold text-gray-800">Equilibrio</h4>
                <p className="text-sm text-gray-600">Small/Medium: Perfecto balance entre velocidad y calidad</p>
              </div>
            </div>
            
            <div className="p-6 bg-gradient-to-br from-accent-50 to-primary-50 rounded-2xl border border-accent-200">
              <div className="text-center space-y-3">
                <div className="w-12 h-12 bg-gradient-to-br from-accent-500 to-primary-500 rounded-xl flex items-center justify-center mx-auto">
                  <span className="text-white text-xl">🎯</span>
                </div>
                <h4 className="font-semibold text-gray-800">Precisión</h4>
                <p className="text-sm text-gray-600">Large-v3: Máxima calidad para contenido profesional</p>
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <button
            onClick={handleReset}
            className="group relative px-6 py-3 bg-gradient-to-r from-gray-500 to-gray-600 text-white rounded-2xl font-semibold shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 overflow-hidden"
          >
            {/* Animated background */}
            <div className="absolute inset-0 bg-gradient-to-r from-gray-600 to-gray-700 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            
            {/* Button content */}
            <div className="relative flex items-center space-x-3">
              <RotateCcw className="h-5 w-5 group-hover:rotate-180 transition-transform duration-300" />
              <span>Restablecer</span>
            </div>
            
            {/* Shine effect */}
            <div className="absolute inset-0 -skew-x-12 bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-0 group-hover:opacity-100 group-hover:animate-shine"></div>
          </button>

          <button
            onClick={handleSave}
            className={`group relative px-8 py-3 rounded-2xl font-semibold shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 overflow-hidden ${
              saved
                ? 'bg-gradient-to-r from-success-500 to-primary-500 text-white'
                : 'bg-gradient-to-r from-primary-500 to-secondary-500 text-white'
            }`}
          >
            {/* Animated background */}
            <div className={`absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 ${
              saved
                ? 'bg-gradient-to-r from-success-600 to-primary-600'
                : 'bg-gradient-to-r from-primary-600 to-secondary-600'
            }`}></div>
            
            {/* Button content */}
            <div className="relative flex items-center space-x-3">
              <Save className={`h-5 w-5 transition-transform duration-300 ${
                saved ? 'scale-110' : 'group-hover:scale-110'
              }`} />
              <span>{saved ? '¡Configuración Guardada!' : 'Guardar Configuración'}</span>
              {saved && <span className="animate-bounce">✨</span>}
            </div>
            
            {/* Shine effect */}
            <div className="absolute inset-0 -skew-x-12 bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-0 group-hover:opacity-100 group-hover:animate-shine"></div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfigPage;