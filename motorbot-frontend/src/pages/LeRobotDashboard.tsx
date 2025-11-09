/**
 * LeRobot Dashboard Page
 * Real-time telemetry and motor status dashboard
 */

import React from 'react';
import { useTranslation } from 'react-i18next';
import { useMotorContext } from '../context/MotorContext';
import { TrendingUp, Gauge, Thermometer, Zap } from 'lucide-react';

const LeRobotDashboard: React.FC = () => {
  const { t } = useTranslation();
  const { motors, selectedMotorId, setSelectedMotorId, currentTelemetry } =
    useMotorContext();

  const selectedMotor = motors.find((m) => m.id === selectedMotorId);

  const telemetryItems = [
    {
      label: 'Angle',
      value: currentTelemetry?.angle || 0,
      unit: '°',
      icon: <Gauge className="w-5 h-5" />,
      color: 'blue',
    },
    {
      label: 'Speed',
      value: currentTelemetry?.speed || 0,
      unit: 'RPM',
      icon: <TrendingUp className="w-5 h-5" />,
      color: 'green',
    },
    {
      label: 'Temperature',
      value: currentTelemetry?.temperature || 0,
      unit: '°C',
      icon: <Thermometer className="w-5 h-5" />,
      color: 'amber',
    },
    {
      label: 'Current',
      value: currentTelemetry?.current || 0,
      unit: 'A',
      icon: <Zap className="w-5 h-5" />,
      color: 'purple',
    },
  ];

  const colorClasses: { [key: string]: string } = {
    blue: 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20',
    green: 'text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20',
    amber: 'text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/20',
    purple: 'text-purple-600 dark:text-purple-400 bg-purple-50 dark:bg-purple-900/20',
  };

  return (
    <div className="p-6 md:p-8 space-y-6">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
        {t('lerobot.title')}
      </h1>

      {/* Motor Selection */}
      <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          {t('common.selectMotor')}
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
          {motors.map((motor) => (
            <button
              key={motor.id}
              onClick={() => setSelectedMotorId(motor.id)}
              className={`p-3 rounded-lg border-2 transition-colors text-left ${
                selectedMotorId === motor.id
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-800 hover:border-blue-300'
              }`}
            >
              <p className="font-semibold text-gray-900 dark:text-white">
                {motor.name}
              </p>
              <p className="text-xs text-gray-600 dark:text-gray-400">
                {motor.status}
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* Telemetry Display */}
      {selectedMotor && (
        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">
            {selectedMotor.name} - {t('lerobot.realTimeTelemetry')}
          </h2>

          {/* Telemetry Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {telemetryItems.map((item) => (
              <div
                key={item.label}
                className={`p-4 rounded-lg border border-gray-200 dark:border-gray-800 ${colorClasses[item.color]}`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {item.label}
                  </span>
                  {item.icon}
                </div>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">
                  {item.value.toFixed(1)}
                  <span className="text-sm ml-1 text-gray-600 dark:text-gray-400">
                    {item.unit}
                  </span>
                </p>
              </div>
            ))}
          </div>

          {/* Status */}
          <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Last updated:{' '}
              {currentTelemetry?.timestamp
                ? new Date(currentTelemetry.timestamp).toLocaleTimeString()
                : 'N/A'}
            </p>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!selectedMotor && (
        <div className="text-center py-12 text-gray-600 dark:text-gray-400">
          <p>{t('common.selectMotorToView')}</p>
        </div>
      )}
    </div>
  );
};

export default LeRobotDashboard;
