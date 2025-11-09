/**
 * i18n Configuration
 * Internationalization setup for English and Korean
 */

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import en from './en.json';
import ko from './ko.json';

// Get user's preferred language
const getUserLanguage = (): string => {
  const saved = localStorage.getItem('language');
  if (saved) return saved;

  const browserLang = navigator.language.split('-')[0];
  return ['ko', 'en'].includes(browserLang) ? browserLang : 'en';
};

i18n
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      ko: { translation: ko },
    },
    lng: getUserLanguage(),
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;
