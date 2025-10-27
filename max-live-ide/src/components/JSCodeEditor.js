/**
 * AI-Enhanced JavaScript Code Editor
 * Monaco editor with AI assistance, Max JS validation, and arranger integration
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import Editor from '@monaco-editor/react';
import {
  Paper,
  Stack,
  Group,
  Button,
  Text,
  Badge,
  Tabs,
  Alert,
  Textarea,
  ActionIcon,
  Tooltip,
  Modal,
  Loader
} from '@mantine/core';
import {
  IconSparkles,
  IconCheck,
  IconAlertCircle,
  IconInfoCircle,
  IconWand,
  IconCode,
  IconBrain,
  IconMusic
} from '@tabler/icons-react';
import { getAIService } from '../services/aiService';
import { getArrangerOSC } from '../utils/ArrangerOSC';
import './JSCodeEditor.css';

const JSCodeEditor = ({ node, onCodeChange, onClose }) => {
  const [code, setCode] = useState(node.data.jsCode || '');
  const [errors, setErrors] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [aiPanelOpen, setAIPanelOpen] = useState(false);
  const [nlPrompt, setNLPrompt] = useState('');
  const [generating, setGenerating] = useState(false);
  const [activeTab, setActiveTab] = useState('code');
  const [explanation, setExplanation] = useState('');
  
  const editorRef = useRef(null);
  const aiService = useRef(getAIService({ provider: 'mock' }));
  const arrangerOSC = useRef(getArrangerOSC());

  // Initialize editor
  useEffect(() => {
    if (!code) {
      setCode(getDefaultTemplate(node.data.label));
    }
  }, []);

  // Auto-validate code on change
  useEffect(() => {
    const validateDebounced = setTimeout(() => {
      validateCode();
    }, 500);

    return () => clearTimeout(validateDebounced);
  }, [code]);

  const validateCode = async () => {
    const analysisErrors = await aiService.current.analyzeCode(code, {
      objectType: node.data.label,
      connectedObjects: node.data.connectedObjects || []
    });
    setErrors(analysisErrors);
  };

  const handleEditorMount = (editor, monaco) => {
    editorRef.current = editor;

    // Register Max JS language features
    monaco.languages.registerCompletionItemProvider('javascript', {
      provideCompletionItems: (model, position) => {
        return {
          suggestions: getMaxJSCompletions(monaco)
        };
      }
    });

    // Add error markers
    updateErrorMarkers(monaco);
  };

  const handleCodeChange = (newCode) => {
    setCode(newCode);
    onCodeChange(node.id, newCode);
  };

  const updateErrorMarkers = (monaco) => {
    if (!editorRef.current || !monaco) return;

    const model = editorRef.current.getModel();
    const markers = errors.map(error => ({
      severity: error.severity === 'error' 
        ? monaco.MarkerSeverity.Error 
        : error.severity === 'warning'
        ? monaco.MarkerSeverity.Warning
        : monaco.MarkerSeverity.Info,
      message: error.message,
      startLineNumber: error.line || 1,
      startColumn: 1,
      endLineNumber: error.line || 1,
      endColumn: 1000
    }));

    monaco.editor.setModelMarkers(model, 'maxjs', markers);
  };

  const handleNLGenerate = async () => {
    if (!nlPrompt.trim()) return;

    setGenerating(true);
    try {
      const result = await aiService.current.generateFromNaturalLanguage({
        prompt: nlPrompt,
        maxObjectType: node.data.label,
        arrangerConnection: arrangerOSC.current.connected,
        existingPatch: true
      });

      setCode(result.code);
      setExplanation(result.explanation);
      handleCodeChange(result.code);
      setNLPrompt('');
      setActiveTab('code');
    } catch (error) {
      console.error('Generation failed:', error);
    } finally {
      setGenerating(false);
    }
  };

  const handleExplainCode = async () => {
    setGenerating(true);
    try {
      const explanationText = await aiService.current.explainCode(code);
      setExplanation(explanationText);
      setActiveTab('info');
    } catch (error) {
      console.error('Explanation failed:', error);
    } finally {
      setGenerating(false);
    }
  };

  const handleApplyFix = async (fix) => {
    if (fix && fix.fix && fix.fix.code) {
      setCode(fix.fix.code);
      handleCodeChange(fix.fix.code);
    }
  };

  const handleQuickTemplate = async (templateType) => {
    let templateCode = '';
    
    switch (templateType) {
      case 'arpeggiator':
        const chords = await arrangerOSC.current.getChordSuggestions('Cmaj7', 'pop');
        templateCode = generateArpeggiatorTemplate(chords);
        break;
      case 'randomizer':
        const scales = await arrangerOSC.current.getScales('C');
        templateCode = generateRandomizerTemplate(scales[0]);
        break;
      case 'basic':
      default:
        templateCode = getDefaultTemplate('js');
    }

    setCode(templateCode);
    handleCodeChange(templateCode);
  };

  return (
    <Modal
      opened={true}
      onClose={onClose}
      title={
        <Group gap="sm">
          <IconCode size={20} />
          <Text fw={600}>{node.data.label} Editor</Text>
          {arrangerOSC.current.connected && (
            <Badge size="sm" color="teal" leftSection={<IconMusic size={12} />}>
              Arranger Connected
            </Badge>
          )}
        </Group>
      }
      size="xl"
      styles={{
        modal: { height: '80vh' },
        body: { height: 'calc(80vh - 60px)', display: 'flex', flexDirection: 'column' }
      }}
    >
      <Stack style={{ flex: 1, overflow: 'hidden' }}>
        {/* Toolbar */}
        <Group justify="space-between">
          <Group gap="xs">
            <Button
              size="xs"
              variant="light"
              leftSection={<IconSparkles size={14} />}
              onClick={() => setAIPanelOpen(!aiPanelOpen)}
            >
              AI Assistant
            </Button>
            <Button
              size="xs"
              variant="light"
              leftSection={<IconBrain size={14} />}
              onClick={handleExplainCode}
              loading={generating}
            >
              Explain Code
            </Button>
          </Group>
          
          <Group gap="xs">
            <Tooltip label="Basic Template">
              <ActionIcon variant="subtle" onClick={() => handleQuickTemplate('basic')}>
                <IconCode size={16} />
              </ActionIcon>
            </Tooltip>
            <Tooltip label="Arpeggiator">
              <ActionIcon variant="subtle" onClick={() => handleQuickTemplate('arpeggiator')}>
                <IconMusic size={16} />
              </ActionIcon>
            </Tooltip>
            <Tooltip label="Randomizer">
              <ActionIcon variant="subtle" onClick={() => handleQuickTemplate('randomizer')}>
                <IconWand size={16} />
              </ActionIcon>
            </Tooltip>
          </Group>
        </Group>

        {/* AI Natural Language Panel */}
        {aiPanelOpen && (
          <Paper p="md" withBorder>
            <Stack gap="sm">
              <Text size="sm" fw={600}>
                <IconSparkles size={16} style={{ marginRight: 4 }} />
                Generate Code from Description
              </Text>
              <Textarea
                placeholder="Describe what you want to create... (e.g., 'Create a MIDI arpeggiator that plays chords in sequence')"
                value={nlPrompt}
                onChange={(e) => setNLPrompt(e.target.value)}
                minRows={2}
              />
              <Group gap="xs">
                <Button
                  size="xs"
                  onClick={handleNLGenerate}
                  loading={generating}
                  leftSection={<IconWand size={14} />}
                >
                  Generate
                </Button>
                {EXAMPLE_PROMPTS.map(prompt => (
                  <Button
                    key={prompt}
                    size="xs"
                    variant="subtle"
                    onClick={() => setNLPrompt(prompt)}
                  >
                    {prompt}
                  </Button>
                ))}
              </Group>
            </Stack>
          </Paper>
        )}

        {/* Error Display */}
        {errors.length > 0 && (
          <Stack gap="xs">
            {errors.slice(0, 3).map((error, idx) => (
              <Alert
                key={idx}
                icon={error.severity === 'error' ? <IconAlertCircle /> : <IconInfoCircle />}
                color={error.severity === 'error' ? 'red' : error.severity === 'warning' ? 'yellow' : 'blue'}
                variant="light"
                withCloseButton
              >
                <Group justify="space-between">
                  <Text size="sm">{error.message}</Text>
                  {error.fix && (
                    <Button size="xs" variant="light" onClick={() => handleApplyFix({ fix: error })}>
                      Fix
                    </Button>
                  )}
                </Group>
              </Alert>
            ))}
          </Stack>
        )}

        {/* Editor Tabs */}
        <Tabs value={activeTab} onChange={setActiveTab} style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          <Tabs.List>
            <Tabs.Tab value="code" leftSection={<IconCode size={14} />}>
              Code
            </Tabs.Tab>
            <Tabs.Tab value="info" leftSection={<IconInfoCircle size={14} />}>
              Info
            </Tabs.Tab>
          </Tabs.List>

          <Tabs.Panel value="code" style={{ flex: 1, marginTop: 12 }}>
            <Editor
              height="100%"
              defaultLanguage="javascript"
              value={code}
              onChange={handleCodeChange}
              onMount={handleEditorMount}
              theme="vs-dark"
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                lineNumbers: 'on',
                autoClosingBrackets: 'always',
                autoClosingQuotes: 'always',
                formatOnPaste: true,
                formatOnType: true,
                tabSize: 2,
                wordWrap: 'on',
                suggest: {
                  showWords: true,
                  showMethods: true,
                  showFunctions: true
                }
              }}
            />
          </Tabs.Panel>

          <Tabs.Panel value="info" pt="md">
            <Paper p="md" withBorder>
              <Stack gap="md">
                <div>
                  <Text size="sm" fw={600} mb="xs">Object Type</Text>
                  <Badge>{node.data.label}</Badge>
                </div>
                
                <div>
                  <Text size="sm" fw={600} mb="xs">Status</Text>
                  <Group gap="xs">
                    <Badge color={errors.length === 0 ? 'green' : 'red'}>
                      {errors.length === 0 ? 'No Errors' : `${errors.length} Issues`}
                    </Badge>
                    {code.includes('inlets') && <Badge color="blue">Has Inlets</Badge>}
                    {code.includes('outlets') && <Badge color="blue">Has Outlets</Badge>}
                  </Group>
                </div>

                {explanation && (
                  <div>
                    <Text size="sm" fw={600} mb="xs">AI Explanation</Text>
                    <Text size="sm" c="dimmed">{explanation}</Text>
                  </div>
                )}

                <div>
                  <Text size="sm" fw={600} mb="xs">Quick Reference</Text>
                  <Stack gap="xs">
                    <Text size="xs" c="dimmed">• Use <code>inlets = N</code> and <code>outlets = N</code></Text>
                    <Text size="xs" c="dimmed">• Send data with <code>outlet(index, value)</code></Text>
                    <Text size="xs" c="dimmed">• Handle input with <code>bang()</code>, <code>msg_int(v)</code>, etc.</Text>
                    <Text size="xs" c="dimmed">• Debug with <code>post("message")</code></Text>
                  </Stack>
                </div>
              </Stack>
            </Paper>
          </Tabs.Panel>
        </Tabs>

        {/* Footer Actions */}
        <Group justify="flex-end">
          <Button variant="subtle" onClick={onClose}>
            Close
          </Button>
          <Button
            leftSection={<IconCheck size={16} />}
            onClick={() => {
              handleCodeChange(code);
              onClose();
            }}
          >
            Apply & Close
          </Button>
        </Group>
      </Stack>
    </Modal>
  );
};

// Helper Functions

const getDefaultTemplate = (objectType) => {
  return `// Max for Live JavaScript (${objectType})
inlets = 1;
outlets = 1;

// Handle bang messages
function bang() {
  outlet(0, 1);
}

// Handle integer messages
function msg_int(v) {
  outlet(0, v);
}

// Handle float messages
function msg_float(v) {
  outlet(0, v);
}`;
};

const generateArpeggiatorTemplate = (chords) => {
  const chordData = chords.map(c => ({ symbol: c.symbol, notes: c.notes }));
  
  return `// MIDI Arpeggiator - AI Generated with Arranger Integration
inlets = 2;  // [0] bang to trigger, [1] chord index
outlets = 1; // MIDI note output

var chords = ${JSON.stringify(chordData)};
var currentChord = 0;
var currentNote = 0;
var pattern = [0, 1, 2, 1]; // Up-down arpeggio pattern

function bang() {
  if (chords.length === 0) return;
  
  var chord = chords[currentChord];
  var noteIndex = pattern[currentNote % pattern.length];
  var midiNote = chord.notes[noteIndex % chord.notes.length];
  
  outlet(0, midiNote);
  
  currentNote++;
  if (currentNote >= pattern.length * 2) {
    currentNote = 0;
  }
}

function msg_int(chordIndex) {
  currentChord = Math.max(0, Math.min(chordIndex, chords.length - 1));
  currentNote = 0;
  post("Switched to chord: " + chords[currentChord].symbol + "\\n");
}`;
};

const generateRandomizerTemplate = (scale) => {
  return `// Scale-Aware MIDI Randomizer - AI Generated
inlets = 2;  // [0] MIDI note in, [1] probability (0-100)
outlets = 1; // MIDI note out

var probability = 50;
var scale = ${JSON.stringify(scale.notes)};

function msg_int(note) {
  if (Math.random() * 100 < probability) {
    // Randomize to scale note
    var scaleNote = scale[Math.floor(Math.random() * scale.length)];
    var octave = Math.floor(note / 12);
    var randomNote = (octave * 12) + (scaleNote % 12);
    outlet(0, randomNote);
  } else {
    // Pass through
    outlet(0, note);
  }
}

function msg_float(prob) {
  probability = Math.max(0, Math.min(100, prob));
  post("Probability: " + probability + "%\\n");
}`;
};

const getMaxJSCompletions = (monaco) => {
  return [
    {
      label: 'inlets',
      kind: monaco.languages.CompletionItemKind.Variable,
      insertText: 'inlets = ${1:1};',
      insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
      documentation: 'Number of inlets for this object'
    },
    {
      label: 'outlets',
      kind: monaco.languages.CompletionItemKind.Variable,
      insertText: 'outlets = ${1:1};',
      insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
      documentation: 'Number of outlets for this object'
    },
    {
      label: 'bang',
      kind: monaco.languages.CompletionItemKind.Function,
      insertText: 'function bang() {\n\t${1:outlet(0, 1);}\n}',
      insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
      documentation: 'Handle bang messages'
    },
    {
      label: 'msg_int',
      kind: monaco.languages.CompletionItemKind.Function,
      insertText: 'function msg_int(v) {\n\t${1:outlet(0, v);}\n}',
      insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
      documentation: 'Handle integer messages'
    },
    {
      label: 'outlet',
      kind: monaco.languages.CompletionItemKind.Function,
      insertText: 'outlet(${1:0}, ${2:value});',
      insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
      documentation: 'Send value to outlet'
    },
    {
      label: 'post',
      kind: monaco.languages.CompletionItemKind.Function,
      insertText: 'post(${1:"message"});',
      insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
      documentation: 'Print message to Max console'
    }
  ];
};

const EXAMPLE_PROMPTS = [
  'MIDI arpeggiator',
  'Note randomizer',
  'Chord player',
  'Euclidean rhythm'
];

export default JSCodeEditor;
