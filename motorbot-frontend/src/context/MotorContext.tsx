/**
 * Motor Context
 * Global context for managing motor state and operations
 */

import React, { createContext, useContext, useEffect } from 'react';
import { webSocketService } from '../services/websocket';
import { useMotors, type Motor } from '../hooks/useMotors';
import { useTelemetry, type TelemetryData } from '../hooks/useTelemetry';
import { useTests, type TestResult } from '../hooks/useTests';
import { useOperations, type Operation } from '../hooks/useOperations';

interface MotorContextType {
  // Motor state
  motors: Motor[];
  selectedMotorId: number | null;
  setSelectedMotorId: (id: number | null) => void;
  selectedMotor: Motor | undefined;

  // Motor operations
  motorState: {
    loading: boolean;
    error: string | null;
  };
  createMotor: (data: any) => Promise<Motor | null>;
  updateMotor: (id: number, data: any) => Promise<Motor | null>;
  deleteMotor: (id: number) => Promise<boolean>;
  calibrateMotor: (id: number) => Promise<boolean>;
  refreshMotors: () => Promise<void>;

  // Telemetry state
  currentTelemetry: TelemetryData | null;
  telemetryLoading: boolean;
  telemetryError: string | null;
  recordTelemetry: (motorId: number, data: any) => Promise<boolean>;
  refreshTelemetry: (motorId: number) => Promise<void>;

  // Test state
  testResults: TestResult[];
  testLoading: boolean;
  testError: string | null;
  executeTest: (motorId: number, testType: string) => Promise<TestResult | null>;
  runAllTests: (motorId: number) => Promise<boolean>;
  refreshTests: (motorId: number) => Promise<void>;

  // Operations state
  operations: Operation[];
  operationLoading: boolean;
  operationError: string | null;
  createOperation: (motorId: number, operation: any) => Promise<Operation | null>;
  refreshOperations: (motorId: number) => Promise<void>;

  // WebSocket
  wsConnected: boolean;
  connectWebSocket: () => Promise<void>;
  disconnectWebSocket: () => void;
}

const MotorContext = createContext<MotorContextType | undefined>(undefined);

interface MotorContextProviderProps {
  children: React.ReactNode;
}

export const MotorContextProvider: React.FC<MotorContextProviderProps> = ({ children }) => {
  const [selectedMotorId, setSelectedMotorId] = React.useState<number | null>(null);
  const [wsConnected, setWsConnected] = React.useState(false);

  // Hooks
  const motors = useMotors();
  const telemetry = useTelemetry(selectedMotorId ?? undefined);
  const tests = useTests(selectedMotorId ?? undefined);
  const operations = useOperations(selectedMotorId ?? undefined);

  const selectedMotor = motors.motors.find((m) => m.id === selectedMotorId);

  // Initialize WebSocket connection (disabled until backend implements it)
  useEffect(() => {
    // WebSocket endpoint not yet implemented in backend
    // Leaving this as a placeholder for future real-time features
    setWsConnected(false);
  }, []);

  const connectWebSocket = async () => {
    try {
      await webSocketService.connect();
      setWsConnected(true);
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      setWsConnected(false);
    }
  };

  const disconnectWebSocket = () => {
    webSocketService.disconnect();
    setWsConnected(false);
  };

  const contextValue: MotorContextType = {
    // Motor state
    motors: motors.motors,
    selectedMotorId,
    setSelectedMotorId,
    selectedMotor,

    // Motor operations
    motorState: {
      loading: motors.loading,
      error: motors.error,
    },
    createMotor: motors.createMotor,
    updateMotor: motors.updateMotor,
    deleteMotor: motors.deleteMotor,
    calibrateMotor: motors.calibrateMotor,
    refreshMotors: motors.refresh,

    // Telemetry state
    currentTelemetry: telemetry.currentTelemetry,
    telemetryLoading: telemetry.loading,
    telemetryError: telemetry.error,
    recordTelemetry: telemetry.recordTelemetry,
    refreshTelemetry: telemetry.refresh,

    // Test state
    testResults: tests.testResults,
    testLoading: tests.loading,
    testError: tests.error,
    executeTest: tests.executeTest,
    runAllTests: tests.runAllTests,
    refreshTests: tests.refresh,

    // Operations state
    operations: operations.operations,
    operationLoading: operations.loading,
    operationError: operations.error,
    createOperation: operations.createOperation,
    refreshOperations: operations.refresh,

    // WebSocket
    wsConnected,
    connectWebSocket,
    disconnectWebSocket,
  };

  return (
    <MotorContext.Provider value={contextValue}>
      {children}
    </MotorContext.Provider>
  );
};

/**
 * Hook to use Motor Context
 */
export const useMotorContext = (): MotorContextType => {
  const context = useContext(MotorContext);
  if (!context) {
    throw new Error('useMotorContext must be used within MotorContextProvider');
  }
  return context;
};

export default MotorContext;
