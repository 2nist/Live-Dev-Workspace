/**
 * Live Connection Manager
 * Enhanced error handling and user notifications for Live connectivity
 */

import React, { createContext, useContext, useState, useCallback, useRef } from 'react';
import { notifications } from '@mantine/notifications';
import { 
  IconWifi, 
  IconWifiOff, 
  IconAlertTriangle, 
  IconCheck,
  IconRefresh,
  IconSettings
} from '@tabler/icons-react';

// Connection Context
const LiveConnectionContext = createContext();

export const useLiveConnection = () => {
  const context = useContext(LiveConnectionContext);
  if (!context) {
    throw new Error('useLiveConnection must be used within LiveConnectionProvider');
  }
  return context;
};

// Connection States
export const CONNECTION_STATES = {
  DISCONNECTED: 'disconnected',
  CONNECTING: 'connecting', 
  CONNECTED: 'connected',
  RECONNECTING: 'reconnecting',
  ERROR: 'error',
  TIMEOUT: 'timeout'
};

// Error Types
export const ERROR_TYPES = {
  CONNECTION_FAILED: 'connection_failed',
  CONNECTION_LOST: 'connection_lost',
  AUTHENTICATION_FAILED: 'authentication_failed',
  VERSION_MISMATCH: 'version_mismatch',
  TIMEOUT: 'timeout',
  PROTOCOL_ERROR: 'protocol_error',
  LIVE_NOT_RUNNING: 'live_not_running',
  PLUGIN_NOT_INSTALLED: 'plugin_not_installed'
};

// Connection Manager Provider
export const LiveConnectionProvider = ({ children }) => {
  const [connectionState, setConnectionState] = useState(CONNECTION_STATES.DISCONNECTED);
  const [connectionHealth, setConnectionHealth] = useState({
    overall: 0,
    websocket: false,
    http: false,
    udp: false,
    lastPing: null,
    uptime: 0
  });
  const [connectionErrors, setConnectionErrors] = useState([]);
  const [connectionConfig, setConnectionConfig] = useState({
    webSocketUrl: 'ws://localhost:8080',
    httpUrl: 'http://localhost:8081',
    udpPort: 9001,
    timeout: 5000,
    retryAttempts: 3,
    retryDelay: 1000,
    heartbeatInterval: 2000
  });
  const [liveInfo, setLiveInfo] = useState({
    version: null,
    isPlaying: false,
    tempo: 120,
    currentTime: 0,
    devices: []
  });

  // Connection refs
  const wsRef = useRef(null);
  const httpRef = useRef(null);
  const udpRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const heartbeatIntervalRef = useRef(null);
  const connectionStartTimeRef = useRef(null);

  // Error handling and notifications
  const addConnectionError = useCallback((type, message, details = {}) => {
    const error = {
      id: Math.random().toString(36).substr(2, 9),
      type,
      message,
      details,
      timestamp: Date.now(),
      resolved: false
    };

    setConnectionErrors(prev => [...prev.slice(-19), error]); // Keep last 20 errors

    // Show appropriate notification
    const notificationConfig = getErrorNotificationConfig(type, message);
    if (notificationConfig) {
      notifications.show(notificationConfig);
    }

    return error.id;
  }, []);

  // Get notification config for error types
  const getErrorNotificationConfig = (type, message) => {
    const configs = {
      [ERROR_TYPES.CONNECTION_FAILED]: {
        title: 'Connection Failed',
        message: 'Could not connect to Ableton Live',
        color: 'red',
        icon: <IconWifiOff size={16} />,
        autoClose: false,
        actions: [
          {
            label: 'Retry',
            onClick: () => connect()
          },
          {
            label: 'Settings',
            onClick: () => openConnectionSettings()
          }
        ]
      },
      [ERROR_TYPES.CONNECTION_LOST]: {
        title: 'Connection Lost',
        message: 'Connection to Ableton Live was lost',
        color: 'orange',
        icon: <IconAlertTriangle size={16} />,
        autoClose: 5000
      },
      [ERROR_TYPES.LIVE_NOT_RUNNING]: {
        title: 'Ableton Live Not Running',
        message: 'Please start Ableton Live and try again',
        color: 'yellow',
        icon: <IconAlertTriangle size={16} />,
        autoClose: false,
        actions: [
          {
            label: 'Retry',
            onClick: () => connect()
          }
        ]
      },
      [ERROR_TYPES.PLUGIN_NOT_INSTALLED]: {
        title: 'Plugin Not Installed',
        message: 'AbletonJS plugin is not installed in Live',
        color: 'red',
        icon: <IconSettings size={16} />,
        autoClose: false,
        actions: [
          {
            label: 'Installation Guide',
            onClick: () => openInstallationGuide()
          }
        ]
      },
      [ERROR_TYPES.VERSION_MISMATCH]: {
        title: 'Version Mismatch',
        message: 'Plugin version is incompatible',
        color: 'orange',
        icon: <IconRefresh size={16} />,
        autoClose: false
      }
    };

    return configs[type] || {
      title: 'Connection Error',
      message,
      color: 'red',
      icon: <IconAlertTriangle size={16} />
    };
  };

  // Resolve error
  const resolveError = useCallback((errorId) => {
    setConnectionErrors(prev => 
      prev.map(error => 
        error.id === errorId 
          ? { ...error, resolved: true, resolvedAt: Date.now() }
          : error
      )
    );
  }, []);

  // Clear all errors
  const clearErrors = useCallback(() => {
    setConnectionErrors([]);
  }, []);

  // Update connection health
  const updateConnectionHealth = useCallback((updates) => {
    setConnectionHealth(prev => {
      const newHealth = { ...prev, ...updates };
      
      // Calculate overall health score
      const scores = [
        newHealth.websocket ? 40 : 0,
        newHealth.http ? 30 : 0,
        newHealth.udp ? 20 : 0,
        newHealth.lastPing && newHealth.lastPing < 100 ? 10 : 
        newHealth.lastPing && newHealth.lastPing < 500 ? 5 : 0
      ];
      
      newHealth.overall = scores.reduce((sum, score) => sum + score, 0);
      
      return newHealth;
    });
  }, []);

  // WebSocket connection
  const connectWebSocket = useCallback(async () => {
    try {
      if (wsRef.current?.readyState === WebSocket.OPEN) return true;

      return new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
          reject(new Error('WebSocket connection timeout'));
        }, connectionConfig.timeout);

        wsRef.current = new WebSocket(connectionConfig.webSocketUrl);

        wsRef.current.onopen = () => {
          clearTimeout(timeout);
          updateConnectionHealth({ websocket: true });
          resolve(true);
        };

        wsRef.current.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
          } catch (error) {
            addConnectionError(ERROR_TYPES.PROTOCOL_ERROR, 'Invalid message format');
          }
        };

        wsRef.current.onclose = () => {
          updateConnectionHealth({ websocket: false });
          if (connectionState === CONNECTION_STATES.CONNECTED) {
            addConnectionError(ERROR_TYPES.CONNECTION_LOST, 'WebSocket connection closed');
            attemptReconnection();
          }
        };

        wsRef.current.onerror = (error) => {
          clearTimeout(timeout);
          updateConnectionHealth({ websocket: false });
          reject(error);
        };
      });

    } catch (error) {
      addConnectionError(ERROR_TYPES.CONNECTION_FAILED, `WebSocket: ${error.message}`);
      throw error;
    }
  }, [connectionConfig, connectionState, updateConnectionHealth, addConnectionError]);

  // HTTP connection test
  const testHttpConnection = useCallback(async () => {
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), connectionConfig.timeout);

      const response = await fetch(`${connectionConfig.httpUrl}/ping`, {
        signal: controller.signal,
        method: 'GET'
      });

      clearTimeout(timeout);

      if (response.ok) {
        updateConnectionHealth({ http: true });
        return true;
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

    } catch (error) {
      updateConnectionHealth({ http: false });
      
      if (error.name === 'AbortError') {
        addConnectionError(ERROR_TYPES.TIMEOUT, 'HTTP connection timeout');
      } else {
        addConnectionError(ERROR_TYPES.CONNECTION_FAILED, `HTTP: ${error.message}`);
      }
      
      return false;
    }
  }, [connectionConfig, updateConnectionHealth, addConnectionError]);

  // Handle WebSocket messages
  const handleWebSocketMessage = useCallback((data) => {
    switch (data.type) {
      case 'ping_response':
        const latency = Date.now() - data.timestamp;
        updateConnectionHealth({ lastPing: latency });
        break;
        
      case 'live_info':
        setLiveInfo(prev => ({ ...prev, ...data.info }));
        break;
        
      case 'error':
        addConnectionError(ERROR_TYPES.PROTOCOL_ERROR, data.message);
        break;
        
      default:
        // Forward to other handlers
        break;
    }
  }, [updateConnectionHealth, addConnectionError]);

  // Start heartbeat monitoring
  const startHeartbeat = useCallback(() => {
    if (heartbeatIntervalRef.current) return;

    heartbeatIntervalRef.current = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          type: 'ping',
          timestamp: Date.now()
        }));
      }

      // Update uptime
      if (connectionStartTimeRef.current) {
        const uptime = Math.floor((Date.now() - connectionStartTimeRef.current) / 1000);
        updateConnectionHealth({ uptime });
      }
    }, connectionConfig.heartbeatInterval);
  }, [connectionConfig.heartbeatInterval, updateConnectionHealth]);

  // Stop heartbeat monitoring
  const stopHeartbeat = useCallback(() => {
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current);
      heartbeatIntervalRef.current = null;
    }
  }, []);

  // Main connection function
  const connect = useCallback(async () => {
    if (connectionState === CONNECTION_STATES.CONNECTING) return;

    setConnectionState(CONNECTION_STATES.CONNECTING);
    connectionStartTimeRef.current = Date.now();
    
    try {
      // Test HTTP first (fastest check)
      const httpOk = await testHttpConnection();
      
      if (!httpOk) {
        // If HTTP fails, Live might not be running
        setConnectionState(CONNECTION_STATES.ERROR);
        addConnectionError(ERROR_TYPES.LIVE_NOT_RUNNING, 'Ableton Live is not responding');
        return false;
      }

      // Connect WebSocket
      await connectWebSocket();
      
      // TODO: Test UDP connection
      updateConnectionHealth({ udp: true });

      setConnectionState(CONNECTION_STATES.CONNECTED);
      startHeartbeat();

      notifications.show({
        title: 'Connected to Live',
        message: 'Real-time sync is active',
        color: 'green',
        icon: <IconWifi size={16} />
      });

      return true;

    } catch (error) {
      setConnectionState(CONNECTION_STATES.ERROR);
      addConnectionError(ERROR_TYPES.CONNECTION_FAILED, error.message);
      return false;
    }
  }, [connectionState, testHttpConnection, connectWebSocket, updateConnectionHealth, startHeartbeat, addConnectionError]);

  // Disconnect
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    stopHeartbeat();

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setConnectionState(CONNECTION_STATES.DISCONNECTED);
    updateConnectionHealth({
      overall: 0,
      websocket: false,
      http: false,
      udp: false,
      lastPing: null,
      uptime: 0
    });

    notifications.show({
      title: 'Disconnected',
      message: 'Connection to Live closed',
      color: 'gray',
      icon: <IconWifiOff size={16} />
    });
  }, [stopHeartbeat, updateConnectionHealth]);

  // Attempt reconnection
  const attemptReconnection = useCallback(() => {
    if (connectionState === CONNECTION_STATES.RECONNECTING) return;
    if (reconnectTimeoutRef.current) return;

    setConnectionState(CONNECTION_STATES.RECONNECTING);
    
    let attempts = 0;
    const reconnect = async () => {
      attempts++;
      
      if (attempts > connectionConfig.retryAttempts) {
        setConnectionState(CONNECTION_STATES.ERROR);
        addConnectionError(ERROR_TYPES.CONNECTION_FAILED, 'Reconnection attempts exceeded');
        return;
      }

      const success = await connect();
      
      if (!success) {
        const delay = connectionConfig.retryDelay * Math.pow(2, attempts - 1);
        reconnectTimeoutRef.current = setTimeout(reconnect, delay);
      }
    };

    reconnect();
  }, [connectionState, connectionConfig, connect, addConnectionError]);

  // Update connection configuration
  const updateConfig = useCallback((newConfig) => {
    setConnectionConfig(prev => ({ ...prev, ...newConfig }));
  }, []);

  // Utility functions
  const openConnectionSettings = () => {
    // This would open a settings modal/panel
    console.log('Open connection settings');
  };

  const openInstallationGuide = () => {
    // This would open installation documentation
    window.open('https://github.com/leolabs/ableton-js#installation', '_blank');
  };

  const getConnectionStatus = useCallback(() => {
    return {
      state: connectionState,
      health: connectionHealth,
      errors: connectionErrors.filter(e => !e.resolved),
      isConnected: connectionState === CONNECTION_STATES.CONNECTED,
      canConnect: connectionState === CONNECTION_STATES.DISCONNECTED || connectionState === CONNECTION_STATES.ERROR
    };
  }, [connectionState, connectionHealth, connectionErrors]);

  // Context value
  const value = {
    // State
    connectionState,
    connectionHealth,
    connectionErrors,
    connectionConfig,
    liveInfo,
    
    // Actions
    connect,
    disconnect,
    updateConfig,
    
    // Error management
    addConnectionError,
    resolveError,
    clearErrors,
    
    // Utilities
    getConnectionStatus,
    isConnected: connectionState === CONNECTION_STATES.CONNECTED
  };

  return (
    <LiveConnectionContext.Provider value={value}>
      {children}
    </LiveConnectionContext.Provider>
  );
};

export default LiveConnectionContext;
