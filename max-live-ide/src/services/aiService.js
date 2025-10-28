/**
 * AI Service for Code Generation and Assistance
 * Supports multiple AI providers with fallback options
 */

class AIService {
  constructor(config = {}) {
    this.provider = config.provider || 'mock'; // 'openai', 'anthropic', 'mock'
    this.apiKey = config.apiKey || null;
    this.model = config.model || 'gpt-4';
    this.temperature = config.temperature || 0.7;
    this.maxTokens = config.maxTokens || 1000;
    this.enabled = config.enabled !== false;
  }

  /**
   * Generate code from natural language prompt
   */
  async generateFromNaturalLanguage(context) {
    const { prompt, maxObjectType, arrangerConnection, existingPatch } = context;

    const systemPrompt = `You are an expert Max for Live JavaScript developer. Generate clean, efficient Max JS code.
    
Max JS Constraints:
- Use 'inlets' and 'outlets' variables to declare I/O
- Use outlet(index, value) to send data
- Use msg_int(), msg_float(), bang() for inlet handlers
- No return statements - use outlet() instead
- Keep code concise and performant

Current Context:
- Object Type: ${maxObjectType}
- Arranger Integration: ${arrangerConnection ? 'Available' : 'Not available'}
- Existing Patch: ${existingPatch ? 'Yes' : 'Empty patch'}`;

    const userPrompt = `Generate Max JavaScript code for: ${prompt}

Requirements:
1. Include inlet/outlet declarations
2. Add clear comments
3. Follow Max JS best practices
4. Make it production-ready`;

    if (this.provider === 'mock') {
      return this.generateMockCode(prompt, context);
    }

    try {
      const response = await this.callAIProvider(systemPrompt, userPrompt);
      return {
        code: this.extractCode(response),
        explanation: this.extractExplanation(response),
        parameters: this.extractParameters(response),
        usage: this.extractUsage(response)
      };
    } catch (error) {
      console.error('AI generation failed:', error);
      return this.generateMockCode(prompt, context);
    }
  }

  /**
   * Get code suggestions based on current context
   */
  async getSuggestions(context) {
    const { code, cursor, objectType, connectedObjects, patchContext } = context;

    // Extract context around cursor
    const lines = code.split('\n');
    const cursorLine = this.getCursorLine(code, cursor);
    const currentLine = lines[cursorLine] || '';

    // Analyze what user is typing
    const suggestions = [];

    // Max JS specific suggestions
    if (currentLine.trim().startsWith('function')) {
      suggestions.push(...this.getMaxFunctionSuggestions());
    }

    if (currentLine.includes('outlet(')) {
      suggestions.push(...this.getOutletSuggestions(connectedObjects));
    }

    if (currentLine.includes('inlet')) {
      suggestions.push(...this.getInletHandlerSuggestions());
    }

    // Add AI-powered suggestions if enabled
    if (this.enabled && this.provider !== 'mock') {
      const aiSuggestions = await this.getAISuggestions(context);
      suggestions.push(...aiSuggestions);
    }

    return suggestions;
  }

  /**
   * Analyze code for errors and issues
   */
  async analyzeCode(code, context = {}) {
    const errors = [];

    // Basic syntax validation
    try {
      new Function(code);
    } catch (e) {
      errors.push({
        type: 'error',
        message: `Syntax Error: ${e.message}`,
        line: this.extractLineNumber(e),
        severity: 'error'
      });
    }

    // Max JS specific validation
    errors.push(...this.validateMaxJSPatterns(code));

    // Performance analysis
    errors.push(...this.analyzePerformance(code));

    // AI-powered semantic analysis
    if (this.enabled && this.provider !== 'mock') {
      const semanticIssues = await this.analyzeSemantics(code, context);
      errors.push(...semanticIssues);
    }

    return errors;
  }

  /**
   * Generate fixes for detected errors
   */
  async generateFixes(errors, code) {
    const fixes = [];

    for (const error of errors) {
      let fix = null;

      // Pattern-based fixes
      if (error.type === 'missing-inlets-outlets') {
        fix = {
          description: 'Add inlet and outlet declarations',
          code: 'inlets = 1;\noutlets = 1;\n\n' + code,
          confidence: 0.95
        };
      } else if (error.type === 'return-instead-of-outlet') {
        fix = {
          description: 'Replace return with outlet()',
          code: code.replace(/return\s+(.+);/g, 'outlet(0, $1);'),
          confidence: 0.9
        };
      } else if (this.enabled && this.provider !== 'mock') {
        // AI-generated fix
        fix = await this.generateAIFix(error, code);
      }

      if (fix) {
        fixes.push({ error, fix });
      }
    }

    return fixes;
  }

  /**
   * Explain code in natural language
   */
  async explainCode(code) {
    if (this.provider === 'mock') {
      return this.generateMockExplanation(code);
    }

    const prompt = `Explain this Max for Live JavaScript code in simple terms:\n\n${code}`;
    
    try {
      const response = await this.callAIProvider(
        'You are a Max for Live expert. Explain code clearly and concisely.',
        prompt
      );
      return response;
    } catch (error) {
      return this.generateMockExplanation(code);
    }
  }

  // ==========================================
  // Private Methods
  // ==========================================

  validateMaxJSPatterns(code) {
    const issues = [];

    // Check for inlet/outlet declarations
    if (!code.includes('inlets') || !code.includes('outlets')) {
      issues.push({
        type: 'missing-inlets-outlets',
        message: 'Missing inlet/outlet declarations. Add: inlets = N; outlets = M;',
        line: 1,
        severity: 'warning',
        fix: 'Add inlet and outlet declarations at the top of the file'
      });
    }

    // Check for return statements (should use outlet)
    if (code.includes('return ') && !code.includes('// return ok')) {
      issues.push({
        type: 'return-instead-of-outlet',
        message: 'Use outlet() instead of return in Max JS',
        severity: 'warning',
        fix: 'Replace return statements with outlet(index, value)'
      });
    }

    // Check for console.log (should use post)
    if (code.includes('console.log')) {
      issues.push({
        type: 'console-log',
        message: 'Use post() instead of console.log() in Max JS',
        severity: 'info',
        fix: 'Replace console.log with post()'
      });
    }

    // Check for missing inlet handlers
    if (code.includes('inlets') && !code.includes('function bang()') && !code.includes('function msg_')) {
      issues.push({
        type: 'no-inlet-handlers',
        message: 'No inlet handler functions defined (bang, msg_int, msg_float, etc.)',
        severity: 'warning',
        fix: 'Add inlet handler functions like bang() or msg_int()'
      });
    }

    return issues;
  }

  analyzePerformance(code) {
    const issues = [];

    // Check for loops in potentially high-frequency functions
    if (code.includes('function bang()') && code.includes('for (')) {
      issues.push({
        type: 'performance',
        message: 'Loop in bang() function may cause performance issues',
        severity: 'info',
        fix: 'Consider optimizing loops or moving to lower-frequency function'
      });
    }

    // Check for array operations that could be optimized
    if (code.includes('.map(') || code.includes('.filter(')) {
      issues.push({
        type: 'performance',
        message: 'Functional array operations may impact real-time performance',
        severity: 'info',
        fix: 'Consider using traditional for loops for better performance'
      });
    }

    return issues;
  }

  getMaxFunctionSuggestions() {
    return [
      {
        label: 'bang()',
        kind: 'function',
        insertText: 'bang() {\n  outlet(0, 1);\n}',
        documentation: 'Handler for bang messages on inlet 0'
      },
      {
        label: 'msg_int(v)',
        kind: 'function',
        insertText: 'msg_int(v) {\n  outlet(0, v);\n}',
        documentation: 'Handler for integer messages on inlet 0'
      },
      {
        label: 'msg_float(v)',
        kind: 'function',
        insertText: 'msg_float(v) {\n  outlet(0, v);\n}',
        documentation: 'Handler for float messages on inlet 0'
      },
      {
        label: 'list()',
        kind: 'function',
        insertText: 'list() {\n  var args = arrayfromargs(arguments);\n  outlet(0, args);\n}',
        documentation: 'Handler for list messages'
      }
    ];
  }

  getOutletSuggestions(connectedObjects) {
    const suggestions = [
      {
        label: 'outlet(0, value)',
        kind: 'function',
        insertText: 'outlet(0, ${1:value})',
        documentation: 'Send value to outlet 0'
      }
    ];

    if (connectedObjects && connectedObjects.length > 1) {
      for (let i = 1; i < connectedObjects.length; i++) {
        suggestions.push({
          label: `outlet(${i}, value)`,
          kind: 'function',
          insertText: `outlet(${i}, \${1:value})`,
          documentation: `Send value to outlet ${i}`
        });
      }
    }

    return suggestions;
  }

  getInletHandlerSuggestions() {
    return [
      {
        label: 'inlets = 1',
        kind: 'variable',
        insertText: 'inlets = ${1:1};',
        documentation: 'Number of inlets for this object'
      },
      {
        label: 'outlets = 1',
        kind: 'variable',
        insertText: 'outlets = ${1:1};',
        documentation: 'Number of outlets for this object'
      }
    ];
  }

  generateMockCode(prompt, context) {
    const { arrangerConnection } = context;
    
    // Generate contextual mock code based on prompt keywords
    if (prompt.toLowerCase().includes('arpeggiator') || prompt.toLowerCase().includes('chord')) {
      return {
        code: this.getMockArpeggiatorCode(arrangerConnection),
        explanation: 'A MIDI arpeggiator that plays chord notes in sequence. Bang to advance to next note.',
        parameters: ['pattern', 'octaves', 'tempo'],
        usage: 'Connect MIDI out to an instrument. Bang to trigger notes.'
      };
    }
    
    if (prompt.toLowerCase().includes('random') || prompt.toLowerCase().includes('probability')) {
      return {
        code: this.getMockRandomizerCode(),
        explanation: 'A probability-based MIDI note randomizer with scale constraints.',
        parameters: ['probability', 'scale', 'range'],
        usage: 'Send MIDI notes through. Some notes pass, some are randomized.'
      };
    }

    // Default mock code
    return {
      code: `// Generated Max JS code
inlets = 1;
outlets = 1;

function bang() {
  // Your code here
  outlet(0, 1);
}

function msg_int(v) {
  outlet(0, v);
}`,
      explanation: 'Basic Max JS template with inlet handlers',
      parameters: [],
      usage: 'Send bang or integers to trigger output'
    };
  }

  getMockArpeggiatorCode(useArranger) {
    if (useArranger) {
      return `// MIDI Arpeggiator with Arranger Integration
// Auto-generated from Arranger System

inlets = 2;  // [0] bang to trigger, [1] chord data from arranger
outlets = 1; // MIDI note output

var currentChord = [60, 64, 67]; // Default C major
var currentNote = 0;
var pattern = [0, 1, 2, 1]; // Up-down pattern

function bang() {
  var noteIndex = pattern[currentNote % pattern.length];
  var midiNote = currentChord[noteIndex % currentChord.length];
  
  outlet(0, midiNote);
  
  currentNote++;
  if (currentNote >= pattern.length * 2) {
    currentNote = 0;
  }
}

function list() {
  // Receive chord notes from arranger
  currentChord = arrayfromargs(arguments);
  currentNote = 0;
  post("Updated chord: " + currentChord + "\\n");
}

function setPattern(p) {
  pattern = arrayfromargs(arguments);
  post("Updated pattern: " + pattern + "\\n");
}`;
    }

    return `// Simple MIDI Arpeggiator
inlets = 1;
outlets = 1;

var chord = [60, 64, 67]; // C major
var currentNote = 0;

function bang() {
  var note = chord[currentNote % chord.length];
  outlet(0, note);
  currentNote++;
}`;
  }

  getMockRandomizerCode() {
    return `// MIDI Note Randomizer
inlets = 2;  // [0] MIDI note, [1] probability (0-100)
outlets = 1;

var probability = 50;
var scale = [0, 2, 4, 5, 7, 9, 11]; // Major scale
var rootNote = 60; // C4

function msg_int(note) {
  if (Math.random() * 100 < probability) {
    // Randomize note within scale
    var scaleIndex = Math.floor(Math.random() * scale.length);
    var octave = Math.floor(note / 12) * 12;
    var randomNote = octave + scale[scaleIndex];
    outlet(0, randomNote);
  } else {
    // Pass through original
    outlet(0, note);
  }
}

function msg_float(prob) {
  probability = Math.max(0, Math.min(100, prob));
  post("Probability: " + probability + "%\\n");
}`;
  }

  generateMockExplanation(code) {
    const lines = code.split('\n').length;
    const hasInlets = code.includes('inlets');
    const hasOutlets = code.includes('outlets');
    const hasBang = code.includes('function bang');

    return `This Max JavaScript code has ${lines} lines. ${
      hasInlets && hasOutlets ? 'It declares inlets and outlets for Max patching. ' : ''
    }${
      hasBang ? 'It responds to bang messages. ' : ''
    }The code processes data and sends output through outlets.`;
  }

  getCursorLine(code, cursor) {
    const lines = code.substring(0, cursor).split('\n');
    return lines.length - 1;
  }

  extractLineNumber(error) {
    // Try to extract line number from error message
    const match = error.message.match(/line (\d+)/i);
    return match ? parseInt(match[1]) : 1;
  }

  extractCode(response) {
    // Extract code from AI response (usually in code blocks)
    const codeMatch = response.match(/```(?:javascript|js)?\n([\s\S]+?)\n```/);
    return codeMatch ? codeMatch[1].trim() : response.trim();
  }

  extractExplanation(response) {
    // Extract explanation text (everything outside code blocks)
    return response.replace(/```(?:javascript|js)?\n[\s\S]+?\n```/g, '').trim();
  }

  extractParameters(response) {
    // Extract parameter mentions
    const params = [];
    const paramMatches = response.matchAll(/parameter[s]?:?\s*([^\n]+)/gi);
    for (const match of paramMatches) {
      params.push(match[1].trim());
    }
    return params;
  }

  extractUsage(response) {
    const usageMatch = response.match(/usage:?\s*([^\n]+)/i);
    return usageMatch ? usageMatch[1].trim() : 'Send messages to inlets to trigger output';
  }

  async callAIProvider(systemPrompt, userPrompt) {
    // Placeholder for actual AI provider calls
    // In production, implement actual API calls to OpenAI, Anthropic, etc.
    throw new Error('AI provider not configured. Using mock mode.');
  }

  async getAISuggestions(context) {
    // Placeholder for AI-powered suggestions
    return [];
  }

  async analyzeSemantics(code, context) {
    // Placeholder for AI semantic analysis
    return [];
  }

  async generateAIFix(error, code) {
    // Placeholder for AI fix generation
    return null;
  }

  /**
   * Chat interface for conversational AI assistance
   */
  async chat({ messages, context, mode = 'general' }) {
    const lastMessage = messages[messages.length - 1]?.content?.toLowerCase() || '';
    
    // M4L-specific responses
    const m4lResponses = {
      'midi': {
        message: "For MIDI processing in M4L, you'll want to use these objects:\n\n• **notein** - Receives MIDI notes\n• **noteout** - Sends MIDI notes\n• **makenote** - Creates note on/off pairs\n• **midiparse** - Parses raw MIDI\n\nWould you like me to show you a complete MIDI effect example?",
        suggestions: [
          { text: 'Show MIDI effect example', action: 'example', type: 'midi-effect' },
          { text: 'Create notein object', action: 'create', object: { type: 'notein' } }
        ]
      },
      'live api': {
        message: "The Live API lets you control Live from Max. Here's the basic approach:\n\n1. Use **live.path** to navigate to objects\n2. Use **live.object** to get/set properties\n3. Use **live.observer** to monitor changes\n\nExample path: `live_set tracks 0 devices 0`\n\nWhat would you like to control?",
        suggestions: [
          { text: 'Show Live API example', action: 'example', type: 'live-api' },
          { text: 'Create live.path', action: 'create', object: { type: 'live.path' } }
        ]
      },
      'javascript': {
        message: "JavaScript in Max is powerful! The **js** object runs JavaScript code with:\n\n• Full Max messaging system\n• Inlets and outlets for data flow\n• Access to Max objects via JSAdapter\n\nWould you like me to generate a JavaScript template for you?",
        codeBlocks: [
          {
            language: 'javascript',
            code: `inlets = 1;
outlets = 1;

function msg_int(v) {
    // Process numbers
    outlet(0, v * 2);
}

function bang() {
    post("Hello from JS!\\n");
}`
          }
        ],
        suggestions: [
          { text: 'Generate custom JS code', action: 'generate' }
        ]
      },
      'audio': {
        message: "For audio processing in M4L:\n\n• **plugin~** - Audio in/out from Live\n• **live.gain~** - Volume control with meter\n• **biquad~** - Flexible filter\n• **pfft~** - FFT processing\n\nAudio objects end with **~**. What kind of audio effect are you building?",
        suggestions: [
          { text: 'Show audio effect example', action: 'example', type: 'audio-effect' }
        ]
      },
      'arpeggiator': {
        message: "I can help you create an arpeggiator! Here's a simple example:",
        codeBlocks: [
          {
            language: 'javascript',
            code: `inlets = 2;  // [0] notes, [1] bang to advance
outlets = 1;

var notes = [];
var currentIndex = 0;

function list() {
    if (inlet === 0) {
        var pitch = arguments[0];
        var velocity = arguments[1];
        
        if (velocity > 0) {
            // Add note
            if (notes.indexOf(pitch) === -1) {
                notes.push(pitch);
                notes.sort(function(a,b) { return a-b; });
            }
        } else {
            // Remove note
            var idx = notes.indexOf(pitch);
            if (idx !== -1) notes.splice(idx, 1);
        }
    }
}

function bang() {
    if (inlet === 1 && notes.length > 0) {
        outlet(0, [notes[currentIndex], 100]);
        currentIndex = (currentIndex + 1) % notes.length;
    }
}`
          }
        ],
        suggestions: [
          { text: 'Add rhythm patterns', action: 'enhance' },
          { text: 'Add direction control', action: 'enhance' }
        ]
      },
      'help': {
        message: "I can help you with Max for Live development! Here are some things I can do:\n\n• **Explain M4L concepts** - Ask about objects, patching, etc.\n• **Generate JavaScript code** - Describe what you want to create\n• **Debug patches** - Help troubleshoot issues\n• **Show examples** - Get code for common patterns\n• **Suggest objects** - Find the right tool for your needs\n\nTry asking something like:\n- 'How do I receive MIDI notes?'\n- 'Create an arpeggiator'\n- 'How do I control Live parameters?'\n- 'Show me a filter example'",
        suggestions: [
          { text: 'Create MIDI effect', action: 'tutorial' },
          { text: 'Use Live API', action: 'tutorial' },
          { text: 'Write JavaScript', action: 'tutorial' }
        ]
      }
    };

    // Find matching response
    for (const [key, response] of Object.entries(m4lResponses)) {
      if (lastMessage.includes(key)) {
        return response;
      }
    }

    // Default helpful response
    return m4lResponses.help;
  }
}

// Singleton instance
let aiServiceInstance = null;

export const getAIService = (config) => {
  if (!aiServiceInstance) {
    aiServiceInstance = new AIService(config);
  }
  return aiServiceInstance;
};

export const configureAIService = (config) => {
  aiServiceInstance = new AIService(config);
  return aiServiceInstance;
};

export default AIService;
