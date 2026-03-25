import { useLanguage } from '../../contexts/LanguageContext';
import { ChevronDown } from 'lucide-react';
import { useState } from 'react';

const LanguageSelector = () => {
  const { language, languages, changeLanguage } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);

  const selectedLang = languages.find(l => l.code === language);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 bg-white px-4 py-2 rounded-full shadow-sm border border-gray-200"
      >
        <span className="text-gray-700 font-medium">{selectedLang?.name}</span>
        <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-lg border border-gray-200 z-20 py-1">
            {languages.map((lang) => (
              <button
                key={lang.code}
                onClick={() => {
                  changeLanguage(lang.code);
                  setIsOpen(false);
                }}
                className={`w-full text-left px-4 py-3 hover:bg-gray-50 transition-colors
                  ${language === lang.code ? 'bg-primary-50 text-primary-600' : 'text-gray-700'}`}
              >
                <div className="font-medium">{lang.name}</div>
                <div className="text-xs text-gray-500">{lang.englishName}</div>
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default LanguageSelector;