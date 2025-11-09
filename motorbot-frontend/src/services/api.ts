/**
 * API Client Service
 * Handles all HTTP requests to the backend API
 */

import axios, { type AxiosInstance, type AxiosError } from 'axios';

// Get API base URL from environment or use default
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3201';

class ApiClient {
  private client: AxiosInstance;

  constructor(baseURL: string = API_BASE_URL) {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  // Health Check
  async getHealth() {
    const response = await this.client.get('/api/health');
    return response.data;
  }

  // Port Endpoints
  async discoverPorts() {
    const response = await this.client.post('/api/ports/discover');
    return response.data;
  }

  async listPorts(activeOnly = false) {
    const response = await this.client.get('/api/ports', {
      params: { active_only: activeOnly },
    });
    return response.data;
  }

  async getPort(portId: number) {
    const response = await this.client.get(`/api/ports/${portId}`);
    return response.data;
  }

  async getAvailablePorts() {
    const response = await this.client.get('/api/ports/available');
    return response.data;
  }

  // Motor Endpoints
  async listMotors(calibratedOnly = false, functionalOnly = false) {
    const response = await this.client.get('/api/motors', {
      params: {
        calibrated_only: calibratedOnly,
        functional_only: functionalOnly,
      },
    });
    return response.data;
  }

  async getMotor(motorId: number) {
    const response = await this.client.get(`/api/motors/${motorId}`);
    return response.data;
  }

  async getAllMotorsStatus() {
    const response = await this.client.get('/api/motors/status/all');
    return response.data;
  }

  async getMotorStatus(motorId: number) {
    const response = await this.client.get(`/api/motors/${motorId}/status`);
    return response.data;
  }

  async createMotor(motorData: any) {
    const response = await this.client.post('/api/motors', motorData);
    return response.data;
  }

  async updateMotor(motorId: number, motorData: any) {
    const response = await this.client.put(`/api/motors/${motorId}`, motorData);
    return response.data;
  }

  async calibrateMotor(motorId: number) {
    const response = await this.client.post(`/api/motors/${motorId}/calibrate`);
    return response.data;
  }

  async deleteMotor(motorId: number) {
    const response = await this.client.delete(`/api/motors/${motorId}`);
    return response.data;
  }

  // Configuration Endpoints
  async getMotorConfig(motorId: number) {
    const response = await this.client.get(`/api/motors/${motorId}/config`);
    return response.data;
  }

  async createMotorConfig(motorId: number, configData: any) {
    const response = await this.client.post(
      `/api/motors/${motorId}/config`,
      configData
    );
    return response.data;
  }

  async updateMotorConfig(motorId: number, configData: any) {
    const response = await this.client.put(
      `/api/motors/${motorId}/config`,
      configData
    );
    return response.data;
  }

  async applyConfigPreset(motorId: number, presetName: string) {
    const response = await this.client.post(
      `/api/motors/${motorId}/config/preset/${presetName}`
    );
    return response.data;
  }

  async getConfigPresets() {
    const response = await this.client.get('/api/motors/config/presets');
    return response.data;
  }

  async resetConfigToDefault(motorId: number) {
    const response = await this.client.post(`/api/motors/${motorId}/config/reset`);
    return response.data;
  }

  async compareConfigurations(motorId1: number, motorId2: number) {
    const response = await this.client.get('/api/motors/config/compare', {
      params: {
        motor_id_1: motorId1,
        motor_id_2: motorId2,
      },
    });
    return response.data;
  }

  // Telemetry Endpoints
  async recordTelemetry(motorId: number, telemetryData: any) {
    const response = await this.client.post(
      `/api/motors/${motorId}/telemetry`,
      telemetryData
    );
    return response.data;
  }

  async getLatestTelemetry(motorId: number) {
    const response = await this.client.get(
      `/api/motors/${motorId}/telemetry/latest`
    );
    return response.data;
  }

  async getTelemetryRange(
    motorId: number,
    hours = 24,
    limit = 100,
    offset = 0
  ) {
    const response = await this.client.get(`/api/motors/${motorId}/telemetry`, {
      params: { hours, limit, offset },
    });
    return response.data;
  }

  async getTelemetryStatistics(motorId: number, hours = 24) {
    const response = await this.client.get(
      `/api/motors/${motorId}/telemetry/statistics`,
      { params: { hours } }
    );
    return response.data;
  }

  async detectAnomalies(motorId: number, limit = 100) {
    const response = await this.client.get(
      `/api/motors/${motorId}/telemetry/anomalies`,
      { params: { limit } }
    );
    return response.data;
  }

  async getAllMotorsLatestTelemetry() {
    const response = await this.client.get('/api/motors/telemetry/all/latest');
    return response.data;
  }

  // Test Endpoints
  async getAvailableTests(motorId: number) {
    const response = await this.client.get(
      `/api/motors/${motorId}/tests/available`
    );
    return response.data;
  }

  async executeTest(motorId: number, testRequest: any) {
    const response = await this.client.post(
      `/api/motors/${motorId}/tests/execute`,
      testRequest
    );
    return response.data;
  }

  async getTestResult(motorId: number, testId: number) {
    const response = await this.client.get(
      `/api/motors/${motorId}/tests/${testId}`
    );
    return response.data;
  }

  async getMotorTests(motorId: number, testType?: string, limit = 50, offset = 0) {
    const response = await this.client.get(`/api/motors/${motorId}/tests`, {
      params: { test_type: testType, limit, offset },
    });
    return response.data;
  }

  async getTestHistory(motorId: number) {
    const response = await this.client.get(
      `/api/motors/${motorId}/tests/history`
    );
    return response.data;
  }

  async runAllTests(motorId: number) {
    const response = await this.client.post(
      `/api/motors/${motorId}/tests/run-all`
    );
    return response.data;
  }

  // Operations Endpoints
  async getOperations(
    motorId: number,
    operationType?: string,
    limit = 50,
    offset = 0
  ) {
    const response = await this.client.get(
      `/api/motors/${motorId}/operations`,
      {
        params: {
          operation_type: operationType,
          limit,
          offset,
        },
      }
    );
    return response.data;
  }

  async getOperationDetails(motorId: number, operationId: number) {
    const response = await this.client.get(
      `/api/motors/${motorId}/operations/${operationId}`
    );
    return response.data;
  }

  async getOperationsSummary(motorId: number) {
    const response = await this.client.get(
      `/api/motors/${motorId}/operations/summary`
    );
    return response.data;
  }

  async getOperationsByType(motorId: number, operationType: string) {
    const response = await this.client.get('/api/motors/operations/by-type', {
      params: { motor_id: motorId, operation_type: operationType },
    });
    return response.data;
  }

  async getOperationsByStatus(motorId: number, status: string) {
    const response = await this.client.get('/api/motors/operations/by-status', {
      params: { motor_id: motorId, status },
    });
    return response.data;
  }

  async getOperationsTimeline(motorId: number, hours = 24) {
    const response = await this.client.get('/api/motors/operations/timeline', {
      params: { motor_id: motorId, hours },
    });
    return response.data;
  }

  async createOperation(motorId: number, operationData: any) {
    const response = await this.client.post(`/api/motors/${motorId}/operations`, operationData);
    return response.data;
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
export default ApiClient;
