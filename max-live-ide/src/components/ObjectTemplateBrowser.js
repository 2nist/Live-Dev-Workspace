/**
 * Object & Template Search Browser
 * Unified search interface for Max objects, Live API objects, and templates
 */

import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import { 
  Paper, 
  TextInput, 
  Button, 
  Group, 
  Stack, 
  Badge, 
  Text, 
  ActionIcon, 
  ScrollArea,
  Divider,
  Kbd,
  CloseButton,
  SimpleGrid,
  ThemeIcon,
  Tabs,
  Tooltip,
  Modal,
  Code,
  Spoiler,
  Anchor,
  Select,
  MultiSelect
} from '@mantine/core';
import { 
  IconSearch, 
  IconFilter, 
  IconTag, 
  IconChevronRight,
  IconMusic,
  IconWaveSquare,
  IconSettings,
  IconDevices,
  IconTemplate,
  IconBolt,
  IconEye,
  IconDownload,
  IconStar,
  IconCopy,
  IconPin,
  IconHeart,
  IconBook,
  IconCode,
  IconZap,
  IconTarget,
  IconBulb
} from '@tabler/icons-react';
import { QUICK_START_TEMPLATES } from './QuickStartTemplates';
import './ObjectTemplateBrowser.css';

// Max Objects Database
const MAX_OBJECTS_DATABASE = {
  // Audio Objects
  audio: [
    {
      name: 'osc~',
      category: 'audio',
      type: 'generator',
      description: 'Oscillator with multiple waveforms',
      inlets: 2,
      outlets: 1,
      tags: ['oscillator', 'generator', 'waveform', 'audio'],
      difficulty: 'beginner',
      usage: 'osc~ [frequency] [phase]',
      example: 'osc~ 440',
      parameters: ['frequency', 'phase', 'waveform'],
      relatedObjects: ['cycle~', 'saw~', 'rect~']
    },
    {
      name: 'cycle~',
      category: 'audio',
      type: 'generator',
      description: 'Sine wave oscillator',
      inlets: 2,
      outlets: 1,
      tags: ['sine', 'oscillator', 'generator', 'audio'],
      difficulty: 'beginner',
      usage: 'cycle~ [frequency]',
      example: 'cycle~ 440',
      parameters: ['frequency', 'phase'],
      relatedObjects: ['osc~', 'phasor~']
    },
    {
      name: 'saw~',
      category: 'audio',
      type: 'generator',
      description: 'Sawtooth wave oscillator',
      inlets: 2,
      outlets: 1,
      tags: ['sawtooth', 'oscillator', 'generator', 'audio'],
      difficulty: 'beginner',
      usage: 'saw~ [frequency]',
      example: 'saw~ 110',
      parameters: ['frequency', 'phase'],
      relatedObjects: ['osc~', 'rect~', 'tri~']
    },
    {
      name: 'rect~',
      category: 'audio',
      type: 'generator',
      description: 'Rectangle wave oscillator',
      inlets: 3,
      outlets: 1,
      tags: ['rectangle', 'square', 'oscillator', 'generator', 'audio'],
      difficulty: 'beginner',
      usage: 'rect~ [frequency] [pulsewidth]',
      example: 'rect~ 220 0.5',
      parameters: ['frequency', 'pulsewidth', 'phase'],
      relatedObjects: ['osc~', 'saw~']
    },
    {
      name: 'noise~',
      category: 'audio',
      type: 'generator',
      description: 'White noise generator',
      inlets: 0,
      outlets: 1,
      tags: ['noise', 'generator', 'random', 'audio'],
      difficulty: 'beginner',
      usage: 'noise~',
      example: 'noise~',
      parameters: [],
      relatedObjects: ['rand~', 'pink~']
    },
    {
      name: 'biquad~',
      category: 'audio',
      type: 'filter',
      description: 'Biquadratic filter with multiple modes',
      inlets: 6,
      outlets: 1,
      tags: ['filter', 'biquad', 'lowpass', 'highpass', 'bandpass', 'effect'],
      difficulty: 'intermediate',
      usage: 'biquad~ [a0] [a1] [a2] [b1] [b2]',
      example: 'biquad~ 1. 0. 0. 0. 0.',
      parameters: ['coefficients', 'frequency', 'resonance'],
      relatedObjects: ['filtergraph~', 'reson~', 'lores~']
    },
    {
      name: 'delay~',
      category: 'audio',
      type: 'effect',
      description: 'Variable delay line',
      inlets: 2,
      outlets: 1,
      tags: ['delay', 'time', 'effect', 'audio'],
      difficulty: 'intermediate',
      usage: 'delay~ [buffer_name] [delay_time]',
      example: 'delay~ delayBuffer 1000',
      parameters: ['delay_time', 'feedback'],
      relatedObjects: ['tapin~', 'tapout~', 'comb~']
    },
    {
      name: 'gain~',
      category: 'audio',
      type: 'modifier',
      description: 'Audio level control with smoothing',
      inlets: 2,
      outlets: 1,
      tags: ['gain', 'volume', 'level', 'modifier'],
      difficulty: 'beginner',
      usage: 'gain~ [initial_gain]',
      example: 'gain~ 0.5',
      parameters: ['gain_level', 'smoothing_time'],
      relatedObjects: ['*~', 'live.gain~']
    },
    {
      name: 'dac~',
      category: 'audio',
      type: 'output',
      description: 'Digital-to-analog converter (audio output)',
      inlets: 2,
      outlets: 0,
      tags: ['output', 'dac', 'audio'],
      difficulty: 'beginner',
      usage: 'dac~ [channel1] [channel2]',
      example: 'dac~ 1 2',
      parameters: ['output_channels'],
      relatedObjects: ['ezdac~', 'adc~']
    },
    {
      name: 'ezdac~',
      category: 'audio',
      type: 'output',
      description: 'Easy audio output with start/stop button',
      inlets: 2,
      outlets: 0,
      tags: ['output', 'dac', 'audio', 'easy'],
      difficulty: 'beginner',
      usage: 'ezdac~',
      example: 'ezdac~',
      parameters: [],
      relatedObjects: ['dac~', 'adc~']
    }
  ],
  
  // MIDI Objects
  midi: [
    {
      name: 'notein',
      category: 'midi',
      type: 'input',
      description: 'Receives MIDI note messages',
      inlets: 0,
      outlets: 3,
      tags: ['midi', 'input', 'notes', 'velocity', 'channel'],
      difficulty: 'beginner',
      usage: 'notein [channel]',
      example: 'notein 1',
      parameters: ['channel'],
      relatedObjects: ['noteout', 'makenote', 'stripnote']
    },
    {
      name: 'noteout',
      category: 'midi',
      type: 'output',
      description: 'Sends MIDI note messages',
      inlets: 3,
      outlets: 0,
      tags: ['midi', 'output', 'notes', 'velocity', 'channel'],
      difficulty: 'beginner',
      usage: 'noteout [channel]',
      example: 'noteout 1',
      parameters: ['channel'],
      relatedObjects: ['notein', 'makenote', 'stripnote']
    },
    {
      name: 'ctlin',
      category: 'midi',
      type: 'input',
      description: 'Receives MIDI control change messages',
      inlets: 0,
      outlets: 3,
      tags: ['midi', 'input', 'control', 'cc', 'channel'],
      difficulty: 'beginner',
      usage: 'ctlin [controller] [channel]',
      example: 'ctlin 1 1',
      parameters: ['controller_number', 'channel'],
      relatedObjects: ['ctlout', 'midiin', 'midiparse']
    },
    {
      name: 'ctlout',
      category: 'midi',
      type: 'output',
      description: 'Sends MIDI control change messages',
      inlets: 3,
      outlets: 0,
      tags: ['midi', 'output', 'control', 'cc', 'channel'],
      difficulty: 'beginner',
      usage: 'ctlout [channel]',
      example: 'ctlout 1',
      parameters: ['channel'],
      relatedObjects: ['ctlin', 'midiout', 'midiformat']
    },
    {
      name: 'makenote',
      category: 'midi',
      type: 'utility',
      description: 'Creates note-on/note-off pairs with duration',
      inlets: 3,
      outlets: 2,
      tags: ['midi', 'notes', 'duration', 'utility'],
      difficulty: 'beginner',
      usage: 'makenote [velocity] [duration]',
      example: 'makenote 64 500',
      parameters: ['velocity', 'duration'],
      relatedObjects: ['noteout', 'stripnote', 'flush']
    },
    {
      name: 'stripnote',
      category: 'midi',
      type: 'utility',
      description: 'Removes note-off messages',
      inlets: 2,
      outlets: 2,
      tags: ['midi', 'notes', 'filter', 'utility'],
      difficulty: 'beginner',
      usage: 'stripnote',
      example: 'stripnote',
      parameters: [],
      relatedObjects: ['makenote', 'noteout', 'flush']
    }
  ],

  // Live API Objects
  live: [
    {
      name: 'live.dial',
      category: 'live',
      type: 'ui',
      description: 'Rotary control that maps to Live parameters',
      inlets: 1,
      outlets: 1,
      tags: ['live', 'ui', 'control', 'parameter', 'dial'],
      difficulty: 'beginner',
      usage: 'live.dial @parameter_enable 1',
      example: 'live.dial @min 0 @max 127 @parameter_enable 1',
      parameters: ['min', 'max', 'parameter_enable', 'varname'],
      relatedObjects: ['live.slider', 'live.numbox', 'live.button']
    },
    {
      name: 'live.gain~',
      category: 'live',
      type: 'audio',
      description: 'Audio gain control with Live parameter mapping',
      inlets: 2,
      outlets: 1,
      tags: ['live', 'audio', 'gain', 'parameter', 'volume'],
      difficulty: 'beginner',
      usage: 'live.gain~ @parameter_enable 1',
      example: 'live.gain~ @parameter_enable 1',
      parameters: ['parameter_enable', 'varname'],
      relatedObjects: ['gain~', 'live.dial', '*~']
    },
    {
      name: 'live.object',
      category: 'live',
      type: 'api',
      description: 'Access to Live Object Model (LOM)',
      inlets: 1,
      outlets: 2,
      tags: ['live', 'api', 'lom', 'control', 'automation'],
      difficulty: 'advanced',
      usage: 'live.object [path]',
      example: 'live.object live_set',
      parameters: ['path', 'property'],
      relatedObjects: ['live.observer', 'live.path', 'live.remote~']
    },
    {
      name: 'live.observer',
      category: 'live',
      type: 'api',
      description: 'Observes changes in Live Object Model',
      inlets: 1,
      outlets: 1,
      tags: ['live', 'api', 'observer', 'monitoring', 'automation'],
      difficulty: 'advanced',
      usage: 'live.observer [path] [property]',
      example: 'live.observer live_set tempo',
      parameters: ['path', 'property'],
      relatedObjects: ['live.object', 'live.path']
    },
    {
      name: 'live.button',
      category: 'live',
      type: 'ui',
      description: 'Button control that maps to Live parameters',
      inlets: 1,
      outlets: 1,
      tags: ['live', 'ui', 'button', 'parameter', 'control'],
      difficulty: 'beginner',
      usage: 'live.button @parameter_enable 1',
      example: 'live.button @parameter_enable 1 @automation 1',
      parameters: ['parameter_enable', 'automation', 'varname'],
      relatedObjects: ['live.toggle', 'live.tab', 'button']
    },
    {
      name: 'live.in~',
      category: 'live',
      type: 'audio',
      description: 'Audio input from Live tracks',
      inlets: 0,
      outlets: 2,
      tags: ['live', 'audio', 'input', 'track'],
      difficulty: 'beginner',
      usage: 'live.in~',
      example: 'live.in~',
      parameters: [],
      relatedObjects: ['live.out~', 'adc~', 'plugin~']
    },
    {
      name: 'live.out~',
      category: 'live',
      type: 'audio',
      description: 'Audio output to Live tracks',
      inlets: 2,
      outlets: 0,
      tags: ['live', 'audio', 'output', 'track'],
      difficulty: 'beginner',
      usage: 'live.out~',
      example: 'live.out~',
      parameters: [],
      relatedObjects: ['live.in~', 'dac~', 'plugin~']
    }
  ],

  // Utility Objects
  utility: [
    {
      name: 'metro',
      category: 'utility',
      type: 'timing',
      description: 'Metronome for regular timing',
      inlets: 2,
      outlets: 1,
      tags: ['timing', 'metronome', 'clock', 'utility'],
      difficulty: 'beginner',
      usage: 'metro [interval]',
      example: 'metro 1000',
      parameters: ['interval', 'active'],
      relatedObjects: ['tempo', 'clocker', 'timer']
    },
    {
      name: 'random',
      category: 'utility',
      type: 'data',
      description: 'Random number generator',
      inlets: 2,
      outlets: 1,
      tags: ['random', 'number', 'generator', 'utility'],
      difficulty: 'beginner',
      usage: 'random [range]',
      example: 'random 128',
      parameters: ['range'],
      relatedObjects: ['urn', 'drunk', 'decide']
    },
    {
      name: 'counter',
      category: 'utility',
      type: 'data',
      description: 'Counts and outputs sequential numbers',
      inlets: 5,
      outlets: 4,
      tags: ['counter', 'sequence', 'number', 'utility'],
      difficulty: 'beginner',
      usage: 'counter [min] [max] [direction]',
      example: 'counter 0 127 1',
      parameters: ['min', 'max', 'direction'],
      relatedObjects: ['uzi', 'gate', 'select']
    },
    {
      name: 'gate',
      category: 'utility',
      type: 'routing',
      description: 'Routes input to selected outlet',
      inlets: 2,
      outlets: 0,
      tags: ['routing', 'gate', 'selector', 'utility'],
      difficulty: 'beginner',
      usage: 'gate [outlets]',
      example: 'gate 4',
      parameters: ['outlet_count'],
      relatedObjects: ['selector', 'switch', 'router']
    }
  ]
};

// Live Device Types Database
const LIVE_DEVICES_DATABASE = {
  instruments: [
    {
      name: 'Wavetable',
      class_name: 'Wavetable',
      category: 'instrument',
      type: 'synthesizer',
      description: 'Advanced wavetable synthesizer',
      tags: ['wavetable', 'synth', 'modulation', 'instrument'],
      parameters: ['Osc 1 Position', 'Osc 2 Position', 'Filter Freq', 'Filter Res'],
      presets: ['Init', 'Analog', 'Digital', 'Evolving', 'Percussive']
    },
    {
      name: 'Operator',
      class_name: 'Operator',
      category: 'instrument', 
      type: 'synthesizer',
      description: 'FM synthesis with 4 operators',
      tags: ['fm', 'operator', 'synth', 'algorithm', 'instrument'],
      parameters: ['A Freq', 'B Freq', 'C Freq', 'D Freq'],
      presets: ['Init', 'Bass', 'Lead', 'Pad', 'Bell']
    },
    {
      name: 'Simpler',
      class_name: 'Simpler',
      category: 'instrument',
      type: 'sampler',
      description: 'Simple sample-based instrument',
      tags: ['sampler', 'simple', 'instrument', 'sample'],
      parameters: ['Filter Freq', 'Filter Res', 'Env Attack', 'Env Decay'],
      presets: ['Classic', 'Modern', 'Vintage', 'Digital']
    }
  ],
  audioEffects: [
    {
      name: 'Reverb',
      class_name: 'Reverb',
      category: 'audio-effect',
      type: 'spatial',
      description: 'High-quality reverb processor',
      tags: ['reverb', 'space', 'ambience', 'effect'],
      parameters: ['Size', 'Decay', 'Damping', 'Dry/Wet'],
      presets: ['Hall', 'Room', 'Plate', 'Spring']
    },
    {
      name: 'Echo',
      class_name: 'Echo',
      category: 'audio-effect',
      type: 'time',
      description: 'Versatile delay effect',
      tags: ['delay', 'echo', 'time', 'feedback', 'effect'],
      parameters: ['Delay Time', 'Feedback', 'Dry/Wet', 'Filter Freq'],
      presets: ['1/8', '1/4', '1/2', 'Dotted', 'Triplet']
    },
    {
      name: 'EQ Eight',
      class_name: 'Eq8',
      category: 'audio-effect',
      type: 'filter',
      description: '8-band parametric equalizer',
      tags: ['eq', 'equalizer', 'filter', 'frequency', 'effect'],
      parameters: ['1 Freq A', '1 Gain A', '2 Freq A', '2 Gain A'],
      presets: ['Vocal', 'Master', 'Bass', 'Treble']
    }
  ],
  midiEffects: [
    {
      name: 'Arpeggiator',
      class_name: 'Arpeggiator',
      category: 'midi-effect',
      type: 'generator',
      description: 'MIDI arpeggiator with multiple patterns',
      tags: ['arpeggiator', 'midi', 'pattern', 'effect'],
      parameters: ['Rate', 'Steps', 'Distance', 'Repeats'],
      presets: ['Up', 'Down', 'UpDown', 'Random', 'Played']
    },
    {
      name: 'Scale',
      class_name: 'Scale',
      category: 'midi-effect',
      type: 'utility',
      description: 'Constrains notes to musical scales',
      tags: ['scale', 'midi', 'music theory', 'constraint', 'effect'],
      parameters: ['Root', 'Scale', 'Fold'],
      presets: ['Major', 'Minor', 'Dorian', 'Pentatonic']
    }
  ]
};

const ObjectTemplateBrowser = ({
  onObjectSelect,
  onTemplateSelect,
  onClose,
  isVisible = true
}) => {
  const [activeTab, setActiveTab] = useState('objects');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedDifficulty, setSelectedDifficulty] = useState([]);
  const [selectedTags, setSelectedTags] = useState([]);
  const [favorites, setFavorites] = useState(new Set());
  const [recentlyUsed, setRecentlyUsed] = useState([]);
  const [selectedObject, setSelectedObject] = useState(null);
  const [previewModalOpen, setPreviewModalOpen] = useState(false);

  const searchInputRef = useRef(null);

  // Focus search input when panel opens
  useEffect(() => {
    if (isVisible && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [isVisible]);

  // Combined objects database
  const allObjects = useMemo(() => {
    const objects = [];
    Object.entries(MAX_OBJECTS_DATABASE).forEach(([category, categoryObjects]) => {
      objects.push(...categoryObjects.map(obj => ({ ...obj, category })));
    });
    return objects;
  }, []);

  // Combined devices database
  const allDevices = useMemo(() => {
    const devices = [];
    Object.entries(LIVE_DEVICES_DATABASE).forEach(([category, categoryDevices]) => {
      devices.push(...categoryDevices.map(device => ({ ...device, category })));
    });
    return devices;
  }, []);

  // Get all available tags
  const allTags = useMemo(() => {
    const tagSet = new Set();
    allObjects.forEach(obj => obj.tags?.forEach(tag => tagSet.add(tag)));
    allDevices.forEach(device => device.tags?.forEach(tag => tagSet.add(tag)));
    QUICK_START_TEMPLATES.forEach(template => template.tags?.forEach(tag => tagSet.add(tag)));
    return Array.from(tagSet).sort();
  }, [allObjects, allDevices]);

  // Filter objects based on search and filters
  const filteredObjects = useMemo(() => {
    let filtered = allObjects;

    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      filtered = filtered.filter(obj => 
        obj.name.toLowerCase().includes(search) ||
        obj.description.toLowerCase().includes(search) ||
        obj.tags?.some(tag => tag.toLowerCase().includes(search))
      );
    }

    if (selectedCategory !== 'all') {
      filtered = filtered.filter(obj => obj.category === selectedCategory);
    }

    if (selectedDifficulty.length > 0) {
      filtered = filtered.filter(obj => selectedDifficulty.includes(obj.difficulty));
    }

    if (selectedTags.length > 0) {
      filtered = filtered.filter(obj => 
        selectedTags.some(tag => obj.tags?.includes(tag))
      );
    }

    return filtered;
  }, [allObjects, searchTerm, selectedCategory, selectedDifficulty, selectedTags]);

  // Filter devices
  const filteredDevices = useMemo(() => {
    let filtered = allDevices;

    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      filtered = filtered.filter(device => 
        device.name.toLowerCase().includes(search) ||
        device.description.toLowerCase().includes(search) ||
        device.tags?.some(tag => tag.toLowerCase().includes(search))
      );
    }

    if (selectedTags.length > 0) {
      filtered = filtered.filter(device => 
        selectedTags.some(tag => device.tags?.includes(tag))
      );
    }

    return filtered;
  }, [allDevices, searchTerm, selectedTags]);

  // Filter templates
  const filteredTemplates = useMemo(() => {
    let filtered = QUICK_START_TEMPLATES;

    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      filtered = filtered.filter(template => 
        template.name.toLowerCase().includes(search) ||
        template.description.toLowerCase().includes(search) ||
        template.tags?.some(tag => tag.toLowerCase().includes(search))
      );
    }

    if (selectedTags.length > 0) {
      filtered = filtered.filter(template => 
        selectedTags.some(tag => template.tags?.includes(tag))
      );
    }

    return filtered;
  }, [searchTerm, selectedTags]);

  const handleObjectSelect = useCallback((object) => {
    setRecentlyUsed(prev => {
      const updated = [object, ...prev.filter(obj => obj.name !== object.name)];
      return updated.slice(0, 10); // Keep last 10
    });
    onObjectSelect?.(object);
  }, [onObjectSelect]);

  const handleTemplateSelect = useCallback((template) => {
    setRecentlyUsed(prev => {
      const updated = [template, ...prev.filter(t => t.id !== template.id)];
      return updated.slice(0, 10);
    });
    onTemplateSelect?.(template);
  }, [onTemplateSelect]);

  const toggleFavorite = useCallback((item) => {
    setFavorites(prev => {
      const updated = new Set(prev);
      const key = item.name || item.id;
      if (updated.has(key)) {
        updated.delete(key);
      } else {
        updated.add(key);
      }
      return updated;
    });
  }, []);

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'beginner': return 'green';
      case 'intermediate': return 'orange';
      case 'advanced': return 'red';
      default: return 'gray';
    }
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'audio': return <IconWaveSquare size={16} />;
      case 'midi': return <IconMusic size={16} />;
      case 'live': return <IconDevices size={16} />;
      case 'utility': return <IconSettings size={16} />;
      default: return <IconZap size={16} />;
    }
  };

  const ObjectCard = ({ object, type = 'object' }) => (
    <Paper
      p="sm"
      withBorder
      className="object-card"
      style={{ cursor: 'pointer', transition: 'all 0.2s ease' }}
      onClick={() => {
        if (type === 'template') {
          handleTemplateSelect(object);
        } else {
          handleObjectSelect(object);
        }
      }}
    >
      <Group justify="space-between" align="flex-start" mb="xs">
        <Group gap="xs" align="center">
          {getCategoryIcon(object.category)}
          <Text fw={600} size="sm">{object.name}</Text>
          {object.difficulty && (
            <Badge size="xs" color={getDifficultyColor(object.difficulty)}>
              {object.difficulty}
            </Badge>
          )}
        </Group>
        
        <Group gap="xs">
          <ActionIcon
            size="xs"
            variant="subtle"
            onClick={(e) => {
              e.stopPropagation();
              toggleFavorite(object);
            }}
          >
            <IconHeart 
              size={12} 
              fill={favorites.has(object.name || object.id) ? 'red' : 'none'}
              color={favorites.has(object.name || object.id) ? 'red' : 'gray'}
            />
          </ActionIcon>
          <ActionIcon
            size="xs"
            variant="subtle"
            onClick={(e) => {
              e.stopPropagation();
              setSelectedObject(object);
              setPreviewModalOpen(true);
            }}
          >
            <IconEye size={12} />
          </ActionIcon>
        </Group>
      </Group>

      <Text size="xs" c="dimmed" mb="xs" lineClamp={2}>
        {object.description}
      </Text>

      {object.tags && (
        <Group gap="xs" mb="xs">
          {object.tags.slice(0, 3).map(tag => (
            <Badge key={tag} size="xs" variant="dot" color="gray">
              {tag}
            </Badge>
          ))}
          {object.tags.length > 3 && (
            <Text size="xs" c="dimmed">+{object.tags.length - 3}</Text>
          )}
        </Group>
      )}

      {type === 'object' && (
        <Group gap="sm" justify="space-between">
          <Text size="xs" c="dimmed">
            {object.inlets}→{object.outlets}
          </Text>
          {object.usage && (
            <Code size="xs" style={{ fontSize: '10px' }}>
              {object.example || object.usage}
            </Code>
          )}
        </Group>
      )}
    </Paper>
  );

  if (!isVisible) return null;

  return (
    <Paper 
      className="object-template-browser-overlay" 
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000
      }}
    >
      <Paper 
        shadow="xl"
        radius="md"
        style={{
          width: '95%',
          maxWidth: 1200,
          height: '90vh',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        {/* Header */}
        <Group justify="space-between" p="md" style={{ borderBottom: '1px solid var(--mantine-color-gray-3)' }}>
          <Group gap="sm">
            <IconBook size={20} />
            <Text size="lg" fw={600}>Object & Template Browser</Text>
            <Badge variant="light" size="sm">Max Live IDE</Badge>
          </Group>
          <CloseButton onClick={onClose} size="lg" />
        </Group>

        {/* Search and Filters */}
        <Paper p="md" style={{ borderBottom: '1px solid var(--mantine-color-gray-3)' }}>
          <Stack gap="md">
            <Group grow>
              <TextInput
                ref={searchInputRef}
                placeholder="Search objects, devices, and templates..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                leftSection={<IconSearch size={16} />}
                size="md"
              />
              <Select
                placeholder="Category"
                value={selectedCategory}
                onChange={setSelectedCategory}
                data={[
                  { value: 'all', label: 'All Categories' },
                  { value: 'audio', label: 'Audio Objects' },
                  { value: 'midi', label: 'MIDI Objects' },
                  { value: 'live', label: 'Live API Objects' },
                  { value: 'utility', label: 'Utility Objects' }
                ]}
              />
            </Group>

            <Group>
              <MultiSelect
                placeholder="Difficulty"
                value={selectedDifficulty}
                onChange={setSelectedDifficulty}
                data={[
                  { value: 'beginner', label: 'Beginner' },
                  { value: 'intermediate', label: 'Intermediate' },
                  { value: 'advanced', label: 'Advanced' }
                ]}
                size="sm"
                style={{ minWidth: 200 }}
              />
              <MultiSelect
                placeholder="Filter by tags..."
                value={selectedTags}
                onChange={setSelectedTags}
                data={allTags.map(tag => ({ value: tag, label: tag }))}
                searchable
                size="sm"
                style={{ flex: 1 }}
              />
            </Group>
          </Stack>
        </Paper>

        {/* Tabs */}
        <Tabs value={activeTab} onChange={setActiveTab} style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          <Tabs.List px="md">
            <Tabs.Tab value="objects" leftSection={<IconZap size={16} />}>
              Max Objects ({filteredObjects.length})
            </Tabs.Tab>
            <Tabs.Tab value="devices" leftSection={<IconDevices size={16} />}>
              Live Devices ({filteredDevices.length})
            </Tabs.Tab>
            <Tabs.Tab value="templates" leftSection={<IconTemplate size={16} />}>
              Templates ({filteredTemplates.length})
            </Tabs.Tab>
            {recentlyUsed.length > 0 && (
              <Tabs.Tab value="recent" leftSection={<IconTarget size={16} />}>
                Recent ({recentlyUsed.length})
              </Tabs.Tab>
            )}
            {favorites.size > 0 && (
              <Tabs.Tab value="favorites" leftSection={<IconHeart size={16} />}>
                Favorites ({favorites.size})
              </Tabs.Tab>
            )}
          </Tabs.List>

          <div style={{ flex: 1, overflow: 'hidden' }}>
            <Tabs.Panel value="objects" style={{ height: '100%' }}>
              <ScrollArea h="100%" p="md">
                <SimpleGrid cols={3} spacing="md">
                  {filteredObjects.map(object => (
                    <ObjectCard key={object.name} object={object} />
                  ))}
                </SimpleGrid>
                {filteredObjects.length === 0 && (
                  <Text ta="center" c="dimmed" mt="xl">
                    No Max objects found matching your criteria
                  </Text>
                )}
              </ScrollArea>
            </Tabs.Panel>

            <Tabs.Panel value="devices" style={{ height: '100%' }}>
              <ScrollArea h="100%" p="md">
                <SimpleGrid cols={3} spacing="md">
                  {filteredDevices.map(device => (
                    <ObjectCard key={device.name} object={device} />
                  ))}
                </SimpleGrid>
                {filteredDevices.length === 0 && (
                  <Text ta="center" c="dimmed" mt="xl">
                    No Live devices found matching your criteria
                  </Text>
                )}
              </ScrollArea>
            </Tabs.Panel>

            <Tabs.Panel value="templates" style={{ height: '100%' }}>
              <ScrollArea h="100%" p="md">
                <SimpleGrid cols={2} spacing="md">
                  {filteredTemplates.map(template => (
                    <ObjectCard key={template.id} object={template} type="template" />
                  ))}
                </SimpleGrid>
                {filteredTemplates.length === 0 && (
                  <Text ta="center" c="dimmed" mt="xl">
                    No templates found matching your criteria
                  </Text>
                )}
              </ScrollArea>
            </Tabs.Panel>

            {recentlyUsed.length > 0 && (
              <Tabs.Panel value="recent" style={{ height: '100%' }}>
                <ScrollArea h="100%" p="md">
                  <SimpleGrid cols={3} spacing="md">
                    {recentlyUsed.map(item => (
                      <ObjectCard 
                        key={item.name || item.id} 
                        object={item} 
                        type={item.id ? 'template' : 'object'} 
                      />
                    ))}
                  </SimpleGrid>
                </ScrollArea>
              </Tabs.Panel>
            )}
          </div>
        </Tabs>

        {/* Footer */}
        <Divider />
        <Group justify="center" gap="md" p="sm">
          <Group gap="xs">
            <Kbd>↑↓</Kbd>
            <Text size="xs" c="dimmed">Navigate</Text>
          </Group>
          <Group gap="xs">
            <Kbd>Enter</Kbd>
            <Text size="xs" c="dimmed">Select</Text>
          </Group>
          <Group gap="xs">
            <Kbd>Esc</Kbd>
            <Text size="xs" c="dimmed">Close</Text>
          </Group>
          <Group gap="xs">
            <Kbd>Ctrl+F</Kbd>
            <Text size="xs" c="dimmed">Focus search</Text>
          </Group>
        </Group>
      </Paper>

      {/* Object Preview Modal */}
      <Modal
        opened={previewModalOpen}
        onClose={() => setPreviewModalOpen(false)}
        title={
          <Group gap="sm">
            {selectedObject && getCategoryIcon(selectedObject.category)}
            <Text fw={600}>{selectedObject?.name}</Text>
            {selectedObject?.difficulty && (
              <Badge color={getDifficultyColor(selectedObject.difficulty)}>
                {selectedObject.difficulty}
              </Badge>
            )}
          </Group>
        }
        size="lg"
      >
        {selectedObject && (
          <Stack gap="md">
            <Text>{selectedObject.description}</Text>
            
            {selectedObject.usage && (
              <div>
                <Text size="sm" fw={500} mb="xs">Usage:</Text>
                <Code block>{selectedObject.usage}</Code>
              </div>
            )}

            {selectedObject.example && selectedObject.example !== selectedObject.usage && (
              <div>
                <Text size="sm" fw={500} mb="xs">Example:</Text>
                <Code block>{selectedObject.example}</Code>
              </div>
            )}

            {selectedObject.parameters && selectedObject.parameters.length > 0 && (
              <div>
                <Text size="sm" fw={500} mb="xs">Parameters:</Text>
                <Group gap="xs">
                  {selectedObject.parameters.map(param => (
                    <Badge key={param} variant="outline" size="sm">{param}</Badge>
                  ))}
                </Group>
              </div>
            )}

            {selectedObject.relatedObjects && selectedObject.relatedObjects.length > 0 && (
              <div>
                <Text size="sm" fw={500} mb="xs">Related Objects:</Text>
                <Group gap="xs">
                  {selectedObject.relatedObjects.map(obj => (
                    <Anchor 
                      key={obj} 
                      size="sm"
                      onClick={() => {
                        setSearchTerm(obj);
                        setPreviewModalOpen(false);
                      }}
                    >
                      {obj}
                    </Anchor>
                  ))}
                </Group>
              </div>
            )}

            <Group gap="md" justify="center" mt="md">
              <Button
                leftSection={<IconDownload size={16} />}
                onClick={() => {
                  handleObjectSelect(selectedObject);
                  setPreviewModalOpen(false);
                }}
              >
                Add to Patch
              </Button>
              <Button
                variant="light"
                leftSection={<IconCopy size={16} />}
                onClick={() => {
                  navigator.clipboard.writeText(selectedObject.example || selectedObject.usage || selectedObject.name);
                }}
              >
                Copy Usage
              </Button>
            </Group>
          </Stack>
        )}
      </Modal>
    </Paper>
  );
};

export default ObjectTemplateBrowser;
