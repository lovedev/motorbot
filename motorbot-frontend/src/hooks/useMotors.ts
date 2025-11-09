/**
 * useMotors Hook
 * Manages motor CRUD operations and status
 */

import { useState, useCallback, useEffect } from 'react';
import { apiClient } from '../services/api';

export interface Motor {
  id: number;
  name: string;
  port_id: number;
  is_calibrated: boolean;
  is_functional: boolean;
  current_speed: number;
  current_angle: number;
  status: string;
}

interface UseMotorsReturn {
  motors: Motor[];
  loading: boolean;
  error: string | null;
  listMotors: (calibratedOnly?: boolean, functionalOnly?: boolean) => Promise<void>;
  getMotor: (motorId: number) => Promise<Motor | null>;
  createMotor: (motorData: any) => Promise<Motor | null>;
  updateMotor: (motorId: number, motorData: any) => Promise<Motor | null>;
  deleteMotor: (motorId: number) => Promise<boolean>;
  calibrateMotor: (motorId: number) => Promise<boolean>;
  getAllMotorsStatus: () => Promise<void>;
  getMotorStatus: (motorId: number) => Promise<any>;
  refresh: () => Promise<void>;
}

export const useMotors = (): UseMotorsReturn => {
  const [motors, setMotors] = useState<Motor[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleError = (err: any) => {
    const message = err?.response?.data?.detail || err?.message || 'An error occurred';
    setError(message);
    console.error('Motor error:', message);
  };

  const listMotors = useCallback(
    async (calibratedOnly = false, functionalOnly = false) => {
      setLoading(true);
      setError(null);
      try {
        const data = await apiClient.listMotors(calibratedOnly, functionalOnly);
        setMotors(data.motors || []);
      } catch (err) {
        handleError(err);
        setMotors([]);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const getMotor = useCallback(async (motorId: number) => {
    try {
      setError(null);
      const data = await apiClient.getMotor(motorId);
      return data;
    } catch (err) {
      handleError(err);
      return null;
    }
  }, []);

  const createMotor = useCallback(async (motorData: any) => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiClient.createMotor(motorData);
      setMotors((prev) => [...prev, data]);
      return data;
    } catch (err) {
      handleError(err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateMotor = useCallback(async (motorId: number, motorData: any) => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiClient.updateMotor(motorId, motorData);
      setMotors((prev) =>
        prev.map((m) => (m.id === motorId ? data : m))
      );
      return data;
    } catch (err) {
      handleError(err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteMotor = useCallback(async (motorId: number) => {
    setLoading(true);
    setError(null);
    try {
      await apiClient.deleteMotor(motorId);
      setMotors((prev) => prev.filter((m) => m.id !== motorId));
      return true;
    } catch (err) {
      handleError(err);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const calibrateMotor = useCallback(async (motorId: number) => {
    setLoading(true);
    setError(null);
    try {
      await apiClient.calibrateMotor(motorId);
      // Update motor in list
      setMotors((prev) =>
        prev.map((m) => (m.id === motorId ? { ...m, is_calibrated: true } : m))
      );
      return true;
    } catch (err) {
      handleError(err);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const getAllMotorsStatus = useCallback(async () => {
    setError(null);
    try {
      const data = await apiClient.getAllMotorsStatus();
      if (data.motors) {
        setMotors(data.motors);
      }
    } catch (err) {
      handleError(err);
    }
  }, []);

  const getMotorStatus = useCallback(async (motorId: number) => {
    try {
      setError(null);
      const data = await apiClient.getMotorStatus(motorId);
      return data;
    } catch (err) {
      handleError(err);
      return null;
    }
  }, []);

  const refresh = useCallback(async () => {
    await listMotors();
  }, [listMotors]);

  // Auto-fetch motors on mount
  useEffect(() => {
    listMotors();
  }, [listMotors]);

  return {
    motors,
    loading,
    error,
    listMotors,
    getMotor,
    createMotor,
    updateMotor,
    deleteMotor,
    calibrateMotor,
    getAllMotorsStatus,
    getMotorStatus,
    refresh,
  };
};
