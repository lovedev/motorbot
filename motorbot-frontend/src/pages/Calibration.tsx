/**
 * Calibration Page
 * Motor calibration interface
 */

import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useMotorContext } from '../context/MotorContext';
import { Button } from '@/components/ui/button';
import { ZapOff, CheckCircle, AlertTriangle } from 'lucide-react';

const Calibration: React.FC = () => {
  const { t } = useTranslation();
  const { motors, selectedMotorId, setSelectedMotorId, calibrateMotor } =
    useMotorContext();
  const [calibrating, setCalibrating] = useState<number | null>(null);

  const selectedMotor = motors.find((m) => m.id === selectedMotorId);

  const handleCalibrate = async (motorId: number) => {
    setCalibrating(motorId);
    try {
      await calibrateMotor(motorId);
    } finally {
      setCalibrating(null);
    }
  };

  return (
    <div className="p-6 md:p-8 space-y-6">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
        {t('calibration.title')}
      </h1>

      {/* Motor Selection */}
      <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          {t('calibration.selectMotor')}
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {motors.map((motor) => (
            <button
              key={motor.id}
              onClick={() => setSelectedMotorId(motor.id)}
              className={`p-3 rounded-lg border-2 transition-colors ${
                selectedMotorId === motor.id
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-800 hover:border-gray-300 dark:hover:border-gray-700'
              }`}
            >
              <p className="font-semibold text-gray-900 dark:text-white">
                {motor.name.split(' ')[1] || motor.name}
              </p>
              {motor.is_calibrated && (
                <CheckCircle className="w-4 h-4 text-green-500 mx-auto mt-2" />
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Calibration Status */}
      {selectedMotor && (
        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            {selectedMotor.name}
          </h2>

          {selectedMotor.is_calibrated ? (
            <div className="flex items-center gap-3 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
              <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
              <div>
                <p className="font-semibold text-green-900 dark:text-green-100">
                  {t('calibration.calibrated')}
                </p>
                <p className="text-sm text-green-700 dark:text-green-300">
                  {t('calibration.calibratedDescription')}
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center gap-3 p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
                <AlertTriangle className="w-5 h-5 text-amber-600 dark:text-amber-400" />
                <div>
                  <p className="font-semibold text-amber-900 dark:text-amber-100">
                    {t('calibration.notCalibrated')}
                  </p>
                  <p className="text-sm text-amber-700 dark:text-amber-300">
                    {t('calibration.notCalibratedDescription')}
                  </p>
                </div>
              </div>

              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">
                  {t('calibration.instructions')}
                </h3>
                <ol className="list-decimal list-inside space-y-1 text-sm text-blue-700 dark:text-blue-300">
                  <li>{t('calibration.step1')}</li>
                  <li>{t('calibration.step2')}</li>
                  <li>{t('calibration.step3')}</li>
                </ol>
              </div>

              <Button
                onClick={() => handleCalibrate(selectedMotor.id)}
                disabled={calibrating === selectedMotor.id}
                size="lg"
                className="w-full"
              >
                {calibrating === selectedMotor.id ? (
                  <>
                    <ZapOff className="w-4 h-4 mr-2 animate-pulse" />
                    Calibrating...
                  </>
                ) : (
                  <>
                    <ZapOff className="w-4 h-4 mr-2" />
                    {t('calibration.startButton')}
                  </>
                )}
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Calibration;
