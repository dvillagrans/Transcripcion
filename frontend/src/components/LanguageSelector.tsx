interface LanguageSelectorProps {
  value: string;
  onChange: (language: string) => void;
  className?: string;
}

const languages = [
  { code: 'es', name: 'Español' },
  { code: 'en', name: 'English' },
  { code: 'fr', name: 'Français' },
  { code: 'de', name: 'Deutsch' },
  { code: 'it', name: 'Italiano' },
  { code: 'pt', name: 'Português' },
  { code: 'ru', name: 'Русский' },
  { code: 'ja', name: '日本語' },
  { code: 'ko', name: '한국어' },
  { code: 'zh', name: '中文' },
  { code: 'ar', name: 'العربية' },
  { code: 'hi', name: 'हिन्दी' },
  { code: 'auto', name: 'Auto-detectar' }
];

export function LanguageSelector({ value, onChange, className = '' }: LanguageSelectorProps) {
  return (
    <div className={`flex flex-col gap-2 ${className}`}>
      <label htmlFor="language-select" className="text-sm font-medium text-gray-700">
        Idioma de transcripción
      </label>
      <select
        id="language-select"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
      >
        {languages.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.name}
          </option>
        ))}
      </select>
      <p className="text-xs text-gray-500">
        Selecciona el idioma principal del audio para mejorar la precisión
      </p>
    </div>
  );
}

export default LanguageSelector;