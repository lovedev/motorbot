/**
 * WebSocket Service
 * Handles real-time telemetry streaming and motor status updates
 */

export interface TelemetryData {
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

export interface MotorStatusUpdate {
  motor_id: number;
  status: string;
  timestamp: string;
}

export type WebSocketHandler = (data: TelemetryData | MotorStatusUpdate) => void;

class WebSocketService {
  private ws: WebSocket | null = null;
  private wsBaseUrl: string;
  private handlers: Map<string, Set<WebSocketHandler>> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 3000;
  private messageQueue: Array<{ type: string; data: any }> = [];
  private isConnecting = false;

  constructor(baseUrl?: string) {
    // Convert http/https to ws/wss
    // Get the base URL from the API client's configuration
    const apiUrl = baseUrl || 'http://localhost:3201';
    // Remove /api path if present and convert http to ws
    const cleanApiUrl = apiUrl.replace(/\/api.*$/, '');
    this.wsBaseUrl = cleanApiUrl.replace(/^https?/, 'ws');
  }

  /**
   * Connect to WebSocket server
   */
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        resolve();
        return;
      }

      if (this.isConnecting) {
        reject(new Error('Already connecting'));
        return;
      }

      this.isConnecting = true;

      try {
        this.ws = new WebSocket(`${this.wsBaseUrl}/ws`);

        this.ws.onopen = () => {
          console.log('WebSocket connected');
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          this.flushMessageQueue();
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.isConnecting = false;
          reject(error);
        };

        this.ws.onclose = () => {
          console.log('WebSocket disconnected');
          this.isConnecting = false;
          this.attemptReconnect();
        };
      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /**
   * Subscribe to motor telemetry updates
   */
  subscribeTelemetry(motorId: number, handler: WebSocketHandler): void {
    const key = `telemetry:${motorId}`;
    if (!this.handlers.has(key)) {
      this.handlers.set(key, new Set());
    }
    this.handlers.get(key)!.add(handler);

    // Send subscription message to server
    this.send({
      type: 'subscribe_telemetry',
      motor_id: motorId,
    });
  }

  /**
   * Unsubscribe from motor telemetry updates
   */
  unsubscribeTelemetry(motorId: number, handler?: WebSocketHandler): void {
    const key = `telemetry:${motorId}`;
    if (handler) {
      this.handlers.get(key)?.delete(handler);
    } else {
      this.handlers.delete(key);
    }

    // Send unsubscription message to server if no more handlers
    if (!this.handlers.get(key) || this.handlers.get(key)!.size === 0) {
      this.send({
        type: 'unsubscribe_telemetry',
        motor_id: motorId,
      });
    }
  }

  /**
   * Subscribe to motor status updates
   */
  subscribeMotorStatus(motorId: number, handler: WebSocketHandler): void {
    const key = `status:${motorId}`;
    if (!this.handlers.has(key)) {
      this.handlers.set(key, new Set());
    }
    this.handlers.get(key)!.add(handler);

    this.send({
      type: 'subscribe_status',
      motor_id: motorId,
    });
  }

  /**
   * Unsubscribe from motor status updates
   */
  unsubscribeMotorStatus(motorId: number, handler?: WebSocketHandler): void {
    const key = `status:${motorId}`;
    if (handler) {
      this.handlers.get(key)?.delete(handler);
    } else {
      this.handlers.delete(key);
    }

    if (!this.handlers.get(key) || this.handlers.get(key)!.size === 0) {
      this.send({
        type: 'unsubscribe_status',
        motor_id: motorId,
      });
    }
  }

  /**
   * Subscribe to all motors telemetry (broadcast updates)
   */
  subscribeBroadcast(handler: WebSocketHandler): void {
    const key = 'broadcast:telemetry';
    if (!this.handlers.has(key)) {
      this.handlers.set(key, new Set());
    }
    this.handlers.get(key)!.add(handler);

    this.send({
      type: 'subscribe_broadcast',
    });
  }

  /**
   * Unsubscribe from broadcast updates
   */
  unsubscribeBroadcast(handler?: WebSocketHandler): void {
    const key = 'broadcast:telemetry';
    if (handler) {
      this.handlers.get(key)?.delete(handler);
    } else {
      this.handlers.delete(key);
    }

    if (!this.handlers.get(key) || this.handlers.get(key)!.size === 0) {
      this.send({
        type: 'unsubscribe_broadcast',
      });
    }
  }

  /**
   * Send message through WebSocket
   */
  private send(message: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      // Queue message for when connection is established
      this.messageQueue.push(message);
      if (!this.ws || this.ws.readyState === WebSocket.CLOSED) {
        this.connect().catch((error) => {
          console.error('Failed to reconnect:', error);
        });
      }
    }
  }

  /**
   * Handle incoming WebSocket message
   */
  private handleMessage(data: any): void {
    const { type, motor_id } = data;

    if (type === 'telemetry') {
      const key = `telemetry:${motor_id}`;
      this.handlers.get(key)?.forEach((handler) => {
        handler(data as TelemetryData);
      });
      // Also notify broadcast subscribers
      this.handlers.get('broadcast:telemetry')?.forEach((handler) => {
        handler(data as TelemetryData);
      });
    } else if (type === 'status') {
      const key = `status:${motor_id}`;
      this.handlers.get(key)?.forEach((handler) => {
        handler(data as MotorStatusUpdate);
      });
    }
  }

  /**
   * Attempt to reconnect to WebSocket
   */
  private attemptReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts}) in ${delay}ms`);

      setTimeout(() => {
        this.connect().catch((error) => {
          console.error('Reconnection attempt failed:', error);
        });
      }, delay);
    } else {
      console.error('Max reconnection attempts reached');
    }
  }

  /**
   * Flush queued messages when connection is established
   */
  private flushMessageQueue(): void {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      if (message && this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify(message));
      }
    }
  }

  /**
   * Check if WebSocket is connected
   */
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  /**
   * Get current connection state
   */
  getState(): number {
    return this.ws?.readyState ?? WebSocket.CLOSED;
  }
}

// Export singleton instance
export const webSocketService = new WebSocketService();
export default WebSocketService;
