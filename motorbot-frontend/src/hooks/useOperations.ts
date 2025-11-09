/**
 * useOperations Hook
 * Manages operation logging, history, and tracking
 */

import { useState, useCallback, useEffect } from 'react';
import { apiClient } from '../services/api';

export interface Operation {
  id: number;
  motor_id: number;
  operation_type: string;
  status: string;
  description: string;
  result: string | null;
  duration: number | null;
  timestamp: string;
}

export interface OperationSummary {
  motor_id: number;
  motor_name: string;
  total_operations: number;
  successful_operations: number;
  failed_operations: number;
  calibration_count?: number;
  test_count?: number;
  control_count?: number;
  configuration_count?: number;
  first_operation?: string;
  last_operation?: string;
  avg_operation_duration?: number;
}

export interface OperationTimeline {
  [key: string]: Operation[];
}

interface UseOperationsReturn {
  operations: Operation[];
  summary: OperationSummary | null;
  timeline: OperationTimeline | null;
  loading: boolean;
  error: string | null;
  getOperations: (motorId: number, operationType?: string, limit?: number, offset?: number) => Promise<void>;
  getOperationDetails: (motorId: number, operationId: number) => Promise<Operation | null>;
  createOperation: (motorId: number, operation: any) => Promise<Operation | null>;
  getOperationsSummary: (motorId: number) => Promise<void>;
  getOperationsByType: (motorId: number, operationType: string) => Promise<void>;
  getOperationsByStatus: (motorId: number, status: string) => Promise<void>;
  getOperationsTimeline: (motorId: number, hours?: number) => Promise<void>;
  refresh: (motorId: number) => Promise<void>;
}

export const useOperations = (motorId?: number): UseOperationsReturn => {
  const [operations, setOperations] = useState<Operation[]>([]);
  const [summary, setSummary] = useState<OperationSummary | null>(null);
  const [timeline, setTimeline] = useState<OperationTimeline | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleError = (err: any) => {
    const message = err?.response?.data?.detail || err?.message || 'An error occurred';
    setError(message);
    console.error('Operation error:', message);
  };

  const getOperations = useCallback(
    async (id: number, operationType?: string, limit = 50, offset = 0) => {
      setLoading(true);
      setError(null);
      try {
        const data = await apiClient.getOperations(id, operationType, limit, offset);
        setOperations(data.logs || []);
      } catch (err) {
        handleError(err);
        setOperations([]);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const getOperationDetails = useCallback(async (id: number, operationId: number) => {
    try {
      setError(null);
      const data = await apiClient.getOperationDetails(id, operationId);
      return data;
    } catch (err) {
      handleError(err);
      return null;
    }
  }, []);

  const createOperation = useCallback(async (id: number, operation: any) => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiClient.createOperation(id, operation);
      setOperations((prev) => [data, ...prev]);
      return data;
    } catch (err) {
      handleError(err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const getOperationsSummary = useCallback(async (id: number) => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiClient.getOperationsSummary(id);
      setSummary(data);
    } catch (err) {
      handleError(err);
      setSummary(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const getOperationsByType = useCallback(
    async (id: number, operationType: string) => {
      setLoading(true);
      setError(null);
      try {
        const data = await apiClient.getOperationsByType(id, operationType);
        setOperations(data.operations || []);
      } catch (err) {
        handleError(err);
        setOperations([]);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const getOperationsByStatus = useCallback(
    async (id: number, status: string) => {
      setLoading(true);
      setError(null);
      try {
        const data = await apiClient.getOperationsByStatus(id, status);
        setOperations(data.operations || []);
      } catch (err) {
        handleError(err);
        setOperations([]);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const getOperationsTimeline = useCallback(
    async (id: number, hours = 24) => {
      setLoading(true);
      setError(null);
      try {
        const data = await apiClient.getOperationsTimeline(id, hours);
        setTimeline(data.timeline || null);
        // Also collect operations from timeline
        if (data.timeline) {
          const allOps = Object.values(data.timeline).flat() as Operation[];
          setOperations(allOps);
        }
      } catch (err) {
        handleError(err);
        setTimeline(null);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const refresh = useCallback(
    async (id: number) => {
      await getOperations(id);
      await getOperationsSummary(id);
      await getOperationsTimeline(id);
    },
    [getOperations, getOperationsSummary, getOperationsTimeline]
  );

  // Load operations when motorId changes
  useEffect(() => {
    if (motorId) {
      getOperations(motorId);
      getOperationsSummary(motorId);
      getOperationsTimeline(motorId);
    }
  }, [motorId, getOperations, getOperationsSummary, getOperationsTimeline]);

  return {
    operations,
    summary,
    timeline,
    loading,
    error,
    getOperations,
    getOperationDetails,
    createOperation,
    getOperationsSummary,
    getOperationsByType,
    getOperationsByStatus,
    getOperationsTimeline,
    refresh,
  };
};
