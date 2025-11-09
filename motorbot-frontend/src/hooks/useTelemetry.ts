/**
 * useTelemetry Hook
 * Manages telemetry data, statistics, and real-time updates
 */

import { useState, useCallback, useEffect } from 'react';
import { apiClient } from '../services/api';
import { webSocketService, type TelemetryData } from '../services/websocket';

export type { TelemetryData };

export interface TelemetryPoint {
  id: number;
  motor_id: number;
  angle: number;
  speed: number;
  torque: number;
  temperature: number;
  voltage: number;
  current: number;
  error_code: number | null;
  timestamp: string;
}

export interface TelemetryStatistics {
  average_angle: number;
  average_speed: number;
  average_torque: number;
  average_temperature: number;
  min_temperature: number;
  max_temperature: number;
  min_current: number;
  max_current: number;
  sample_count: number;
  time_period: string;
}

export interface Anomaly {
  id: number;
  motor_id: number;
  anomaly_type: string;
  value: number;
  threshold: number;
  timestamp: string;
  description: string;
}

interface UseTelemetryReturn {
  telemetry: TelemetryPoint[];
  currentTelemetry: TelemetryData | null;
  statistics: TelemetryStatistics | null;
  anomalies: Anomaly[];
  loading: boolean;
  error: string | null;
  recordTelemetry: (motorId: number, data: any) => Promise<boolean>;
  getLatestTelemetry: (motorId: number) => Promise<TelemetryPoint | null>;
  getTelemetryRange: (motorId: number, hours?: number, limit?: number, offset?: number) => Promise<void>;
  getTelemetryStatistics: (motorId: number, hours?: number) => Promise<void>;
  detectAnomalies: (motorId: number, limit?: number) => Promise<void>;
  getAllMotorsLatestTelemetry: () => Promise<void>;
  subscribeTelemetry: (motorId: number) => void;
  unsubscribeTelemetry: (motorId: number) => void;
  refresh: () => Promise<void>;
}

export const useTelemetry = (motorId?: number): UseTelemetryReturn => {
  const [telemetry, setTelemetry] = useState<TelemetryPoint[]>([]);
  const [currentTelemetry, setCurrentTelemetry] = useState<TelemetryData | null>(null);
  const [statistics, setStatistics] = useState<TelemetryStatistics | null>(null);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleError = (err: any) => {
    const message = err?.response?.data?.detail || err?.message || 'An error occurred';
    setError(message);
    console.error('Telemetry error:', message);
  };

  const recordTelemetry = useCallback(
    async (id: number, data: any) => {
      try {
        setError(null);
        await apiClient.recordTelemetry(id, data);
        return true;
      } catch (err) {
        handleError(err);
        return false;
      }
    },
    []
  );

  const getLatestTelemetry = useCallback(async (id: number) => {
    try {
      setError(null);
      const data = await apiClient.getLatestTelemetry(id);
      return data;
    } catch (err) {
      handleError(err);
      return null;
    }
  }, []);

  const getTelemetryRange = useCallback(
    async (id: number, hours = 24, limit = 100, offset = 0) => {
      setLoading(true);
      setError(null);
      try {
        const data = await apiClient.getTelemetryRange(id, hours, limit, offset);
        setTelemetry(data.data || []);
      } catch (err) {
        handleError(err);
        setTelemetry([]);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const getTelemetryStatistics = useCallback(
    async (id: number, hours = 24) => {
      setLoading(true);
      setError(null);
      try {
        const data = await apiClient.getTelemetryStatistics(id, hours);
        setStatistics(data.statistics || null);
      } catch (err) {
        handleError(err);
        setStatistics(null);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const detectAnomalies = useCallback(
    async (id: number, limit = 100) => {
      setLoading(true);
      setError(null);
      try {
        const data = await apiClient.detectAnomalies(id, limit);
        setAnomalies(data.anomalies || []);
      } catch (err) {
        handleError(err);
        setAnomalies([]);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const getAllMotorsLatestTelemetry = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiClient.getAllMotorsLatestTelemetry();
      if (data.telemetry && data.telemetry.length > 0) {
        setCurrentTelemetry(data.telemetry[0]);
      }
    } catch (err) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  const subscribeTelemetry = useCallback(
    (id: number) => {
      webSocketService.subscribeTelemetry(id, (data) => {
        if ('angle' in data && 'speed' in data) {
          setCurrentTelemetry(data as TelemetryData);
          setTelemetry((prev) => [data as any, ...prev].slice(0, 100));
        }
      });
    },
    []
  );

  const unsubscribeTelemetry = useCallback((id: number) => {
    webSocketService.unsubscribeTelemetry(id);
  }, []);

  const refresh = useCallback(async () => {
    if (motorId) {
      await getTelemetryRange(motorId);
      await getTelemetryStatistics(motorId);
      await detectAnomalies(motorId);
    }
  }, [motorId, getTelemetryRange, getTelemetryStatistics, detectAnomalies]);

  // Subscribe to telemetry updates when motorId changes
  useEffect(() => {
    if (motorId && webSocketService.isConnected()) {
      subscribeTelemetry(motorId);
      return () => {
        unsubscribeTelemetry(motorId);
      };
    }
  }, [motorId, subscribeTelemetry, unsubscribeTelemetry]);

  return {
    telemetry,
    currentTelemetry,
    statistics,
    anomalies,
    loading,
    error,
    recordTelemetry,
    getLatestTelemetry,
    getTelemetryRange,
    getTelemetryStatistics,
    detectAnomalies,
    getAllMotorsLatestTelemetry,
    subscribeTelemetry,
    unsubscribeTelemetry,
    refresh,
  };
};
