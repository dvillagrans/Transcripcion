import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { AudioWaveform, Settings, History, Home, Menu, X, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader } from '@/components/ui/card';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navigation = [
    { name: 'Inicio', href: '/', icon: Home, description: 'Página principal' },
    { name: 'Configuración', href: '/config', icon: Settings, description: 'Ajustar parámetros' },
    { name: 'Procesamiento', href: '/process', icon: AudioWaveform, description: 'Transcribir audio' },
    { name: 'Historial', href: '/history', icon: History, description: 'Ver trabajos anteriores' },
  ];

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50/30 via-white to-secondary-50/30">
      {/* Mobile menu button */}
      <div className="lg:hidden fixed top-4 left-4 z-50">
        <Button
          variant="secondary"
          size="icon"
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="p-2 rounded-xl bg-white/80 backdrop-blur-sm shadow-lg hover:shadow-glow transition-all duration-300 border-0"
        >
          {sidebarOpen ? (
            <X className="h-6 w-6 text-dark-700" />
          ) : (
            <Menu className="h-6 w-6 text-dark-700" />
          )}
        </Button>
      </div>

      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-40 w-72 transform transition-transform duration-300 ease-in-out lg:translate-x-0 ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        {/* Sidebar backdrop */}
        <div className="absolute inset-0 glass-container border-r border-white/20"></div>
        
        {/* Sidebar content */}
        <div className="relative h-full flex flex-col">
          {/* Logo */}
          <div className="flex h-20 items-center justify-center px-6 border-b border-white/10">
            <Link to="/" className="flex items-center space-x-3 group">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-primary rounded-xl blur opacity-75 group-hover:opacity-100 transition-opacity"></div>
                <div className="relative bg-gradient-primary p-2 rounded-xl">
                  <AudioWaveform className="h-8 w-8 text-white" />
                </div>
              </div>
              <div className="flex flex-col">
                <span className="text-xl font-bold text-gradient">Audio Pipeline</span>
                <span className="text-xs text-dark-500 font-medium">Powered by AI</span>
              </div>
            </Link>
          </div>
          
          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {navigation.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.href);
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={`group flex items-center space-x-4 rounded-2xl px-4 py-3 text-sm font-medium transition-all duration-300 relative overflow-hidden ${
                    active
                      ? 'bg-gradient-primary text-white shadow-glow'
                      : 'text-dark-700 hover:bg-white/50 hover:shadow-lg'
                  }`}
                >
                  {active && (
                    <div className="absolute inset-0 bg-gradient-primary opacity-10 animate-pulse"></div>
                  )}
                  <div className={`relative p-2 rounded-xl transition-all duration-300 ${
                    active 
                      ? 'bg-white/20' 
                      : 'bg-white/30 group-hover:bg-white/50'
                  }`}>
                    <Icon className={`h-5 w-5 transition-all duration-300 ${
                      active 
                        ? 'text-white' 
                        : 'text-dark-600 group-hover:text-primary-600'
                    }`} />
                  </div>
                  <div className="flex-1 relative">
                    <div className={`font-semibold transition-colors ${
                      active ? 'text-white' : 'text-dark-800 group-hover:text-primary-700'
                    }`}>
                      {item.name}
                    </div>
                    <div className={`text-xs transition-colors ${
                      active ? 'text-white/80' : 'text-dark-500 group-hover:text-primary-500'
                    }`}>
                      {item.description}
                    </div>
                  </div>
                  {active && (
                    <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                  )}
                </Link>
              );
            })}
          </nav>
          
          {/* Footer */}
          <div className="px-4 pb-6">
            <Card className="bg-gradient-secondary/10 backdrop-blur-sm border border-white/20">
              <CardHeader className="pb-3">
                <div className="flex items-center space-x-3">
                  <Sparkles className="h-5 w-5 text-secondary-600" />
                  <span className="text-sm font-semibold text-dark-800">Estado del Sistema</span>
                </div>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between items-center">
                    <span className="text-dark-600">Backend</span>
                    <Badge variant="secondary" className="bg-success-100 text-success-800 border-success-200 text-xs">
                      <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse mr-1"></div>
                      Activo
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-dark-600">IA Service</span>
                    <Badge variant="secondary" className="bg-success-100 text-success-800 border-success-200 text-xs">
                      <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse mr-1"></div>
                      Listo
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-dark-900/50 backdrop-blur-sm z-30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        ></div>
      )}

      {/* Main content */}
      <div className="lg:pl-72 transition-all duration-300">
        <main className="min-h-screen">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;