/**
 * Real-Time Parameter Sync Hook
 * Manages bidirectional parameter synchronization between Devible and Ableton Live
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { notifications } from '@mantine/notifications';

/**
 * Real-time parameter sync hook with WebSocket/OSC support
 */
export const useRealTimeSync = (options = {}) => {
  const {
    webSocketUrl = 'ws://localhost:8080',
    oscPort = 9001,
    syncInterval = 50, // ms
    retryAttempts = 3,
    enableBidirectional = true,
    enableOSC = false,
    parameterMappings = {},
    onParameterChange,
    onSyncError,
    onConnectionStateChange
  } = options;

  // State management
  const [isConnected, setIsConnected] = useState(false);
  const [connectionState, setConnectionState] = useState('disconnected');
  const [syncedParameters, setSyncedParameters] = useState(new Map());
  const [parameterValues, setParameterValues] = useState(new Map());
  const [syncErrors, setSyncErrors] = useState([]);
  const [syncStats, setSyncStats] = useState({
    messagesSent: 0,
    messagesReceived: 0,
    avgLatency: 0,
    errorRate: 0
  });

  // Refs for persistent connections
  const wsRef = useRef(null);
  const oscRef = useRef(null);
  const syncIntervalRef = useRef(null);
  const messageQueueRef = useRef([]);
  const latencyTrackerRef = useRef(new Map());
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttemptsRef = useRef(0);

  // WebSocket connection management
  const connectWebSocket = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    try {
      setConnectionState('connecting');
      wsRef.current = new WebSocket(webSocketUrl);

      wsRef.current.onopen = () => {
        console.log('Real-time sync connected via WebSocket');
        setIsConnected(true);
        setConnectionState('connected');
        reconnectAttemptsRef.current = 0;
        
        // Request initial parameter state
        sendMessage({
          type: 'request_parameters',
          timestamp: Date.now()
        });

        onConnectionStateChange?.('connected');
      };

      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleIncomingMessage(data);
        } catch (error) {
          console.error('Error parsing sync message:', error);
          addSyncError('message_parse_error', error.message);
        }
      };

      wsRef.current.onclose = () => {
        console.log('Real-time sync disconnected');
        setIsConnected(false);
        setConnectionState('disconnected');
        onConnectionStateChange?.('disconnected');
        
        // Attempt reconnection
        if (reconnectAttemptsRef.current < retryAttempts) {
          reconnectAttemptsRef.current++;
          const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 10000);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connectWebSocket();
          }, delay);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket sync error:', error);
        setConnectionState('error');
        addSyncError('websocket_error', 'Connection failed');
      };

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setConnectionState('error');
      addSyncError('connection_error', error.message);
    }
  }, [webSocketUrl, retryAttempts, onConnectionStateChange]);

  // OSC connection setup (placeholder for actual OSC implementation)
  const connectOSC = useCallback(() => {
    if (!enableOSC) return;

    try {
      // In a real implementation, this would use an OSC library like 'osc-js'
      console.log(`OSC sync enabled on port ${oscPort}`);
      // oscRef.current = new OSCServer(oscPort);
    } catch (error) {
      console.error('Failed to setup OSC connection:', error);
      addSyncError('osc_error', error.message);
    }
  }, [enableOSC, oscPort]);

  // Handle incoming messages from Live
  const handleIncomingMessage = useCallback((data) => {
    const timestamp = Date.now();
    
    // Update stats
    setSyncStats(prev => ({
      ...prev,
      messagesReceived: prev.messagesReceived + 1
    }));

    // Calculate latency if this is a response
    if (data.messageId && latencyTrackerRef.current.has(data.messageId)) {
      const sendTime = latencyTrackerRef.current.get(data.messageId);
      const latency = timestamp - sendTime;
      
      setSyncStats(prev => ({
        ...prev,
        avgLatency: (prev.avgLatency + latency) / 2
      }));
      
      latencyTrackerRef.current.delete(data.messageId);
    }

    switch (data.type) {
      case 'parameter_update':
        handleParameterUpdate(data);
        break;
        
      case 'parameter_list':
        handleParameterList(data);
        break;
        
      case 'sync_error':
        addSyncError('live_error', data.message);
        break;
        
      case 'heartbeat':
        // Keep connection alive
        sendMessage({
          type: 'heartbeat_response',
          timestamp
        });
        break;
        
      default:
        console.warn('Unknown sync message type:', data.type);
    }
  }, []);

  // Handle parameter updates from Live
  const handleParameterUpdate = useCallback((data) => {
    const { parameterId, value, timestamp } = data;
    
    if (!parameterId) return;

    // Update local parameter value
    setParameterValues(prev => new Map(prev.set(parameterId, {
      value,
      timestamp,
      source: 'live'
    })));

    // Notify parameter change callback
    onParameterChange?.(parameterId, value, 'live');

  }, [onParameterChange]);

  // Handle parameter list from Live
  const handleParameterList = useCallback((data) => {
    const { parameters } = data;
    
    if (!parameters) return;

    const newSyncedParams = new Map();
    parameters.forEach(param => {
      newSyncedParams.set(param.id, {
        id: param.id,
        name: param.name,
        min: param.min,
        max: param.max,
        type: param.type,
        mappedTo: parameterMappings[param.id] || null
      });
    });

    setSyncedParameters(newSyncedParams);
  }, [parameterMappings]);

  // Send message to Live
  const sendMessage = useCallback((message) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      // Queue message for when connection is restored
      messageQueueRef.current.push(message);
      return false;
    }

    try {
      const messageWithId = {
        ...message,
        messageId: generateMessageId(),
        timestamp: Date.now()
      };

      // Track latency for responses
      if (message.type !== 'heartbeat_response') {
        latencyTrackerRef.current.set(messageWithId.messageId, messageWithId.timestamp);
      }

      wsRef.current.send(JSON.stringify(messageWithId));
      
      setSyncStats(prev => ({
        ...prev,
        messagesSent: prev.messagesSent + 1
      }));

      return true;
    } catch (error) {
      console.error('Failed to send sync message:', error);
      addSyncError('send_error', error.message);
      return false;
    }
  }, []);

  // Send parameter update to Live
  const updateParameter = useCallback((parameterId, value, source = 'devible') => {
    if (!isConnected) {
      addSyncError('not_connected', 'Cannot update parameter: not connected to Live');
      return false;
    }

    // Update local state
    setParameterValues(prev => new Map(prev.set(parameterId, {
      value,
      timestamp: Date.now(),
      source
    })));

    // Send to Live
    const success = sendMessage({
      type: 'parameter_update',
      parameterId,
      value,
      source
    });

    if (success) {
      onParameterChange?.(parameterId, value, source);
    }

    return success;
  }, [isConnected, sendMessage, onParameterChange]);

  // Sync parameter from Devible to Live
  const syncParameterToLive = useCallback((nodeId, parameterName, value) => {
    const parameterId = `${nodeId}.${parameterName}`;
    return updateParameter(parameterId, value, 'devible');
  }, [updateParameter]);

  // Request specific parameter from Live
  const requestParameter = useCallback((parameterId) => {
    return sendMessage({
      type: 'request_parameter',
      parameterId
    });
  }, [sendMessage]);

  // Subscribe to parameter changes in Live
  const subscribeToParameter = useCallback((parameterId, options = {}) => {
    return sendMessage({
      type: 'subscribe_parameter',
      parameterId,
      options: {
        updateRate: options.updateRate || syncInterval,
        sendOnChange: options.sendOnChange !== false
      }
    });
  }, [sendMessage, syncInterval]);

  // Unsubscribe from parameter changes
  const unsubscribeFromParameter = useCallback((parameterId) => {
    return sendMessage({
      type: 'unsubscribe_parameter',
      parameterId
    });
  }, [sendMessage]);

  // Bulk parameter sync
  const syncAllParameters = useCallback((nodeParameterMap) => {
    if (!isConnected) return false;

    const updates = Object.entries(nodeParameterMap).map(([nodeId, parameters]) => {
      return Object.entries(parameters).map(([paramName, value]) => ({
        parameterId: `${nodeId}.${paramName}`,
        value
      }));
    }).flat();

    return sendMessage({
      type: 'bulk_parameter_update',
      updates,
      source: 'devible'
    });
  }, [isConnected, sendMessage]);

  // Error handling
  const addSyncError = useCallback((type, message) => {
    const error = {
      type,
      message,
      timestamp: Date.now(),
      id: Math.random().toString(36).substr(2, 9)
    };

    setSyncErrors(prev => [...prev.slice(-9), error]); // Keep last 10 errors
    
    setSyncStats(prev => ({
      ...prev,
      errorRate: (prev.errorRate + 1) / (prev.messagesSent + prev.messagesReceived + 1)
    }));

    onSyncError?.(error);

    // Show user notification for critical errors
    if (type === 'connection_error' || type === 'websocket_error') {
      notifications.show({
        title: 'Sync Error',
        message: `Connection to Live lost: ${message}`,
        color: 'red',
        autoClose: 5000
      });
    }
  }, [onSyncError]);

  // Generate unique message ID
  const generateMessageId = () => {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  };

  // Process queued messages when connection is restored
  const processMessageQueue = useCallback(() => {
    if (messageQueueRef.current.length === 0) return;

    const queue = [...messageQueueRef.current];
    messageQueueRef.current = [];

    queue.forEach(message => {
      sendMessage(message);
    });
  }, [sendMessage]);

  // Setup periodic sync
  useEffect(() => {
    if (!isConnected) return;

    syncIntervalRef.current = setInterval(() => {
      // Send heartbeat to maintain connection
      sendMessage({
        type: 'heartbeat'
      });

      // Process any queued messages
      processMessageQueue();
    }, syncInterval);

    return () => {
      if (syncIntervalRef.current) {
        clearInterval(syncIntervalRef.current);
      }
    };
  }, [isConnected, syncInterval, sendMessage, processMessageQueue]);

  // Initialize connections
  useEffect(() => {
    connectWebSocket();
    connectOSC();

    return () => {
      // Cleanup connections
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (oscRef.current) {
        // oscRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (syncIntervalRef.current) {
        clearInterval(syncIntervalRef.current);
      }
    };
  }, []);

  // Public API
  return {
    // Connection state
    isConnected,
    connectionState,
    
    // Parameter management
    syncedParameters,
    parameterValues,
    updateParameter,
    syncParameterToLive,
    requestParameter,
    subscribeToParameter,
    unsubscribeFromParameter,
    syncAllParameters,
    
    // Connection control
    connect: connectWebSocket,
    disconnect: () => {
      if (wsRef.current) wsRef.current.close();
    },
    
    // Status and diagnostics
    syncStats,
    syncErrors,
    
    // Utilities
    sendMessage,
    clearErrors: () => setSyncErrors([])
  };
};

export default useRealTimeSync;
