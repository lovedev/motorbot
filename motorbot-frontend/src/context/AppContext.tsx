/**
 * App Context
 * Global context for app-wide state like theme, language, and preferences
 */

import React, { createContext, useContext, useEffect, useState } from 'react';

export type Theme = 'light' | 'dark' | 'system';
export type Language = 'en' | 'ko';

export interface AppPreferences {
  theme: Theme;
  language: Language;
  sidebarOpen: boolean;
  autoRefresh: boolean;
  autoRefreshInterval: number; // in seconds
  telemetryUpdateInterval: number; // in seconds
  showNotifications: boolean;
}

interface AppContextType {
  preferences: AppPreferences;
  setTheme: (theme: Theme) => void;
  setLanguage: (language: Language) => void;
  setSidebarOpen: (open: boolean) => void;
  setAutoRefresh: (enabled: boolean) => void;
  setAutoRefreshInterval: (interval: number) => void;
  setTelemetryUpdateInterval: (interval: number) => void;
  setShowNotifications: (show: boolean) => void;
  isDarkMode: boolean;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

// Default preferences
const DEFAULT_PREFERENCES: AppPreferences = {
  theme: 'system',
  language: 'en',
  sidebarOpen: true,
  autoRefresh: true,
  autoRefreshInterval: 5, // 5 seconds
  telemetryUpdateInterval: 1, // 1 second
  showNotifications: true,
};

interface AppContextProviderProps {
  children: React.ReactNode;
}

export const AppContextProvider: React.FC<AppContextProviderProps> = ({ children }) => {
  const [preferences, setPreferences] = useState<AppPreferences>(DEFAULT_PREFERENCES);
  const [isDarkMode, setIsDarkMode] = useState(false);

  // Load preferences from localStorage on mount
  useEffect(() => {
    const savedPreferences = localStorage.getItem('app-preferences');
    if (savedPreferences) {
      try {
        setPreferences((prev) => ({
          ...prev,
          ...JSON.parse(savedPreferences),
        }));
      } catch (error) {
        console.error('Failed to load preferences:', error);
      }
    }

    // Apply theme on mount
    applyTheme(preferences.theme);
  }, []);

  // Apply theme changes
  useEffect(() => {
    applyTheme(preferences.theme);
  }, [preferences.theme]);

  // Update localStorage whenever preferences change
  useEffect(() => {
    localStorage.setItem('app-preferences', JSON.stringify(preferences));
  }, [preferences]);

  const applyTheme = (theme: Theme) => {
    const root = document.documentElement;
    const isDark =
      theme === 'dark' ||
      (theme === 'system' &&
        window.matchMedia('(prefers-color-scheme: dark)').matches);

    setIsDarkMode(isDark);

    if (isDark) {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  };

  const setTheme = (theme: Theme) => {
    setPreferences((prev) => ({
      ...prev,
      theme,
    }));
  };

  const setLanguage = (language: Language) => {
    setPreferences((prev) => ({
      ...prev,
      language,
    }));
  };

  const setSidebarOpen = (open: boolean) => {
    setPreferences((prev) => ({
      ...prev,
      sidebarOpen: open,
    }));
  };

  const setAutoRefresh = (enabled: boolean) => {
    setPreferences((prev) => ({
      ...prev,
      autoRefresh: enabled,
    }));
  };

  const setAutoRefreshInterval = (interval: number) => {
    setPreferences((prev) => ({
      ...prev,
      autoRefreshInterval: Math.max(1, interval),
    }));
  };

  const setTelemetryUpdateInterval = (interval: number) => {
    setPreferences((prev) => ({
      ...prev,
      telemetryUpdateInterval: Math.max(1, interval),
    }));
  };

  const setShowNotifications = (show: boolean) => {
    setPreferences((prev) => ({
      ...prev,
      showNotifications: show,
    }));
  };

  const contextValue: AppContextType = {
    preferences,
    setTheme,
    setLanguage,
    setSidebarOpen,
    setAutoRefresh,
    setAutoRefreshInterval,
    setTelemetryUpdateInterval,
    setShowNotifications,
    isDarkMode,
  };

  return (
    <AppContext.Provider value={contextValue}>
      {children}
    </AppContext.Provider>
  );
};

/**
 * Hook to use App Context
 */
export const useAppContext = (): AppContextType => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within AppContextProvider');
  }
  return context;
};

export default AppContext;
