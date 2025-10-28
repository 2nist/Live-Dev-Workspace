/**
 * M4L Knowledge Base
 * Common patterns, examples, and tutorials for Max for Live development
 */

export const M4L_KNOWLEDGE = {
  // Common object patterns
  patterns: {
    midiEffect: {
      title: 'MIDI Effect Template',
      description: 'Basic structure for a MIDI effect device',
      objects: [
        { type: 'midiin', purpose: 'Receive MIDI from Live' },
        { type: 'midiparse', purpose: 'Parse MIDI messages' },
        { type: 'midiformat', purpose: 'Format MIDI messages' },
        { type: 'midiout', purpose: 'Send MIDI to Live' }
      ],
      example: `
Basic MIDI effect flow:
midiin → midiparse → [your processing] → midiformat → midiout

Common processing:
- makenote: Create note on/off pairs
- flush: Clear stuck notes
- borax: MIDI utilities
- bag: Chord memory
      `.trim()
    },

    audioEffect: {
      title: 'Audio Effect Template',
      description: 'Basic structure for an audio effect device',
      objects: [
        { type: 'plugin~', purpose: 'Audio input/output' },
        { type: 'live.gain~', purpose: 'Volume control with Live integration' }
      ],
      example: `
Basic audio effect flow:
plugin~ 1 1 → [your processing] → plugin~ 1 1

Common processing:
- filtergraph~: Visual filter design
- biquad~: Multi-mode filter
- delay~: Audio delay
- pfft~: FFT processing
      `.trim()
    },

    liveAPI: {
      title: 'Live API Integration',
      description: 'Communicate with Live using the Live Object Model',
      objects: [
        { type: 'live.path', purpose: 'Navigate Live\'s object hierarchy' },
        { type: 'live.object', purpose: 'Get/set Live object properties' },
        { type: 'live.observer', purpose: 'Monitor Live object changes' }
      ],
      example: `
Basic Live API usage:
live.path → live.object → get/set properties

Common paths:
"live_set" - The entire Live set
"live_set tracks N" - Access track N
"live_set view selected_track" - Current track
"this_device" - The current M4L device
      `.trim()
    },

    jsProcessing: {
      title: 'JavaScript Processing',
      description: 'Use JavaScript for complex logic',
      objects: [
        { type: 'js', purpose: 'Execute JavaScript code' },
        { type: 'jsui', purpose: 'Custom UI with JavaScript' }
      ],
      example: `
JavaScript object basics:
- inlets/outlets property defines I/O
- inlet property shows current inlet
- outlet() function sends data
- msg_int/float/list functions receive data

Common uses:
- MIDI note processing
- Custom algorithms
- Data structures
- UI interaction
      `.trim()
    }
  },

  // Common Max objects for M4L
  essentialObjects: {
    midi: [
      { name: 'midiin', description: 'Receive MIDI from Live', category: 'input' },
      { name: 'midiout', description: 'Send MIDI to Live', category: 'output' },
      { name: 'notein', description: 'Parse incoming MIDI notes', category: 'input' },
      { name: 'noteout', description: 'Output MIDI notes', category: 'output' },
      { name: 'ctlin', description: 'Parse incoming MIDI CC', category: 'input' },
      { name: 'ctlout', description: 'Output MIDI CC', category: 'output' },
      { name: 'makenote', description: 'Create note on/off pairs with duration', category: 'utility' },
      { name: 'midiparse', description: 'Parse raw MIDI bytes', category: 'utility' },
      { name: 'midiformat', description: 'Format raw MIDI bytes', category: 'utility' },
      { name: 'flush', description: 'Clear stuck MIDI notes', category: 'utility' }
    ],

    live: [
      { name: 'live.path', description: 'Navigate Live Object Model', category: 'api' },
      { name: 'live.object', description: 'Control Live objects', category: 'api' },
      { name: 'live.observer', description: 'Monitor Live property changes', category: 'api' },
      { name: 'live.dial', description: 'Rotary control with Live integration', category: 'ui' },
      { name: 'live.slider', description: 'Slider control with Live integration', category: 'ui' },
      { name: 'live.toggle', description: 'Toggle button with Live integration', category: 'ui' },
      { name: 'live.menu', description: 'Dropdown menu with Live integration', category: 'ui' },
      { name: 'live.tab', description: 'Tab selector with Live integration', category: 'ui' },
      { name: 'live.text', description: 'Text button with Live integration', category: 'ui' },
      { name: 'live.gain~', description: 'Volume control with meter', category: 'audio' }
    ],

    data: [
      { name: 'coll', description: 'Named data collection', category: 'storage' },
      { name: 'table', description: 'Array of numbers', category: 'storage' },
      { name: 'bag', description: 'Store and recall lists', category: 'storage' },
      { name: 'pattr', description: 'Parameter storage', category: 'storage' },
      { name: 'zl', description: 'List processing', category: 'processing' },
      { name: 'bucket', description: 'List storage with scripting', category: 'storage' }
    ],

    control: [
      { name: 'gate', description: 'Route messages to different outlets', category: 'routing' },
      { name: 'switch', description: 'Switch between inlets', category: 'routing' },
      { name: 'route', description: 'Route messages by first element', category: 'routing' },
      { name: 'select', description: 'Compare input and output on match', category: 'routing' },
      { name: 'split', description: 'Filter numbers by range', category: 'routing' },
      { name: 'trigger', description: 'Output in right-to-left order', category: 'timing' },
      { name: 'delay', description: 'Delay messages', category: 'timing' },
      { name: 'pipe', description: 'Delay messages with data', category: 'timing' },
      { name: 'metro', description: 'Metronome/clock', category: 'timing' }
    ]
  },

  // JavaScript code templates
  jsTemplates: {
    basicStructure: {
      title: 'Basic JS Object Structure',
      code: `
inlets = 1;
outlets = 1;

function msg_int(v) {
    // Process integer input
    outlet(0, v);
}

function msg_float(v) {
    // Process float input
    outlet(0, v);
}

function list() {
    // Process list input
    var args = arrayfromargs(arguments);
    outlet(0, args);
}
      `.trim()
    },

    midiProcessor: {
      title: 'MIDI Note Processor',
      code: `
inlets = 1;
outlets = 1;

var scale = [0, 2, 4, 5, 7, 9, 11]; // Major scale

function list() {
    var args = arrayfromargs(arguments);
    
    if (args.length >= 2) {
        var pitch = args[0];
        var velocity = args[1];
        
        // Quantize to scale
        var note = pitch % 12;
        var octave = Math.floor(pitch / 12);
        
        var quantized = findNearestScaleNote(note);
        var newPitch = (octave * 12) + quantized;
        
        outlet(0, [newPitch, velocity]);
    }
}

function findNearestScaleNote(note) {
    var closest = scale[0];
    var minDist = Math.abs(note - closest);
    
    for (var i = 1; i < scale.length; i++) {
        var dist = Math.abs(note - scale[i]);
        if (dist < minDist) {
            minDist = dist;
            closest = scale[i];
        }
    }
    
    return closest;
}
      `.trim()
    },

    arpeggiator: {
      title: 'Simple Arpeggiator',
      code: `
inlets = 2;
outlets = 1;

var notes = [];
var currentIndex = 0;
var playing = false;

// Inlet 0: note input
// Inlet 1: bang to advance

function list() {
    if (inlet === 0) {
        var pitch = arguments[0];
        var velocity = arguments[1];
        
        if (velocity > 0) {
            // Note on - add to array
            if (notes.indexOf(pitch) === -1) {
                notes.push(pitch);
                notes.sort(function(a, b) { return a - b; });
            }
        } else {
            // Note off - remove from array
            var index = notes.indexOf(pitch);
            if (index !== -1) {
                notes.splice(index, 1);
            }
        }
    }
}

function bang() {
    if (inlet === 1 && notes.length > 0) {
        outlet(0, [notes[currentIndex], 100]);
        currentIndex = (currentIndex + 1) % notes.length;
    }
}

function clear() {
    notes = [];
    currentIndex = 0;
}
      `.trim()
    }
  },

  // Common questions and answers
  faq: [
    {
      question: 'How do I receive MIDI from Live?',
      answer: 'Use `midiin` or `notein` objects. `midiin` gives raw MIDI bytes, while `notein` parses note messages. Connect to `midiparse` if you need to parse raw MIDI.',
      relatedObjects: ['midiin', 'notein', 'midiparse']
    },
    {
      question: 'How do I control Live parameters?',
      answer: 'Use the Live API with `live.path` and `live.object`. Navigate to the parameter using its path (e.g., "live_set tracks 0 devices 0 parameters 0"), then use `live.object` to get or set its value.',
      relatedObjects: ['live.path', 'live.object', 'live.observer']
    },
    {
      question: 'How do I create a custom UI?',
      answer: 'Use `live.*` objects for standard controls (dial, slider, toggle) or `jsui` for completely custom interfaces with JavaScript and graphics.',
      relatedObjects: ['live.dial', 'live.slider', 'jsui']
    },
    {
      question: 'How do I save parameters with my device?',
      answer: 'Use the `pattr` system. Create a `pattr` object for each parameter you want to save, and use `autopattr` to automatically save all `live.*` UI objects.',
      relatedObjects: ['pattr', 'autopattr', 'pattrstorage']
    },
    {
      question: 'How do I sync to Live\'s tempo?',
      answer: 'Use `live.object` to observe "live_set tempo" or use transport objects like `transport` with tempo-sync enabled.',
      relatedObjects: ['live.object', 'transport', 'metro']
    }
  ],

  // Tutorials
  tutorials: [
    {
      id: 'simple-midi-effect',
      title: 'Create a Simple MIDI Effect',
      difficulty: 'beginner',
      steps: [
        {
          instruction: 'Add MIDI input',
          objects: ['notein'],
          description: 'This receives MIDI notes from Live'
        },
        {
          instruction: 'Add a pitch shifter',
          objects: ['+', '7'],
          description: 'Add 7 semitones (perfect fifth) to transpose notes'
        },
        {
          instruction: 'Add MIDI output',
          objects: ['noteout'],
          description: 'Send the transposed notes back to Live'
        },
        {
          instruction: 'Connect the objects',
          connections: [
            'Connect notein left outlet (pitch) to + left inlet',
            'Connect notein middle outlet (velocity) to noteout middle inlet',
            'Connect + outlet to noteout left inlet'
          ],
          description: 'This creates a simple harmonizer'
        }
      ]
    }
  ]
};

// Helper function to search knowledge base
export function searchM4LKnowledge(query) {
  const results = [];
  const lowerQuery = query.toLowerCase();

  // Search patterns
  Object.entries(M4L_KNOWLEDGE.patterns).forEach(([key, pattern]) => {
    if (pattern.title.toLowerCase().includes(lowerQuery) ||
        pattern.description.toLowerCase().includes(lowerQuery)) {
      results.push({ type: 'pattern', ...pattern });
    }
  });

  // Search objects
  Object.values(M4L_KNOWLEDGE.essentialObjects).flat().forEach(obj => {
    if (obj.name.toLowerCase().includes(lowerQuery) ||
        obj.description.toLowerCase().includes(lowerQuery)) {
      results.push({ type: 'object', ...obj });
    }
  });

  // Search FAQ
  M4L_KNOWLEDGE.faq.forEach(faq => {
    if (faq.question.toLowerCase().includes(lowerQuery) ||
        faq.answer.toLowerCase().includes(lowerQuery)) {
      results.push({ type: 'faq', ...faq });
    }
  });

  return results;
}
