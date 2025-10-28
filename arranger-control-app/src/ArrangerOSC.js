/**
 * ArrangerOSC Client for Electron App
 * Communicates with the arranger OSC server
 */

class ArrangerOSCClient {
  constructor(options = {}) {
    this.host = options.host || 'localhost';
    this.port = options.port || 12000;
    this.baseUrl = `http://${this.host}:${this.port}`;
    this.connected = false;
    this.reconnectInterval = options.reconnectInterval || 5000;
    this.reconnectTimer = null;
    this.onStatusChange = options.onStatusChange || (() => {});
  }

  async connect() {
    try {
      // Test with a simple endpoint
      const response = await fetch(`${this.baseUrl}/live/get_tempo`, {
        method: 'POST',
        signal: AbortSignal.timeout(2000)
      });

      if (response.ok) {
        this.connected = true;
        console.log('✅ Connected to Arranger OSC system');
        this.stopReconnect();
        this.onStatusChange(true);
        return true;
      }
    } catch (error) {
      this.connected = false;
      console.warn('⚠️ Arranger system not available, will retry...');
      this.startReconnect();
      this.onStatusChange(false);
      return false;
    }
  }

  // Transport controls
  async play() {
    return this.send('/live/play');
  }

  async stop() {
    return this.send('/live/stop');
  }

  async setTempo(tempo) {
    return this.send('/live/set_tempo', { tempo });
  }

  async getTempo() {
    return this.send('/live/get_tempo');
  }

  async getTimeSignature() {
    return this.send('/live/get_time_signature');
  }

  // Scene controls
  async createScene() {
    return this.send('/live/create_scene_index', { index: -1 });
  }

  async triggerScene(index) {
    return this.send('/live/trigger_scene', { index });
  }

  // Clip controls
  async createClip(track, scene, length = 4.0) {
    return this.send('/live/clip/create', { track, scene, length });
  }

  async addNote(track, scene, pitch, start, duration, velocity) {
    return this.send('/live/clip/add_note', {
      track, scene, pitch, start, dur: duration, vel: velocity
    });
  }

  // Track controls
  async setVolume(track, volume) {
    return this.send('/live/track/set/volume', { track, volume });
  }

  async getVolume(track) {
    return this.send('/live/track/get/volume', { track });
  }

  async setPan(track, pan) {
    return this.send('/live/track/set/pan', { track, pan });
  }

  async setMute(track, mute) {
    return this.send('/live/track/set/mute', { track, mute: mute ? 1 : 0 });
  }

  async setSolo(track, solo) {
    return this.send('/live/track/set/solo', { track, solo: solo ? 1 : 0 });
  }

  async setArm(track, arm) {
    return this.send('/live/track/set/arm', { track, arm: arm ? 1 : 0 });
  }

  // Generic send helper
  async send(endpoint, params = {}) {
    if (!this.connected) {
      console.warn('Not connected to arranger system');
      return { error: 'Not connected' };
    }

    try {
      const url = `${this.baseUrl}${endpoint}`;
      const method = Object.keys(params).length > 0 ? 'POST' : 'GET';
      const options = {
        method,
        headers: method === 'POST' ? { 'Content-Type': 'application/json' } : {}
      };

      if (method === 'POST' && Object.keys(params).length > 0) {
        options.body = JSON.stringify(params);
      }

      const response = await fetch(url, options);
      
      if (response.ok) {
        const data = await response.json();
        return data;
      } else {
        console.error(`Request failed: ${endpoint}`, response.statusText);
        return { error: response.statusText };
      }
    } catch (error) {
      console.error(`Request error: ${endpoint}`, error);
      this.connected = false;
      this.onStatusChange(false);
      this.startReconnect();
      return { error: error.message };
    }
  }

  disconnect() {
    this.connected = false;
    this.stopReconnect();
    this.onStatusChange(false);
  }

  startReconnect() {
    if (this.reconnectTimer) return;

    this.reconnectTimer = setInterval(() => {
      console.log('Attempting to reconnect to Arranger system...');
      this.connect();
    }, this.reconnectInterval);
  }

  stopReconnect() {
    if (this.reconnectTimer) {
      clearInterval(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }
}

export default ArrangerOSCClient;
