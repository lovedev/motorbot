/**
 * Setup Page
 * Motor bus setup and port discovery
 */

import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useMotorContext } from '../context/MotorContext';
import { Button } from '@/components/ui/button';
import { Search, RefreshCw } from 'lucide-react';

const Setup: React.FC = () => {
  const { t } = useTranslation();
  const { motors, motorState, refreshMotors } = useMotorContext();
  const [discoveryInProgress, setDiscoveryInProgress] = useState(false);

  const handleDiscoverPorts = async () => {
    setDiscoveryInProgress(true);
    try {
      // Discovery logic would go here
      await refreshMotors();
    } finally {
      setDiscoveryInProgress(false);
    }
  };

  return (
    <div className="p-6 md:p-8 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          {t('setup.title')}
        </h1>
      </div>

      {/* Port Discovery Section */}
      <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          {t('setup.discoverPorts')}
        </h2>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          {t('setup.discoverPortsDescription')}
        </p>
        <Button
          onClick={handleDiscoverPorts}
          disabled={discoveryInProgress || motorState.loading}
          className="flex items-center gap-2"
        >
          {discoveryInProgress ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              Discovering...
            </>
          ) : (
            <>
              <Search className="w-4 h-4" />
              {t('setup.discoverButton')}
            </>
          )}
        </Button>
      </div>

      {/* Motors List */}
      <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          {t('setup.motorsList')}
        </h2>
        <div className="space-y-3">
          {motors.map((motor) => (
            <div
              key={motor.id}
              className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-800 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
            >
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white">
                  {motor.name}
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Port: {motor.port_id} • Status: {motor.status}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  {motor.is_functional ? '✓ Functional' : '✗ Non-functional'}
                </p>
              </div>
            </div>
          ))}
        </div>
        {motors.length === 0 && (
          <p className="text-center py-8 text-gray-500 dark:text-gray-400">
            {t('setup.noMotors')}
          </p>
        )}
      </div>
    </div>
  );
};

export default Setup;
