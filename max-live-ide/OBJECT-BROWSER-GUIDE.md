# 📚 Object & Template Search Browser

## Overview

A comprehensive, unified search and browsing system for Max objects, Live API objects, Live devices, and pre-built templates. This browser makes it easy to discover, preview, and add components to your Max Live IDE patches.

## 🌟 Features

### 🔍 **Unified Search**
- Search across Max objects, Live API objects, Live devices, and templates
- Intelligent search matching names, descriptions, and tags
- Real-time filtering and instant results
- Search history and suggestions

### 📂 **Categorized Browsing**
- **Max Objects**: Audio generators, MIDI processors, utility objects
- **Live API Objects**: live.dial, live.gain~, live.object, live.observer
- **Live Devices**: Wavetable, Operator, Reverb, EQ Eight, Arpeggiator
- **Templates**: Pre-built patches for instant workflow

### 🎛️ **Advanced Filtering**
- Filter by category (Audio, MIDI, Live API, Utility)
- Filter by difficulty (Beginner, Intermediate, Advanced)
- Filter by tags (multiple tag selection)
- Quick filter buttons for common searches

### ❤️ **Smart Features**
- **Favorites**: Heart icon to save frequently used items
- **Recently Used**: Track your most recent selections
- **Quick Preview**: Eye icon to preview object details
- **Usage Examples**: Code examples and parameter info

### ⌨️ **Keyboard Shortcuts**
- `Ctrl+Shift+O` - Open Object Browser
- `Ctrl+F` - Focus search input
- `Esc` - Close browser
- `↑↓` - Navigate results
- `Enter` - Select item

## 📦 Database Contents

### Audio Objects (10+)
```javascript
osc~        // Oscillator with multiple waveforms
cycle~      // Sine wave oscillator  
saw~        // Sawtooth wave oscillator
rect~       // Rectangle wave oscillator
noise~      // White noise generator
biquad~     // Biquadratic filter
delay~      // Variable delay line
gain~       // Audio level control
dac~        // Digital-to-analog converter
ezdac~      // Easy audio output
```

### MIDI Objects (6+)
```javascript
notein      // Receives MIDI note messages
noteout     // Sends MIDI note messages
ctlin       // Receives MIDI control change
ctlout      // Sends MIDI control change
makenote    // Creates note-on/off pairs
stripnote   // Removes note-off messages
```

### Live API Objects (7+)
```javascript
live.dial     // Rotary control for Live parameters
live.gain~    // Audio gain with Live parameter mapping
live.object   // Access to Live Object Model (LOM)
live.observer // Observes changes in Live Object Model
live.button   // Button control for Live parameters
live.in~      // Audio input from Live tracks
live.out~     // Audio output to Live tracks
```

### Utility Objects (4+)
```javascript
metro       // Metronome for regular timing
random      // Random number generator
counter     // Counts and outputs sequential numbers
gate        // Routes input to selected outlet
```

### Live Devices Database

#### Instruments
- **Wavetable** - Advanced wavetable synthesizer
- **Operator** - FM synthesis with 4 operators
- **Simpler** - Simple sample-based instrument

#### Audio Effects
- **Reverb** - High-quality reverb processor
- **Echo** - Versatile delay effect
- **EQ Eight** - 8-band parametric equalizer

#### MIDI Effects
- **Arpeggiator** - MIDI arpeggiator with multiple patterns
- **Scale** - Constrains notes to musical scales

### Quick Start Templates

#### 1. Simple Synth
- Basic oscillator with filter and envelope
- Objects: live.dial, osc~, live.gain~, ezdac~
- Difficulty: Beginner

#### 2. MIDI Effect
- Note processor with velocity and timing control
- Objects: notein, live.dial, noteout
- Difficulty: Beginner

#### 3. Audio Effect
- Signal processing chain with filter
- Objects: live.in~, biquad~, live.out~
- Difficulty: Intermediate

#### 4. Live API Control
- Control Ableton Live parameters and transport
- Objects: live.object, live.button
- Difficulty: Advanced

## 🚀 Usage Guide

### Opening the Browser
```javascript
// Programmatically
browserControls.openBrowser();

// Keyboard shortcut
Ctrl+Shift+O

// Button click
<Button onClick={openBrowser}>Object Browser</Button>
```

### Searching Objects
1. **Basic Search**: Type object name (e.g., "osc", "gain")
2. **Tag Search**: Search by functionality (e.g., "oscillator", "filter")
3. **Description Search**: Search descriptions (e.g., "delay", "reverb")

### Adding Objects to Patch
```javascript
// Object selection handler
const handleObjectSelect = (object) => {
  const newNode = insertObject(object, position);
  browserControls.addToRecent(object);
  browserControls.closeBrowser();
};

// Template selection handler  
const handleTemplateSelect = (template) => {
  const result = insertTemplate(template, position);
  browserControls.addToRecent(template);
  browserControls.closeBrowser();
};
```

### Managing Favorites
```javascript
// Toggle favorite
browserControls.toggleFavorite(object);

// Check if favorited
const isFavorited = favorites.has(object.name);

// Clear all favorites
browserControls.clearFavorites();
```

## 🛠️ Integration

### Component Integration
```javascript
import ObjectTemplateBrowser from './components/ObjectTemplateBrowser';
import { useObjectTemplateBrowser, useObjectInsertion } from './hooks/useObjectTemplateBrowser';

const MyApp = () => {
  const browserControls = useObjectTemplateBrowser();
  const { insertObject, insertTemplate } = useObjectInsertion(setNodes, setEdges);

  return (
    <>
      <Button onClick={browserControls.openBrowser}>
        Open Browser
      </Button>
      
      <ObjectTemplateBrowser
        isVisible={browserControls.isOpen}
        onObjectSelect={insertObject}
        onTemplateSelect={insertTemplate}
        onClose={browserControls.closeBrowser}
      />
    </>
  );
};
```

### Hook Usage
```javascript
// Browser state management
const {
  isOpen,
  searchTerm,
  favorites,
  recentlyUsed,
  openBrowser,
  closeBrowser,
  toggleFavorite,
  addToRecent
} = useObjectTemplateBrowser();

// Keyboard shortcuts
useObjectBrowserShortcuts(browserControls);

// Object insertion
const { insertObject, insertTemplate } = useObjectInsertion(setNodes, setEdges);
```

## 🎨 Customization

### Styling
```css
/* Main browser overlay */
.object-template-browser-overlay {
  backdrop-filter: blur(4px);
  animation: fadeIn 0.2s ease-out;
}

/* Object cards */
.object-card:hover {
  border-color: var(--mantine-color-blue-4);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

/* Category colors */
.object-card[data-category="audio"] {
  border-left: 4px solid #17e2c3;
}
```

### Adding Custom Objects
```javascript
// Add to MAX_OBJECTS_DATABASE
const customObjects = {
  myCategory: [
    {
      name: 'custom~',
      category: 'mycategory',
      type: 'generator',
      description: 'My custom object',
      inlets: 2,
      outlets: 1,
      tags: ['custom', 'special'],
      difficulty: 'advanced',
      usage: 'custom~ [param1] [param2]',
      example: 'custom~ 440 0.5'
    }
  ]
};
```

## 📊 Analytics & Tracking

The browser includes built-in analytics to track usage patterns:

```javascript
const analytics = useObjectAnalytics();

// Track search
analytics.trackSearch('osc', 5); // term, result count

// Track object usage
analytics.trackObjectUsage('osc~');

// Get popular objects
const popular = analytics.getPopularObjects(10);

// Get popular searches
const searches = analytics.getPopularSearches(10);
```

## 🔧 Performance

### Optimizations
- **Virtualized scrolling** for large object lists
- **Debounced search** (300ms) to prevent excessive filtering
- **Memoized filtering** to avoid unnecessary recalculations
- **Lazy loading** of object previews
- **Local storage** for favorites and recent items

### Memory Management
- Recent items limited to 10 entries
- Search history limited to 100 entries
- Automatic cleanup of unused observers
- Efficient component re-rendering with React.memo

## 🧪 Testing

### Manual Testing
1. Open browser with `Ctrl+Shift+O`
2. Search for "osc" - should show oscillator objects
3. Filter by "Audio" category
4. Add object to favorites
5. Select template and verify nodes are added
6. Check recent items tab appears
7. Test keyboard navigation with arrow keys

### Automated Testing
```javascript
// Test object search
expect(filterObjects(objects, { searchTerm: 'osc' }))
  .toContain(expect.objectContaining({ name: 'osc~' }));

// Test template insertion
const result = insertTemplate(simplesynthTemplate);
expect(result.nodes).toHaveLength(4);
expect(result.edges).toHaveLength(3);
```

## 🚧 Future Enhancements

### Planned Features
- [ ] **Custom Object Creation** - Visual object builder
- [ ] **Object Documentation** - Integrated help system
- [ ] **Template Sharing** - Export/import templates
- [ ] **Advanced Analytics** - Usage heatmaps and insights
- [ ] **Plugin System** - Third-party object integration
- [ ] **AI Suggestions** - Smart object recommendations
- [ ] **Version Control** - Template versioning and history

### Potential Integrations
- [ ] **Max Package Manager** integration
- [ ] **Ableton Live Browser** sync
- [ ] **GitHub Templates** repository
- [ ] **Max Community** object sharing
- [ ] **Max Documentation** deep linking

## 🐛 Troubleshooting

### Common Issues

**Browser won't open**
- Check keyboard shortcut conflicts
- Verify component is properly imported
- Check console for JavaScript errors

**Objects not inserting**
- Verify `insertObject` function is connected
- Check node data structure compatibility
- Ensure position coordinates are valid

**Search not working**
- Check search term formatting
- Verify object database is loaded
- Clear browser cache if needed

**Favorites not persisting**
- Check localStorage permissions
- Verify JSON serialization is working
- Clear corrupted localStorage data

### Debug Mode
```javascript
// Enable debug logging
localStorage.setItem('max-live-ide-debug', 'true');

// View browser state
console.log('Browser state:', browserControls);

// Check object database
console.log('Objects:', MAX_OBJECTS_DATABASE);
```

---

## 📄 License

This Object & Template Browser is part of the Max Live IDE project and follows the same licensing terms.

## 🤝 Contributing

To contribute new objects, templates, or features:

1. Fork the repository
2. Add objects to the appropriate database
3. Update documentation
4. Create tests for new functionality
5. Submit a pull request

---

*Built with ❤️ for the Max Live IDE community*
