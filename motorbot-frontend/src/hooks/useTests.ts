/**
 * useTests Hook
 * Manages test execution, results, and history
 */

import { useState, useCallback, useEffect } from 'react';
import { apiClient } from '../services/api';

export interface TestType {
  name: string;
  description: string;
  duration_seconds: number;
}

export interface TestResult {
  id: number;
  motor_id: number;
  test_type: string;
  success: boolean;
  start_time: string;
  end_time: string;
  duration_seconds: number;
  min_value: number | null;
  max_value: number | null;
  average_value: number | null;
  error_message: string | null;
}

export interface TestHistory {
  motor_id: number;
  total_tests: number;
  successful_tests: number;
  failed_tests: number;
  success_rate: number;
  by_type: {
    [key: string]: {
      total: number;
      successful: number;
      failed: number;
      success_rate: number;
    };
  };
}

interface UseTestsReturn {
  availableTests: TestType[];
  testResults: TestResult[];
  testHistory: TestHistory | null;
  loading: boolean;
  error: string | null;
  executing: boolean;
  getAvailableTests: (motorId: number) => Promise<void>;
  executeTest: (motorId: number, testType: string) => Promise<TestResult | null>;
  getTestResult: (motorId: number, testId: number) => Promise<TestResult | null>;
  getMotorTests: (motorId: number, testType?: string, limit?: number, offset?: number) => Promise<void>;
  getTestHistory: (motorId: number) => Promise<void>;
  runAllTests: (motorId: number) => Promise<boolean>;
  deleteTestResult: (motorId: number, testId: number) => Promise<boolean>;
  refresh: (motorId: number) => Promise<void>;
}

export const useTests = (motorId?: number): UseTestsReturn => {
  const [availableTests, setAvailableTests] = useState<TestType[]>([]);
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [testHistory, setTestHistory] = useState<TestHistory | null>(null);
  const [loading, setLoading] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleError = (err: any) => {
    const message = err?.response?.data?.detail || err?.message || 'An error occurred';
    setError(message);
    console.error('Test error:', message);
  };

  const getAvailableTests = useCallback(async (id: number) => {
    setError(null);
    try {
      const data = await apiClient.getAvailableTests(id);
      setAvailableTests(data.available_tests || []);
    } catch (err) {
      handleError(err);
      setAvailableTests([]);
    }
  }, []);

  const executeTest = useCallback(async (id: number, testType: string) => {
    setExecuting(true);
    setError(null);
    try {
      const result = await apiClient.executeTest(id, {
        test_type: testType,
      });
      setTestResults((prev) => [result, ...prev]);
      return result;
    } catch (err) {
      handleError(err);
      return null;
    } finally {
      setExecuting(false);
    }
  }, []);

  const getTestResult = useCallback(async (id: number, testId: number) => {
    try {
      setError(null);
      const data = await apiClient.getTestResult(id, testId);
      return data;
    } catch (err) {
      handleError(err);
      return null;
    }
  }, []);

  const getMotorTests = useCallback(
    async (id: number, testType?: string, limit = 50, offset = 0) => {
      setLoading(true);
      setError(null);
      try {
        const data = await apiClient.getMotorTests(id, testType, limit, offset);
        setTestResults(data.tests || []);
      } catch (err) {
        handleError(err);
        setTestResults([]);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const getTestHistory = useCallback(async (id: number) => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiClient.getTestHistory(id);
      setTestHistory(data.summary || null);
    } catch (err) {
      handleError(err);
      setTestHistory(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const runAllTests = useCallback(async (id: number) => {
    setExecuting(true);
    setError(null);
    try {
      await apiClient.runAllTests(id);
      // Refresh test history after running all tests
      await getTestHistory(id);
      return true;
    } catch (err) {
      handleError(err);
      return false;
    } finally {
      setExecuting(false);
    }
  }, [getTestHistory]);

  const deleteTestResult = useCallback(async (id: number, testId: number) => {
    setLoading(true);
    setError(null);
    try {
      await apiClient.getTestResult(id, testId); // This is for deletion in actual API
      setTestResults((prev) => prev.filter((t) => t.id !== testId));
      return true;
    } catch (err) {
      handleError(err);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const refresh = useCallback(
    async (id: number) => {
      await getAvailableTests(id);
      await getMotorTests(id);
      await getTestHistory(id);
    },
    [getAvailableTests, getMotorTests, getTestHistory]
  );

  // Load available tests when motorId changes
  useEffect(() => {
    if (motorId) {
      getAvailableTests(motorId);
      getMotorTests(motorId);
      getTestHistory(motorId);
    }
  }, [motorId, getAvailableTests, getMotorTests, getTestHistory]);

  return {
    availableTests,
    testResults,
    testHistory,
    loading,
    error,
    executing,
    getAvailableTests,
    executeTest,
    getTestResult,
    getMotorTests,
    getTestHistory,
    runAllTests,
    deleteTestResult,
    refresh,
  };
};
