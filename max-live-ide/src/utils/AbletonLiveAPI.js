/**
 * Ableton Live API Integration for Max Live IDE
 * 
 * Connects the visual patching IDE with Ableton Live through the ableton-js API
 * for real-time synchronization and live device management.
 */

class AbletonLiveAPI {
  constructor(options = {}) {
    this.wsUrl = options.wsUrl || 'ws://localhost:9001';
    this.apiUrl = options.apiUrl || 'http://localhost:9877';
    this.websocket = null;
    this.connected = false;
    this.callbacks = new Map();
    this.eventListeners = new Map();
  }

  async connect() {
    try {
      // Try WebSocket connection first (for real-time updates)
      await this.connectWebSocket();
      
      // Test HTTP API connection
      await this.testConnection();
      
      this.connected = true;
      this.emit('connected');
      return true;
    } catch (error) {
      console.error('Failed to connect to Ableton Live:', error);
      this.connected = false;
      this.emit('error', error);
      return false;
    }
  }

  async connectWebSocket() {
    return new Promise((resolve, reject) => {
      try {
        this.websocket = new WebSocket(this.wsUrl);
        
        this.websocket.onopen = () => {
          console.log('Connected to Ableton Live WebSocket');
          resolve();
        };
        
        this.websocket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };
        
        this.websocket.onclose = () => {
          console.log('Disconnected from Ableton Live WebSocket');
          this.connected = false;
          this.emit('disconnected');
        };
        
        this.websocket.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };
        
        // Timeout after 5 seconds
        setTimeout(() => {
          if (this.websocket.readyState !== WebSocket.OPEN) {
            reject(new Error('WebSocket connection timeout'));
          }
        }, 5000);
        
      } catch (error) {
        reject(error);
      }
    });
  }

  async testConnection() {
    const response = await fetch(`${this.apiUrl}/api/get_session_info`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return response.json();
  }

  async sendCommand(command, params = {}) {
    if (!this.connected) {
      throw new Error('Not connected to Ableton Live');
    }

    try {
      const response = await fetch(`${this.apiUrl}/api/${command}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(params),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return response.json();
    } catch (error) {
      console.error(`Failed to send command ${command}:`, error);
      throw error;
    }
  }

  // Max for Live Device Management
  async loadMaxDevice(trackIndex, devicePath) {
    return this.sendCommand('load_max_device', {
      track_index: trackIndex,
      device_path: devicePath
    });
  }

  async reloadMaxDevice(trackIndex, deviceIndex) {
    return this.sendCommand('reload_max_device', {
      track_index: trackIndex,
      device_index: deviceIndex
    });
  }

  async getMaxDeviceParameters(trackIndex, deviceIndex) {
    return this.sendCommand('get_max_device_parameters', {
      track_index: trackIndex,
      device_index: deviceIndex
    });
  }

  async setMaxDeviceParameter(trackIndex, deviceIndex, parameterName, value) {
    return this.sendCommand('set_max_device_parameter', {
      track_index: trackIndex,
      device_index: deviceIndex,
      parameter_name: parameterName,
      value: value
    });
  }

  // Live Set Management
  async getSessionInfo() {
    return this.sendCommand('get_session_info');
  }

  async getTracks() {
    return this.sendCommand('get_tracks');
  }

  async getDevices(trackIndex) {
    return this.sendCommand('get_devices', { track_index: trackIndex });
  }

  // Real-time Monitoring
  async startParameterMonitoring(trackIndex, deviceIndex, parameterName) {
    const id = `${trackIndex}-${deviceIndex}-${parameterName}`;
    return this.sendCommand('start_parameter_monitoring', {
      id: id,
      track_index: trackIndex,
      device_index: deviceIndex,
      parameter_name: parameterName
    });
  }

  async stopParameterMonitoring(id) {
    return this.sendCommand('stop_parameter_monitoring', { id });
  }

  // Event handling
  on(event, callback) {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, []);
    }
    this.eventListeners.get(event).push(callback);
  }

  off(event, callback) {
    if (this.eventListeners.has(event)) {
      const listeners = this.eventListeners.get(event);
      const index = listeners.indexOf(callback);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    }
  }

  emit(event, data) {
    if (this.eventListeners.has(event)) {
      this.eventListeners.get(event).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in event listener for ${event}:`, error);
        }
      });
    }
  }

  handleMessage(data) {
    const { event, payload } = data;
    
    switch (event) {
      case 'parameter_changed':
        this.emit('parameterChanged', payload);
        break;
      case 'device_added':
        this.emit('deviceAdded', payload);
        break;
      case 'device_removed':
        this.emit('deviceRemoved', payload);
        break;
      case 'track_added':
        this.emit('trackAdded', payload);
        break;
      case 'track_removed':
        this.emit('trackRemoved', payload);
        break;
      default:
        this.emit(event, payload);
    }
  }

  async disconnect() {
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }
    this.connected = false;
    this.emit('disconnected');
  }
}

// Max Device Synchronization Manager
class MaxDeviceSync {
  constructor(abletonAPI) {
    this.api = abletonAPI;
    this.syncedDevices = new Map();
    this.parameterListeners = new Map();
  }

  async syncDevice(patcher, trackIndex, deviceIndex) {
    const deviceId = `${trackIndex}-${deviceIndex}`;
    
    try {
      // Get device parameters from Live
      const parameters = await this.api.getMaxDeviceParameters(trackIndex, deviceIndex);
      
      // Update patcher with Live parameter values
      this.updatePatcherParameters(patcher, parameters);
      
      // Start monitoring parameter changes
      this.startParameterSync(deviceId, trackIndex, deviceIndex, patcher);
      
      this.syncedDevices.set(deviceId, {
        patcher,
        trackIndex,
        deviceIndex,
        parameters
      });
      
      return true;
    } catch (error) {
      console.error('Failed to sync device:', error);
      return false;
    }
  }

  updatePatcherParameters(patcher, parameters) {
    // Find parameter objects in the patcher and update their values
    patcher.objects.forEach(obj => {
      if (obj.maxclass === 'live.numbox' || obj.maxclass === 'live.dial') {
        const paramName = obj.text || obj.box.varname;
        if (parameters[paramName] !== undefined) {
          obj.box.parameter_value = parameters[paramName];
        }
      }
    });
  }

  startParameterSync(deviceId, trackIndex, deviceIndex, patcher) {
    // Listen for parameter changes from Live
    const listener = (data) => {
      if (data.track_index === trackIndex && data.device_index === deviceIndex) {
        this.handleParameterChange(deviceId, data);
      }
    };
    
    this.api.on('parameterChanged', listener);
    this.parameterListeners.set(deviceId, listener);
    
    // Start monitoring all parameters
    patcher.objects.forEach(obj => {
      if (obj.maxclass === 'live.numbox' || obj.maxclass === 'live.dial') {
        const paramName = obj.text || obj.box.varname;
        if (paramName) {
          this.api.startParameterMonitoring(trackIndex, deviceIndex, paramName);
        }
      }
    });
  }

  handleParameterChange(deviceId, data) {
    const device = this.syncedDevices.get(deviceId);
    if (device) {
      // Update the patcher with new parameter value
      const obj = device.patcher.objects.find(o => 
        (o.text || o.box.varname) === data.parameter_name
      );
      
      if (obj) {
        obj.box.parameter_value = data.value;
        // Emit event for UI update
        this.api.emit('patcherParameterChanged', {
          deviceId,
          objectId: obj.id,
          parameterName: data.parameter_name,
          value: data.value
        });
      }
    }
  }

  async stopSync(deviceId) {
    const device = this.syncedDevices.get(deviceId);
    if (device) {
      // Stop parameter monitoring
      const listener = this.parameterListeners.get(deviceId);
      if (listener) {
        this.api.off('parameterChanged', listener);
        this.parameterListeners.delete(deviceId);
      }
      
      this.syncedDevices.delete(deviceId);
    }
  }

  async reloadDevice(deviceId) {
    const device = this.syncedDevices.get(deviceId);
    if (device) {
      try {
        await this.api.reloadMaxDevice(device.trackIndex, device.deviceIndex);
        // Re-sync after reload
        await this.syncDevice(device.patcher, device.trackIndex, device.deviceIndex);
        return true;
      } catch (error) {
        console.error('Failed to reload device:', error);
        return false;
      }
    }
  }
}

export { AbletonLiveAPI, MaxDeviceSync };
