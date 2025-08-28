import React from 'react';
import { Link } from 'react-router-dom';
import { AudioWaveform, Settings, ArrowRight, Sparkles, Zap, Brain, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

const HomePage: React.FC = () => {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        {/* Background with gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary-50 via-white to-secondary-50"></div>
        
        {/* Floating elements */}
        <div className="absolute top-20 left-10 w-20 h-20 bg-primary-200/30 rounded-full blur-xl animate-float"></div>
        <div className="absolute top-40 right-20 w-32 h-32 bg-secondary-200/30 rounded-full blur-xl animate-float" style={{animationDelay: '1s'}}></div>
        <div className="absolute bottom-20 left-1/4 w-16 h-16 bg-accent-200/30 rounded-full blur-xl animate-float" style={{animationDelay: '2s'}}></div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-32">
          <div className="text-center animate-fade-in">
            {/* Badge */}
            <Badge className="inline-flex items-center px-4 py-2 rounded-full bg-gradient-primary text-white text-sm font-medium mb-8 shadow-glow animate-scale-in border-0">
              <Sparkles className="w-4 h-4 mr-2" />
              Powered by AI • Faster-Whisper • Llama 3.1
            </Badge>
            
            {/* Main heading */}
            <h1 className="text-5xl md:text-7xl font-bold mb-8 animate-slide-up">
              <span className="text-gradient">Pipeline de</span>
              <br />
              <span className="text-dark-800">Procesamiento</span>
              <br />
              <span className="text-gradient">de Audio</span>
            </h1>
            
            {/* Subtitle */}
            <p className="text-xl md:text-2xl text-dark-600 max-w-4xl mx-auto mb-12 leading-relaxed animate-slide-up" style={{animationDelay: '0.2s'}}>
              Transcribe, analiza y resume archivos de audio de manera automática usando 
              <span className="text-gradient font-semibold"> tecnologías de IA avanzadas</span>. 
              Convierte horas de audio en insights valiosos en minutos.
            </p>
            
            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16 animate-slide-up" style={{animationDelay: '0.4s'}}>
              <Button asChild size="lg" className="bg-gradient-primary text-white font-semibold text-lg px-8 py-4 shadow-lg hover:shadow-glow transition-all duration-300 transform hover:scale-105 active:scale-95 group">
                <Link to="/process">
                  <AudioWaveform className="mr-3 h-6 w-6 group-hover:animate-pulse" />
                  Comenzar Transcripción
                  <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                </Link>
              </Button>
              <Button asChild variant="secondary" size="lg" className="bg-white/10 backdrop-blur-sm border border-white/20 text-primary-700 font-semibold text-lg px-8 py-4 shadow-glass hover:bg-white/20 transition-all duration-300 group">
                <Link to="/config">
                  <Settings className="mr-3 h-6 w-6 group-hover:rotate-90 transition-transform duration-300" />
                  Configurar
                </Link>
              </Button>
            </div>
            
            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto animate-slide-up" style={{animationDelay: '0.6s'}}>
              <div className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-gradient mb-2">5+</div>
                <div className="text-dark-600 font-medium">Formatos de Audio</div>
              </div>
              <div className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-gradient mb-2">2x</div>
                <div className="text-dark-600 font-medium">Velocidad Real</div>
              </div>
              <div className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-gradient mb-2">95%</div>
                <div className="text-dark-600 font-medium">Precisión</div>
              </div>
              <div className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-gradient mb-2">∞</div>
                <div className="text-dark-600 font-medium">Sin Límites</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-24 bg-white/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-dark-800 mb-6">
              Características <span className="text-gradient">Avanzadas</span>
            </h2>
            <p className="text-xl text-dark-600 max-w-3xl mx-auto">
              Tecnología de vanguardia para transformar tu audio en contenido estructurado
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <Card className="group bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl shadow-glass hover-glow transition-all duration-500 hover:scale-105">
              <CardHeader>
                <div className="flex items-center justify-center w-16 h-16 bg-gradient-primary rounded-2xl mb-6 group-hover:animate-pulse">
                  <AudioWaveform className="h-8 w-8 text-white" />
                </div>
                <CardTitle className="text-2xl font-bold text-dark-800">
                  Transcripción Automática
                </CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-dark-600 mb-6 leading-relaxed text-base">
                  Convierte audio a texto usando modelos Whisper de última generación. 
                  Soporte para múltiples idiomas y alta precisión.
                </CardDescription>
                <Link
                  to="/process"
                  className="inline-flex items-center text-primary-600 hover:text-primary-700 font-semibold group"
                >
                  Comenzar ahora
                  <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                </Link>
              </CardContent>
            </Card>

            {/* Feature 2 */}
            <Card className="group bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl shadow-glass hover-glow transition-all duration-500 hover:scale-105">
              <CardHeader>
                <div className="flex items-center justify-center w-16 h-16 bg-gradient-secondary rounded-2xl mb-6 group-hover:animate-pulse">
                  <Brain className="h-8 w-8 text-white" />
                </div>
                <CardTitle className="text-2xl font-bold text-dark-800">
                  Resúmenes Inteligentes
                </CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-dark-600 mb-6 leading-relaxed text-base">
                  Genera resúmenes automáticos y extrae puntos clave usando 
                  Llama 3.1 para análisis profundo del contenido.
                </CardDescription>
                <Link
                  to="/config"
                  className="inline-flex items-center text-secondary-600 hover:text-secondary-700 font-semibold group"
                >
                  Configurar IA
                  <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                </Link>
              </CardContent>
            </Card>

            {/* Feature 3 */}
            <Card className="group bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl shadow-glass hover-glow transition-all duration-500 hover:scale-105">
              <CardHeader>
                <div className="flex items-center justify-center w-16 h-16 bg-gradient-success rounded-2xl mb-6 group-hover:animate-pulse">
                  <Zap className="h-8 w-8 text-white" />
                </div>
                <CardTitle className="text-2xl font-bold text-dark-800">
                  Procesamiento Rápido
                </CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-dark-600 mb-6 leading-relaxed text-base">
                  Optimizado para GPU con fallback a CPU. Procesa archivos 
                  largos sin límites de memoria o tiempo.
                </CardDescription>
                <Link
                  to="/history"
                  className="inline-flex items-center text-success-600 hover:text-success-700 font-semibold group"
                >
                  Ver historial
                  <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                </Link>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-24 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-dark"></div>
        <div className="absolute inset-0 bg-gradient-glass"></div>
        
        <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="animate-fade-in">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              ¿Listo para <span className="text-gradient">Transformar</span> tu Audio?
            </h2>
            <p className="text-xl text-white/80 mb-12 leading-relaxed">
              Únete a miles de usuarios que ya están convirtiendo sus archivos de audio 
              en contenido valioso con nuestra plataforma de IA.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
              <Button asChild size="lg" className="bg-white text-dark-800 font-bold py-4 px-8 rounded-xl shadow-glow hover:shadow-glow-lg transition-all duration-300 transform hover:scale-105 text-lg group">
                <Link to="/process">
                  <AudioWaveform className="mr-3 h-6 w-6 group-hover:animate-pulse" />
                  Procesar Audio Ahora
                  <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                </Link>
              </Button>
              
              <div className="flex items-center space-x-4 text-white/60">
                <div className="flex items-center">
                  <Download className="h-5 w-5 mr-2" />
                  <span>Sin instalación</span>
                </div>
                <div className="w-1 h-1 bg-white/40 rounded-full"></div>
                <div className="flex items-center">
                  <Sparkles className="h-5 w-5 mr-2" />
                  <span>Gratis para empezar</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;