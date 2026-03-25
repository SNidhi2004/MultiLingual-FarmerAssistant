import { createContext, useState, useContext } from 'react';

const LanguageContext = createContext();

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState('hi-IN'); // Default Hindi
  const [languageName, setLanguageName] = useState('हिन्दी');

  const languages = [
    { code: 'hi-IN', name: 'हिन्दी', englishName: 'Hindi' },
    { code: 'te-IN', name: 'తెలుగు', englishName: 'Telugu' },
    { code: 'ta-IN', name: 'தமிழ்', englishName: 'Tamil' },
    { code: 'kn-IN', name: 'ಕನ್ನಡ', englishName: 'Kannada' },
    { code: 'ml-IN', name: 'മലയാളം', englishName: 'Malayalam' },
    { code: 'en-IN', name: 'English', englishName: 'English' },
  ];

  const changeLanguage = (code) => {
    const selected = languages.find(lang => lang.code === code);
    setLanguage(code);
    setLanguageName(selected?.name || 'हिन्दी');
  };

  return (
    <LanguageContext.Provider value={{
      language,
      languageName,
      languages,
      changeLanguage
    }}>
      {children}
    </LanguageContext.Provider>
  );
};