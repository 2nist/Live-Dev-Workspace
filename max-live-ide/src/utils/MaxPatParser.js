/**
 * MaxPat Parser - Object-oriented parser for .maxpat files
 * 
 * Handles JSON parsing of Max/MSP patch files with support for:
 * - Recursive subpatcher parsing
 * - Object-oriented structure
 * - Schema validation
 * - Lossless round-trip JSON conversion
 */

class MaxPatchObject {
  constructor(data) {
    this.box = data.box || {};
    this.id = this.box.id;
    this.maxclass = this.box.maxclass;
    this.text = this.box.text;
    this.patching_rect = this.box.patching_rect || [];
    this.numinlets = this.box.numinlets || 0;
    this.numoutlets = this.box.numoutlets || 0;
    this.raw = data; // Keep original data for lossless export
  }

  isSubpatcher() {
    return this.maxclass === 'newobj' && 
           (this.text === 'p' || this.text?.startsWith('p '));
  }

  toJSON() {
    return this.raw;
  }
}

class MaxPatchLine {
  constructor(data) {
    this.patchline = data.patchline || {};
    this.source = this.patchline.source || [];
    this.destination = this.patchline.destination || [];
    this.raw = data;
  }

  getSourceId() {
    return this.source[0];
  }

  getDestinationId() {
    return this.destination[0];
  }

  getSourceOutlet() {
    return this.source[1] || 0;
  }

  getDestinationInlet() {
    return this.destination[1] || 0;
  }

  toJSON() {
    return this.raw;
  }
}

class MaxPatcher {
  constructor(data) {
    this.patcher = data.patcher || data;
    this.fileversion = this.patcher.fileversion || 1;
    this.appversion = this.patcher.appversion || {};
    this.rect = this.patcher.rect || [];
    this.bglocked = this.patcher.bglocked || 0;
    this.openinpresentation = this.patcher.openinpresentation || 0;
    this.default_fontsize = this.patcher.default_fontsize || 12.0;
    this.default_fontface = this.patcher.default_fontface || 0;
    this.default_fontname = this.patcher.default_fontname || "Arial";
    
    // Parse objects and lines
    this.objects = (this.patcher.boxes || []).map(box => new MaxPatchObject(box));
    this.lines = (this.patcher.lines || []).map(line => new MaxPatchLine(line));
    
    // Find subpatchers recursively
    this.subpatchers = this.findSubpatchers();
    
    this.raw = data; // Keep original for lossless export
  }

  findSubpatchers() {
    const subpatchers = {};
    
    this.objects.forEach(obj => {
      if (obj.isSubpatcher() && obj.raw.patcher) {
        // Recursively parse subpatcher
        subpatchers[obj.id] = new MaxPatcher(obj.raw.patcher);
      }
    });
    
    return subpatchers;
  }

  getObjectById(id) {
    return this.objects.find(obj => obj.id === id);
  }

  getConnectedObjects(objectId) {
    const connections = {
      inputs: [],
      outputs: []
    };
    
    this.lines.forEach(line => {
      if (line.getDestinationId() === objectId) {
        connections.inputs.push({
          source: line.getSourceId(),
          outlet: line.getSourceOutlet(),
          inlet: line.getDestinationInlet()
        });
      }
      
      if (line.getSourceId() === objectId) {
        connections.outputs.push({
          destination: line.getDestinationId(),
          outlet: line.getSourceOutlet(),
          inlet: line.getDestinationInlet()
        });
      }
    });
    
    return connections;
  }

  addObject(objectData) {
    const newObject = new MaxPatchObject(objectData);
    this.objects.push(newObject);
    return newObject;
  }

  addConnection(sourceId, sourceOutlet, destId, destInlet) {
    const lineData = {
      patchline: {
        source: [sourceId, sourceOutlet],
        destination: [destId, destInlet]
      }
    };
    
    const newLine = new MaxPatchLine(lineData);
    this.lines.push(newLine);
    return newLine;
  }

  removeObject(objectId) {
    // Remove object
    this.objects = this.objects.filter(obj => obj.id !== objectId);
    
    // Remove connected lines
    this.lines = this.lines.filter(line => 
      line.getSourceId() !== objectId && line.getDestinationId() !== objectId
    );
  }

  toJSON() {
    // Rebuild the original structure for Max compatibility
    const result = { ...this.raw };
    
    // Update boxes with current objects
    result.patcher.boxes = this.objects.map(obj => obj.toJSON());
    
    // Update lines with current connections
    result.patcher.lines = this.lines.map(line => line.toJSON());
    
    // Recursively update subpatchers
    Object.keys(this.subpatchers).forEach(id => {
      const obj = this.getObjectById(id);
      if (obj && obj.raw.patcher) {
        obj.raw.patcher = this.subpatchers[id].toJSON().patcher;
      }
    });
    
    return result;
  }
}

class MaxPatParser {
  static parse(jsonData) {
    try {
      const data = typeof jsonData === 'string' ? JSON.parse(jsonData) : jsonData;
      return new MaxPatcher(data);
    } catch (error) {
      throw new Error(`Failed to parse maxpat file: ${error.message}`);
    }
  }

  static stringify(patcher, pretty = true) {
    const json = patcher.toJSON();
    return JSON.stringify(json, null, pretty ? 2 : 0);
  }

  static validate(data) {
    // Basic schema validation
    const required = ['patcher'];
    
    if (typeof data !== 'object') {
      throw new Error('Invalid maxpat: must be an object');
    }
    
    if (!data.patcher) {
      throw new Error('Invalid maxpat: missing patcher object');
    }
    
    if (!Array.isArray(data.patcher.boxes)) {
      data.patcher.boxes = [];
    }
    
    if (!Array.isArray(data.patcher.lines)) {
      data.patcher.lines = [];
    }
    
    return true;
  }
}

// Export for Node.js or browser
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { MaxPatParser, MaxPatcher, MaxPatchObject, MaxPatchLine };
} else if (typeof window !== 'undefined') {
  window.MaxPatParser = MaxPatParser;
  window.MaxPatcher = MaxPatcher;
  window.MaxPatchObject = MaxPatchObject;
  window.MaxPatchLine = MaxPatchLine;
}
