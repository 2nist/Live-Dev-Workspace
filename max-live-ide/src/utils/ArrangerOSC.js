/**
 * Arranger OSC Client
 * Connects Max Live IDE to the Arranger System for music theory integration
 */

class ArrangerOSCClient {
  constructor(options = {}) {
    this.host = options.host || 'localhost';
    this.port = options.port || 12000;
    this.baseUrl = `http://${this.host}:${this.port}`;
    this.connected = false;
    this.reconnectInterval = options.reconnectInterval || 5000;
    this.reconnectTimer = null;
  }

  /**
   * Test connection to arranger system
   */
  async connect() {
    try {
      const response = await fetch(`${this.baseUrl}/arranger/status`, {
        method: 'GET',
        signal: AbortSignal.timeout(2000)
      });

      if (response.ok) {
        this.connected = true;
        console.log('✅ Connected to Arranger OSC system');
        this.stopReconnect();
        return true;
      }
    } catch (error) {
      this.connected = false;
      console.warn('⚠️ Arranger system not available, using mock mode');
      this.startReconnect();
      return false;
    }
  }

  /**
   * Get chord progression suggestions
   */
  async getChordSuggestions(currentChord, style = 'pop', count = 5) {
    if (!this.connected) {
      return this.getMockChordSuggestions(currentChord, style);
    }

    try {
      const response = await fetch(`${this.baseUrl}/arranger/theory/next_chords`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          current_chord: currentChord,
          style: style,
          count: count
        })
      });

      if (response.ok) {
        const data = await response.json();
        return data.suggestions || [];
      }
    } catch (error) {
      console.error('Failed to get chord suggestions:', error);
    }

    return this.getMockChordSuggestions(currentChord, style);
  }

  /**
   * Analyze chord progression
   */
  async analyzeProgression(chords) {
    if (!this.connected) {
      return this.getMockAnalysis(chords);
    }

    try {
      const response = await fetch(`${this.baseUrl}/arranger/theory/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ progression: chords })
      });

      if (response.ok) {
        const data = await response.json();
        return data.analysis || {};
      }
    } catch (error) {
      console.error('Failed to analyze progression:', error);
    }

    return this.getMockAnalysis(chords);
  }

  /**
   * Get available scales
   */
  async getScales(root = 'C', type = 'all') {
    if (!this.connected) {
      return this.getMockScales(root);
    }

    try {
      const response = await fetch(`${this.baseUrl}/arranger/theory/scales`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ root, type })
      });

      if (response.ok) {
        const data = await response.json();
        return data.scales || [];
      }
    } catch (error) {
      console.error('Failed to get scales:', error);
    }

    return this.getMockScales(root);
  }

  /**
   * Get current arrangement from arranger system
   */
  async getCurrentArrangement() {
    if (!this.connected) {
      return this.getMockArrangement();
    }

    try {
      const response = await fetch(`${this.baseUrl}/arranger/arrangement/current`, {
        method: 'GET'
      });

      if (response.ok) {
        const data = await response.json();
        return data.arrangement || this.getMockArrangement();
      }
    } catch (error) {
      console.error('Failed to get arrangement:', error);
    }

    return this.getMockArrangement();
  }

  /**
   * Generate MIDI notes for a chord
   */
  async getChordNotes(chordSymbol, voicing = 'close', octave = 4) {
    if (!this.connected) {
      return this.getMockChordNotes(chordSymbol, octave);
    }

    try {
      const response = await fetch(`${this.baseUrl}/arranger/theory/chord_notes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chord: chordSymbol,
          voicing: voicing,
          octave: octave
        })
      });

      if (response.ok) {
        const data = await response.json();
        return data.notes || [];
      }
    } catch (error) {
      console.error('Failed to get chord notes:', error);
    }

    return this.getMockChordNotes(chordSymbol, octave);
  }

  /**
   * Disconnect from arranger system
   */
  disconnect() {
    this.connected = false;
    this.stopReconnect();
    console.log('Disconnected from Arranger OSC system');
  }

  /**
   * Start automatic reconnection attempts
   */
  startReconnect() {
    if (this.reconnectTimer) return;

    this.reconnectTimer = setInterval(() => {
      console.log('Attempting to reconnect to Arranger system...');
      this.connect();
    }, this.reconnectInterval);
  }

  /**
   * Stop reconnection attempts
   */
  stopReconnect() {
    if (this.reconnectTimer) {
      clearInterval(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  // ==========================================
  // Mock Data for Development/Offline Mode
  // ==========================================

  getMockChordSuggestions(currentChord, style) {
    const suggestions = {
      'Cmaj7': [
        { symbol: 'Dm7', notes: [62, 65, 69, 72], confidence: 0.9 },
        { symbol: 'Am7', notes: [57, 60, 64, 67], confidence: 0.85 },
        { symbol: 'Fmaj7', notes: [65, 69, 72, 76], confidence: 0.8 },
        { symbol: 'G7', notes: [67, 71, 74, 77], confidence: 0.75 }
      ],
      'Am': [
        { symbol: 'F', notes: [65, 69, 72], confidence: 0.9 },
        { symbol: 'C', notes: [60, 64, 67], confidence: 0.85 },
        { symbol: 'G', notes: [67, 71, 74], confidence: 0.8 },
        { symbol: 'Dm', notes: [62, 65, 69], confidence: 0.75 }
      ]
    };

    return suggestions[currentChord] || [
      { symbol: 'Cmaj7', notes: [60, 64, 67, 71], confidence: 0.7 },
      { symbol: 'Dm7', notes: [62, 65, 69, 72], confidence: 0.6 }
    ];
  }

  getMockAnalysis(chords) {
    return {
      key: 'C major',
      quality: 'major',
      progression_type: 'Common progression (I-IV-V-I)',
      cadence: 'Perfect authentic cadence',
      harmonic_rhythm: 'Regular',
      suggestions: [
        'Strong tonic establishment',
        'Consider adding a ii-V progression',
        'Modal interchange opportunity at measure 3'
      ]
    };
  }

  getMockScales(root) {
    const rootNote = this.noteNameToMidi(root);
    return [
      {
        name: 'Major',
        intervals: [0, 2, 4, 5, 7, 9, 11],
        notes: [0, 2, 4, 5, 7, 9, 11].map(i => rootNote + i)
      },
      {
        name: 'Natural Minor',
        intervals: [0, 2, 3, 5, 7, 8, 10],
        notes: [0, 2, 3, 5, 7, 8, 10].map(i => rootNote + i)
      },
      {
        name: 'Harmonic Minor',
        intervals: [0, 2, 3, 5, 7, 8, 11],
        notes: [0, 2, 3, 5, 7, 8, 11].map(i => rootNote + i)
      },
      {
        name: 'Pentatonic Major',
        intervals: [0, 2, 4, 7, 9],
        notes: [0, 2, 4, 7, 9].map(i => rootNote + i)
      }
    ];
  }

  getMockArrangement() {
    return {
      name: 'Example Song',
      tempo: 120,
      time_signature: '4/4',
      sections: [
        {
          name: 'Intro',
          duration: 8,
          chords: [
            { symbol: 'Cmaj7', notes: [60, 64, 67, 71], duration: 4 },
            { symbol: 'Am7', notes: [57, 60, 64, 67], duration: 4 }
          ]
        },
        {
          name: 'Verse',
          duration: 16,
          chords: [
            { symbol: 'Cmaj7', notes: [60, 64, 67, 71], duration: 4 },
            { symbol: 'Dm7', notes: [62, 65, 69, 72], duration: 4 },
            { symbol: 'G7', notes: [67, 71, 74, 77], duration: 4 },
            { symbol: 'Cmaj7', notes: [60, 64, 67, 71], duration: 4 }
          ]
        },
        {
          name: 'Chorus',
          duration: 16,
          chords: [
            { symbol: 'Fmaj7', notes: [65, 69, 72, 76], duration: 4 },
            { symbol: 'G7', notes: [67, 71, 74, 77], duration: 4 },
            { symbol: 'Em7', notes: [64, 67, 71, 74], duration: 4 },
            { symbol: 'Am7', notes: [57, 60, 64, 67], duration: 4 }
          ]
        }
      ]
    };
  }

  getMockChordNotes(chordSymbol, octave = 4) {
    const chords = {
      'C': [0, 4, 7],
      'Cmaj7': [0, 4, 7, 11],
      'Cm': [0, 3, 7],
      'Cm7': [0, 3, 7, 10],
      'C7': [0, 4, 7, 10],
      'Dm': [2, 5, 9],
      'Dm7': [2, 5, 9, 12],
      'Em': [4, 7, 11],
      'Em7': [4, 7, 11, 14],
      'F': [5, 9, 12],
      'Fmaj7': [5, 9, 12, 16],
      'G': [7, 11, 14],
      'G7': [7, 11, 14, 17],
      'Am': [9, 12, 16],
      'Am7': [9, 12, 16, 19]
    };

    const baseNote = octave * 12;
    const intervals = chords[chordSymbol] || [0, 4, 7];
    
    return intervals.map(interval => baseNote + interval);
  }

  noteNameToMidi(noteName) {
    const notes = { 'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11 };
    const note = noteName[0].toUpperCase();
    const baseNote = notes[note] || 0;
    return 60 + baseNote; // C4 is MIDI 60
  }
}

// Singleton instance
let arrangerOSCInstance = null;

export const getArrangerOSC = (options) => {
  if (!arrangerOSCInstance) {
    arrangerOSCInstance = new ArrangerOSCClient(options);
    // Auto-connect on first access
    arrangerOSCInstance.connect();
  }
  return arrangerOSCInstance;
};

export default ArrangerOSCClient;
