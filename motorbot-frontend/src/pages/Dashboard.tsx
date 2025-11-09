/**
 * Dashboard Page
 * Main dashboard showing motor status and real-time telemetry
 */

import React from 'react';
import { useTranslation } from 'react-i18next';
import { useMotorContext } from '../context/MotorContext';
import { Activity, Zap, AlertCircle } from 'lucide-react';

const Dashboard: React.FC = () => {
  const { t } = useTranslation();
  const { motors, selectedMotorId, setSelectedMotorId, motorState } = useMotorContext();

  if (motorState.loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">
            {t('common.loading')}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 md:p-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          {t('dashboard.title')}
        </h1>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse"></div>
          <span className="text-sm text-gray-600 dark:text-gray-400">
            {t('common.online')}
          </span>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white dark:bg-gray-900 p-6 rounded-lg border border-gray-200 dark:border-gray-800">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {t('dashboard.totalMotors')}
              </p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white mt-2">
                {motors.length} / 12
              </p>
            </div>
            <Zap className="w-8 h-8 text-blue-500 opacity-20" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-900 p-6 rounded-lg border border-gray-200 dark:border-gray-800">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {t('dashboard.calibrated')}
              </p>
              <p className="text-2xl font-bold text-green-600 dark:text-green-400 mt-2">
                {motors.filter((m) => m.is_calibrated).length} / 12
              </p>
            </div>
            <Activity className="w-8 h-8 text-green-500 opacity-20" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-900 p-6 rounded-lg border border-gray-200 dark:border-gray-800">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {t('dashboard.functional')}
              </p>
              <p className="text-2xl font-bold text-amber-600 dark:text-amber-400 mt-2">
                {motors.filter((m) => m.is_functional).length} / 12
              </p>
            </div>
            <AlertCircle className="w-8 h-8 text-amber-500 opacity-20" />
          </div>
        </div>
      </div>

      {/* Motor Grid */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          {t('dashboard.motorsList')}
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {motors.map((motor) => (
            <button
              key={motor.id}
              onClick={() => setSelectedMotorId(motor.id)}
              className={`p-4 rounded-lg border-2 transition-colors text-left ${
                selectedMotorId === motor.id
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 hover:border-blue-300 dark:hover:border-blue-700'
              }`}
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white">
                    {motor.name}
                  </h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                    ID: {motor.id}
                  </p>
                </div>
                <div
                  className={`w-3 h-3 rounded-full flex-shrink-0 ${
                    motor.is_functional
                      ? 'bg-green-500'
                      : 'bg-red-500'
                  }`}
                ></div>
              </div>
              <div className="mt-3 text-xs text-gray-600 dark:text-gray-400 space-y-1">
                <p>
                  Calibrated:{' '}
                  <span
                    className={
                      motor.is_calibrated
                        ? 'text-green-600 dark:text-green-400'
                        : 'text-red-600 dark:text-red-400'
                    }
                  >
                    {motor.is_calibrated ? '✓' : '✗'}
                  </span>
                </p>
                <p>Speed: {motor.current_speed} RPM</p>
                <p>Angle: {motor.current_angle}°</p>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Empty state */}
      {motors.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-600 dark:text-gray-400">
            {t('dashboard.noMotors')}
          </p>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
