/**
 * Main App Component
 * Root application with routing and global context providers
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { MotorContextProvider } from './context/MotorContext';
import { AppContextProvider } from './context/AppContext';
import { MainLayout } from './components/Layout';

// Lazy load pages for better performance
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const Setup = React.lazy(() => import('./pages/Setup'));
const Calibration = React.lazy(() => import('./pages/Calibration'));
const LeRobotDashboard = React.lazy(() => import('./pages/LeRobotDashboard'));
const LearningCenter = React.lazy(() => import('./pages/LearningCenter'));

function App() {
  return (
    <Router>
      <AppContextProvider>
        <MotorContextProvider>
          <Routes>
            <Route
              path="/*"
              element={
                <MainLayout>
                  <React.Suspense
                    fallback={
                      <div className="flex items-center justify-center h-full">
                        <div className="text-center">
                          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                          <p className="text-gray-600 dark:text-gray-400">Loading...</p>
                        </div>
                      </div>
                    }
                  >
                    <Routes>
                      <Route path="/" element={<Dashboard />} />
                      <Route path="/setup" element={<Setup />} />
                      <Route path="/calibration" element={<Calibration />} />
                      <Route path="/lerobot" element={<LeRobotDashboard />} />
                      <Route path="/learning" element={<LearningCenter />} />
                      <Route path="*" element={<Navigate to="/" replace />} />
                    </Routes>
                  </React.Suspense>
                </MainLayout>
              }
            />
          </Routes>
        </MotorContextProvider>
      </AppContextProvider>
    </Router>
  );
}

export default App;
