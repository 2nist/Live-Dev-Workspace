/**
 * AI Assistant React Hook
 * Provides AI-powered code generation, suggestions, and analysis
 */

import { useState, useCallback, useRef } from 'react';
import { getAIService } from '../services/aiService';
import { getArrangerOSC } from '../utils/ArrangerOSC';

export const useAIAssistant = (config = {}) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [errors, setErrors] = useState([]);
  
  const aiService = useRef(getAIService(config));
  const arrangerOSC = useRef(getArrangerOSC());

  /**
   * Generate code from natural language prompt
   */
  const generateCode = useCallback(async (context) => {
    setIsGenerating(true);
    try {
      // Enhance context with arranger data if connected
      if (arrangerOSC.current.connected) {
        const arrangement = await arrangerOSC.current.getCurrentArrangement();
        context.arrangerData = arrangement;
      }

      const result = await aiService.current.generateFromNaturalLanguage(context);
      return result;
    } catch (error) {
      console.error('Code generation failed:', error);
      throw error;
    } finally {
      setIsGenerating(false);
    }
  }, []);

  /**
   * Get real-time code suggestions
   */
  const getSuggestions = useCallback(async (context) => {
    try {
      const newSuggestions = await aiService.current.getSuggestions(context);
      setSuggestions(newSuggestions);
      return newSuggestions;
    } catch (error) {
      console.error('Failed to get suggestions:', error);
      return [];
    }
  }, []);

  /**
   * Analyze code for errors and issues
   */
  const analyzeCode = useCallback(async (code, context = {}) => {
    try {
      const analysisErrors = await aiService.current.analyzeCode(code, context);
      setErrors(analysisErrors);
      return analysisErrors;
    } catch (error) {
      console.error('Code analysis failed:', error);
      return [];
    }
  }, []);

  /**
   * Generate fixes for detected errors
   */
  const generateFixes = useCallback(async (errors, code) => {
    try {
      const fixes = await aiService.current.generateFixes(errors, code);
      return fixes;
    } catch (error) {
      console.error('Fix generation failed:', error);
      return [];
    }
  }, []);

  /**
   * Explain code in natural language
   */
  const explainCode = useCallback(async (code) => {
    setIsGenerating(true);
    try {
      const explanation = await aiService.current.explainCode(code);
      return explanation;
    } catch (error) {
      console.error('Code explanation failed:', error);
      throw error;
    } finally {
      setIsGenerating(false);
    }
  }, []);

  /**
   * Generate code with arranger theory integration
   */
  const generateWithTheory = useCallback(async (type, options = {}) => {
    setIsGenerating(true);
    try {
      let code = '';
      
      switch (type) {
        case 'arpeggiator':
          const chords = await arrangerOSC.current.getChordSuggestions(
            options.rootChord || 'Cmaj7',
            options.style || 'pop'
          );
          code = generateArpeggiatorCode(chords, options);
          break;

        case 'chord-player':
          const progression = await arrangerOSC.current.getCurrentArrangement();
          code = generateChordPlayerCode(progression, options);
          break;

        case 'scale-randomizer':
          const scales = await arrangerOSC.current.getScales(
            options.root || 'C',
            options.scaleType || 'all'
          );
          code = generateScaleRandomizerCode(scales[0], options);
          break;

        case 'rhythm-generator':
          code = generateRhythmGeneratorCode(options);
          break;

        default:
          throw new Error(`Unknown theory type: ${type}`);
      }

      return {
        code,
        type,
        options,
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('Theory-based generation failed:', error);
      throw error;
    } finally {
      setIsGenerating(false);
    }
  }, []);

  /**
   * Get arranger connection status
   */
  const getArrangerStatus = useCallback(() => {
    return {
      connected: arrangerOSC.current.connected,
      host: arrangerOSC.current.host,
      port: arrangerOSC.current.port
    };
  }, []);

  return {
    // State
    isGenerating,
    suggestions,
    errors,
    
    // Methods
    generateCode,
    getSuggestions,
    analyzeCode,
    generateFixes,
    explainCode,
    generateWithTheory,
    getArrangerStatus,
    
    // Services
    aiService: aiService.current,
    arrangerOSC: arrangerOSC.current
  };
};

// ==========================================
// Code Generation Helpers
// ==========================================

function generateArpeggiatorCode(chords, options = {}) {
  const pattern = options.pattern || [0, 1, 2, 1];
  const chordData = chords.map(c => ({ symbol: c.symbol, notes: c.notes }));

  return `// AI-Generated MIDI Arpeggiator
// Pattern: ${JSON.stringify(pattern)}
// ${chords.length} chords from arranger system

inlets = 2;  // [0] bang to trigger, [1] chord index
outlets = 1; // MIDI note output

var chords = ${JSON.stringify(chordData, null, 2)};
var currentChord = 0;
var currentNote = 0;
var pattern = ${JSON.stringify(pattern)};

function bang() {
  if (chords.length === 0) return;
  
  var chord = chords[currentChord];
  var noteIndex = pattern[currentNote % pattern.length];
  var midiNote = chord.notes[noteIndex % chord.notes.length];
  
  outlet(0, midiNote);
  
  currentNote++;
  if (currentNote >= pattern.length * ${options.cycles || 2}) {
    currentNote = 0;
  }
}

function msg_int(chordIndex) {
  currentChord = Math.max(0, Math.min(chordIndex, chords.length - 1));
  currentNote = 0;
  post("Switched to: " + chords[currentChord].symbol + "\\n");
}

function setPattern() {
  pattern = arrayfromargs(arguments);
  currentNote = 0;
  post("Pattern updated: " + pattern + "\\n");
}`;
}

function generateChordPlayerCode(arrangement, options = {}) {
  const sections = arrangement.sections || [];
  const allChords = sections.flatMap(s => 
    s.chords.map(c => ({ symbol: c.symbol, notes: c.notes }))
  );

  return `// AI-Generated Chord Player
// From arrangement: ${arrangement.name}
// ${allChords.length} chords across ${sections.length} sections

inlets = 1;  // bang to play next chord
outlets = 2; // [0] MIDI notes, [1] chord name

var chords = ${JSON.stringify(allChords, null, 2)};
var currentChord = 0;

function bang() {
  if (chords.length === 0) return;
  
  var chord = chords[currentChord];
  
  // Output chord name
  outlet(1, chord.symbol);
  
  // Output all notes
  for (var i = 0; i < chord.notes.length; i++) {
    outlet(0, chord.notes[i]);
  }
  
  currentChord = (currentChord + 1) % chords.length;
}

function reset() {
  currentChord = 0;
  post("Reset to first chord\\n");
}

function goto(index) {
  currentChord = Math.max(0, Math.min(index, chords.length - 1));
  post("Jumped to chord " + index + ": " + chords[currentChord].symbol + "\\n");
}`;
}

function generateScaleRandomizerCode(scale, options = {}) {
  const probability = options.probability || 50;

  return `// AI-Generated Scale Randomizer
// Scale: ${scale.name}
// Notes: ${JSON.stringify(scale.notes)}

inlets = 2;  // [0] MIDI note in, [1] probability %
outlets = 1; // MIDI note out

var probability = ${probability};
var scale = ${JSON.stringify(scale.notes)};

function msg_int(note) {
  if (Math.random() * 100 < probability) {
    // Randomize to scale note
    var scaleNote = scale[Math.floor(Math.random() * scale.length)];
    var octave = Math.floor(note / 12);
    var randomNote = (octave * 12) + (scaleNote % 12);
    outlet(0, randomNote);
  } else {
    // Pass through original
    outlet(0, note);
  }
}

function msg_float(prob) {
  probability = Math.max(0, Math.min(100, prob));
  post("Probability: " + probability + "%\\n");
}

function setScale() {
  scale = arrayfromargs(arguments);
  post("Scale updated: " + scale + "\\n");
}`;
}

function generateRhythmGeneratorCode(options = {}) {
  const steps = options.steps || 16;
  const pulses = options.pulses || 4;

  return `// AI-Generated Euclidean Rhythm
// Steps: ${steps}, Pulses: ${pulses}

inlets = 3;  // [0] bang, [1] steps, [2] pulses
outlets = 1; // 1 for hit, 0 for rest

var steps = ${steps};
var pulses = ${pulses};
var currentStep = 0;
var pattern = [];

function bang() {
  if (pattern.length === 0) {
    generatePattern();
  }
  
  var hit = pattern[currentStep % pattern.length];
  outlet(0, hit);
  
  currentStep++;
  if (currentStep >= pattern.length) {
    currentStep = 0;
  }
}

function generatePattern() {
  pattern = euclidean(steps, pulses);
  post("Generated pattern: " + pattern + "\\n");
}

function euclidean(steps, pulses) {
  var pattern = [];
  for (var i = 0; i < steps; i++) {
    pattern[i] = Math.floor((i * pulses) / steps) !== Math.floor(((i - 1) * pulses) / steps) ? 1 : 0;
  }
  return pattern;
}

function setSteps(s) {
  steps = s;
  generatePattern();
}

function setPulses(p) {
  pulses = p;
  generatePattern();
}

// Initialize
generatePattern();`;
}

export default useAIAssistant;
