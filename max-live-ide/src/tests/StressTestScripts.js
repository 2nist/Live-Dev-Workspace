/**
 * Stress Test Scripts for Large Patch Performance
 * Tests interaction performance with 200+ nodes and complex routing
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { act } from 'react-dom/test-utils';
import PerformanceOptimizedReactFlow from '../components/performance/OptimizedReactFlow';

// ========================================
// 1. STRESS TEST DATA GENERATORS
// ========================================

export const generateStressTestNodes = (count = 500, options = {}) => {
  const {
    nodeTypes = ['audio', 'utility', 'midi', 'control'],
    complexityDistribution = { simple: 0.6, medium: 0.3, complex: 0.1 },
    layout = 'hierarchical'
  } = options;

  const nodes = [];
  
  for (let i = 0; i < count; i++) {
    const nodeType = nodeTypes[Math.floor(Math.random() * nodeTypes.length)];
    const complexity = getComplexityLevel(complexityDistribution);
    const position = calculateNodePosition(i, count, layout);
    
    nodes.push({
      id: `stress-node-${i}`,
      type: 'maxObject',
      position,
      data: generateNodeData(nodeType, complexity, i),
      zIndex: Math.floor(Math.random() * 10) + 1
    });
  }
  
  return nodes;
};

const getComplexityLevel = (distribution) => {
  const rand = Math.random();
  if (rand < distribution.simple) return 'simple';
  if (rand < distribution.simple + distribution.medium) return 'medium';
  return 'complex';
};

const calculateNodePosition = (index, total, layout) => {
  switch (layout) {
    case 'grid':
      const cols = Math.ceil(Math.sqrt(total));
      return {
        x: (index % cols) * 200 + Math.random() * 50,
        y: Math.floor(index / cols) * 150 + Math.random() * 50
      };
      
    case 'hierarchical':
      const layers = Math.ceil(Math.log2(total));
      const layer = Math.floor((index / total) * layers);
      const positionInLayer = index % Math.ceil(total / layers);
      return {
        x: positionInLayer * 180 + Math.random() * 40,
        y: layer * 120 + Math.random() * 30
      };
      
    case 'circular':
      const radius = Math.sqrt(total) * 20;
      const angle = (index / total) * 2 * Math.PI;
      return {
        x: radius * Math.cos(angle) + 1000,
        y: radius * Math.sin(angle) + 600
      };
      
    default: // random
      return {
        x: Math.random() * 2000,
        y: Math.random() * 1500
      };
  }
};

const generateNodeData = (nodeType, complexity, index) => {
  const baseData = {
    label: generateNodeLabel(nodeType, index),
    objectType: nodeType,
    status: Math.random() > 0.8 ? 'running' : 'connected',
    tags: getNodeTags(nodeType)
  };

  if (complexity === 'complex') {
    baseData.parameters = generateComplexParameters(nodeType);
    baseData.inputs = Array.from({ length: Math.floor(Math.random() * 4) + 2 }, (_, i) => ({
      id: `input-${i}`,
      name: `Input ${i + 1}`,
      type: 'signal'
    }));
    baseData.outputs = Array.from({ length: Math.floor(Math.random() * 4) + 1 }, (_, i) => ({
      id: `output-${i}`,
      name: `Output ${i + 1}`,
      type: 'signal'
    }));
  } else if (complexity === 'medium') {
    baseData.parameters = generateMediumParameters(nodeType);
    baseData.inputs = [{ id: 'input-0', name: 'Input', type: 'signal' }];
    baseData.outputs = [{ id: 'output-0', name: 'Output', type: 'signal' }];
  }

  return baseData;
};

const generateNodeLabel = (nodeType, index) => {
  const labels = {
    audio: ['osc~', 'filter~', 'delay~', 'reverb~', 'compressor~', 'eq~'],
    utility: ['metro', 'counter', 'random', 'trigger', 'gate', 'select'],
    midi: ['notein', 'noteout', 'ctlin', 'ctlout', 'pgmin', 'pgmout'],
    control: ['slider', 'dial', 'button', 'toggle', 'multislider', 'gain']
  };
  
  const typeLabels = labels[nodeType] || ['object'];
  const baseLabel = typeLabels[Math.floor(Math.random() * typeLabels.length)];
  
  return `${baseLabel} ${index % 100}`;
};

const getNodeTags = (nodeType) => {
  const tagMap = {
    audio: ['audio', 'signal', 'processing'],
    utility: ['utility', 'logic', 'control'],
    midi: ['midi', 'communication', 'protocol'],
    control: ['control', 'interface', 'interaction']
  };
  
  return tagMap[nodeType] || ['unknown'];
};

const generateComplexParameters = (nodeType) => {
  const paramSets = {
    audio: {
      frequency: Math.floor(Math.random() * 20000) + 20,
      amplitude: Math.random().toFixed(3),
      phase: Math.floor(Math.random() * 360),
      resonance: Math.random().toFixed(2),
      cutoff: Math.floor(Math.random() * 20000) + 20
    },
    utility: {
      interval: Math.floor(Math.random() * 1000) + 1,
      count: Math.floor(Math.random() * 100),
      mode: Math.floor(Math.random() * 4),
      threshold: Math.random().toFixed(3)
    },
    midi: {
      channel: Math.floor(Math.random() * 16) + 1,
      controller: Math.floor(Math.random() * 128),
      velocity: Math.floor(Math.random() * 128),
      note: Math.floor(Math.random() * 128)
    },
    control: {
      min: Math.floor(Math.random() * 100),
      max: Math.floor(Math.random() * 900) + 100,
      value: Math.floor(Math.random() * 100),
      step: Math.random().toFixed(2)
    }
  };
  
  return paramSets[nodeType] || { value: Math.random().toFixed(3) };
};

const generateMediumParameters = (nodeType) => {
  const params = generateComplexParameters(nodeType);
  const keys = Object.keys(params);
  const reducedKeys = keys.slice(0, Math.ceil(keys.length / 2));
  
  return reducedKeys.reduce((result, key) => {
    result[key] = params[key];
    return result;
  }, {});
};

export const generateStressTestEdges = (nodes, options = {}) => {
  const {
    density = 0.3,
    patterns = ['sequential', 'hub-spoke', 'mesh'],
    maxConnectionsPerNode = 6
  } = options;

  const edges = [];
  const nodeConnections = new Map();
  
  // Initialize connection tracking
  nodes.forEach(node => {
    nodeConnections.set(node.id, { incoming: 0, outgoing: 0 });
  });

  const targetConnections = Math.floor(nodes.length * density);
  let connectionAttempts = 0;
  const maxAttempts = targetConnections * 3;

  while (edges.length < targetConnections && connectionAttempts < maxAttempts) {
    connectionAttempts++;
    
    const pattern = patterns[Math.floor(Math.random() * patterns.length)];
    const edge = generateEdgeByPattern(nodes, pattern, nodeConnections, maxConnectionsPerNode);
    
    if (edge && !edges.find(e => e.id === edge.id)) {
      edges.push(edge);
      
      // Update connection counts
      const sourceConnections = nodeConnections.get(edge.source);
      const targetConnections = nodeConnections.get(edge.target);
      
      if (sourceConnections) sourceConnections.outgoing++;
      if (targetConnections) targetConnections.incoming++;
    }
  }

  return edges;
};

const generateEdgeByPattern = (nodes, pattern, connections, maxConnections) => {
  switch (pattern) {
    case 'sequential':
      return generateSequentialEdge(nodes, connections, maxConnections);
    case 'hub-spoke':
      return generateHubSpokeEdge(nodes, connections, maxConnections);
    case 'mesh':
      return generateMeshEdge(nodes, connections, maxConnections);
    default:
      return generateRandomEdge(nodes, connections, maxConnections);
  }
};

const generateSequentialEdge = (nodes, connections, maxConnections) => {
  const availableNodes = nodes.filter(node => {
    const conn = connections.get(node.id);
    return conn.outgoing < maxConnections && conn.incoming < maxConnections;
  });

  if (availableNodes.length < 2) return null;

  // Sort by position for sequential flow
  availableNodes.sort((a, b) => a.position.x - b.position.x || a.position.y - b.position.y);

  for (let i = 0; i < availableNodes.length - 1; i++) {
    const source = availableNodes[i];
    const target = availableNodes[i + 1];
    
    if (connections.get(source.id).outgoing < maxConnections &&
        connections.get(target.id).incoming < maxConnections) {
      
      return createEdge(source.id, target.id);
    }
  }

  return null;
};

const generateHubSpokeEdge = (nodes, connections, maxConnections) => {
  // Find potential hub nodes (nodes with low connection counts)
  const potentialHubs = nodes.filter(node => {
    const conn = connections.get(node.id);
    return conn.outgoing + conn.incoming < maxConnections * 0.8;
  });

  if (potentialHubs.length === 0) return generateRandomEdge(nodes, connections, maxConnections);

  const hub = potentialHubs[Math.floor(Math.random() * potentialHubs.length)];
  const spokes = nodes.filter(node => 
    node.id !== hub.id && 
    connections.get(node.id).incoming < maxConnections
  );

  if (spokes.length === 0) return null;

  const spoke = spokes[Math.floor(Math.random() * spokes.length)];
  return createEdge(hub.id, spoke.id);
};

const generateMeshEdge = (nodes, connections, maxConnections) => {
  const availableNodes = nodes.filter(node => {
    const conn = connections.get(node.id);
    return conn.outgoing < maxConnections && conn.incoming < maxConnections;
  });

  if (availableNodes.length < 2) return null;

  const source = availableNodes[Math.floor(Math.random() * availableNodes.length)];
  const targets = availableNodes.filter(node => 
    node.id !== source.id && 
    connections.get(node.id).incoming < maxConnections
  );

  if (targets.length === 0) return null;

  // Prefer nearby nodes for mesh pattern
  targets.sort((a, b) => {
    const distA = Math.hypot(a.position.x - source.position.x, a.position.y - source.position.y);
    const distB = Math.hypot(b.position.x - source.position.x, b.position.y - source.position.y);
    return distA - distB;
  });

  const target = targets[Math.floor(Math.random() * Math.min(3, targets.length))];
  return createEdge(source.id, target.id);
};

const generateRandomEdge = (nodes, connections, maxConnections) => {
  const sources = nodes.filter(node => connections.get(node.id).outgoing < maxConnections);
  const targets = nodes.filter(node => connections.get(node.id).incoming < maxConnections);

  if (sources.length === 0 || targets.length === 0) return null;

  const source = sources[Math.floor(Math.random() * sources.length)];
  const availableTargets = targets.filter(node => node.id !== source.id);

  if (availableTargets.length === 0) return null;

  const target = availableTargets[Math.floor(Math.random() * availableTargets.length)];
  return createEdge(source.id, target.id);
};

const createEdge = (sourceId, targetId) => ({
  id: `edge-${sourceId}-${targetId}`,
  source: sourceId,
  target: targetId,
  type: 'smoothstep',
  animated: Math.random() > 0.9,
  style: {
    strokeWidth: Math.random() > 0.8 ? 3 : 2,
    stroke: Math.random() > 0.9 ? '#3b82f6' : '#6b7280'
  }
});

// ========================================
// 2. PERFORMANCE STRESS TESTS
// ========================================

export const runStressTest = async (testConfig) => {
  const {
    nodeCount = 500,
    edgeDensity = 0.3,
    testDuration = 30000, // 30 seconds
    interactions = ['pan', 'zoom', 'select', 'drag'],
    metrics = ['fps', 'memory', 'renderTime']
  } = testConfig;

  console.log(`Starting stress test: ${nodeCount} nodes, ${Math.floor(nodeCount * edgeDensity)} edges`);

  const nodes = generateStressTestNodes(nodeCount);
  const edges = generateStressTestEdges(nodes, { density: edgeDensity });

  const testResults = {
    config: testConfig,
    startTime: performance.now(),
    metrics: {
      fps: [],
      memory: [],
      renderTime: [],
      frameDrops: 0,
      interactions: 0
    },
    errors: []
  };

  // Render the component
  let container;
  try {
    const result = render(
      <PerformanceOptimizedReactFlow
        nodes={nodes}
        edges={edges}
        fitView={false}
      />
    );
    container = result.container;
  } catch (error) {
    testResults.errors.push(`Render error: ${error.message}`);
    return testResults;
  }

  // Start performance monitoring
  const performanceMonitor = startPerformanceMonitoring(testResults.metrics);

  // Run interactions for specified duration
  const interactionInterval = setInterval(() => {
    const interaction = interactions[Math.floor(Math.random() * interactions.length)];
    performInteraction(container, interaction);
    testResults.metrics.interactions++;
  }, 100); // Interaction every 100ms

  // Wait for test duration
  await new Promise(resolve => setTimeout(resolve, testDuration));

  // Cleanup
  clearInterval(interactionInterval);
  performanceMonitor.stop();

  testResults.endTime = performance.now();
  testResults.duration = testResults.endTime - testResults.startTime;

  return generateTestReport(testResults);
};

const startPerformanceMonitoring = (metrics) => {
  let frameCount = 0;
  let lastTime = performance.now();
  let monitoring = true;

  const monitor = () => {
    if (!monitoring) return;

    frameCount++;
    const currentTime = performance.now();

    if (currentTime >= lastTime + 1000) {
      const fps = Math.round((frameCount * 1000) / (currentTime - lastTime));
      metrics.fps.push(fps);

      if (fps < 30) metrics.frameDrops++;

      if (performance.memory) {
        metrics.memory.push(performance.memory.usedJSHeapSize / 1024 / 1024);
      }

      frameCount = 0;
      lastTime = currentTime;
    }

    requestAnimationFrame(monitor);
  };

  monitor();

  return {
    stop: () => { monitoring = false; }
  };
};

const performInteraction = (container, interaction) => {
  const reactFlowElement = container.querySelector('.react-flow');
  if (!reactFlowElement) return;

  try {
    switch (interaction) {
      case 'pan':
        simulatePanning(reactFlowElement);
        break;
      case 'zoom':
        simulateZooming(reactFlowElement);
        break;
      case 'select':
        simulateSelection(container);
        break;
      case 'drag':
        simulateNodeDragging(container);
        break;
      default:
        break;
    }
  } catch (error) {
    console.warn(`Interaction ${interaction} failed:`, error.message);
  }
};

const simulatePanning = (element) => {
  const startX = Math.random() * element.clientWidth;
  const startY = Math.random() * element.clientHeight;
  const deltaX = (Math.random() - 0.5) * 200;
  const deltaY = (Math.random() - 0.5) * 200;

  fireEvent.mouseDown(element, { clientX: startX, clientY: startY });
  fireEvent.mouseMove(element, { clientX: startX + deltaX, clientY: startY + deltaY });
  fireEvent.mouseUp(element);
};

const simulateZooming = (element) => {
  const centerX = element.clientWidth / 2;
  const centerY = element.clientHeight / 2;
  const zoomDelta = (Math.random() - 0.5) * 1000; // Random zoom

  fireEvent.wheel(element, {
    clientX: centerX,
    clientY: centerY,
    deltaY: zoomDelta
  });
};

const simulateSelection = (container) => {
  const nodes = container.querySelectorAll('.max-object-node');
  if (nodes.length === 0) return;

  const randomNode = nodes[Math.floor(Math.random() * nodes.length)];
  fireEvent.click(randomNode);
};

const simulateNodeDragging = (container) => {
  const nodes = container.querySelectorAll('.max-object-node');
  if (nodes.length === 0) return;

  const randomNode = nodes[Math.floor(Math.random() * nodes.length)];
  const rect = randomNode.getBoundingClientRect();
  
  const startX = rect.left + rect.width / 2;
  const startY = rect.top + rect.height / 2;
  const deltaX = (Math.random() - 0.5) * 100;
  const deltaY = (Math.random() - 0.5) * 100;

  fireEvent.mouseDown(randomNode, { clientX: startX, clientY: startY });
  fireEvent.mouseMove(document, { clientX: startX + deltaX, clientY: startY + deltaY });
  fireEvent.mouseUp(document);
};

const generateTestReport = (testResults) => {
  const { metrics, duration, config } = testResults;

  const avgFPS = metrics.fps.length > 0 ? 
    metrics.fps.reduce((sum, fps) => sum + fps, 0) / metrics.fps.length : 0;
  
  const minFPS = metrics.fps.length > 0 ? Math.min(...metrics.fps) : 0;
  
  const avgMemory = metrics.memory.length > 0 ?
    metrics.memory.reduce((sum, mem) => sum + mem, 0) / metrics.memory.length : 0;
  
  const maxMemory = metrics.memory.length > 0 ? Math.max(...metrics.memory) : 0;

  return {
    ...testResults,
    summary: {
      duration: Math.round(duration),
      nodeCount: config.nodeCount,
      edgeCount: Math.floor(config.nodeCount * (config.edgeDensity || 0.3)),
      avgFPS: Math.round(avgFPS * 10) / 10,
      minFPS,
      frameDrops: metrics.frameDrops,
      avgMemoryMB: Math.round(avgMemory * 10) / 10,
      maxMemoryMB: Math.round(maxMemory * 10) / 10,
      totalInteractions: metrics.interactions,
      errors: testResults.errors.length
    },
    passed: avgFPS >= 30 && metrics.frameDrops < 10 && testResults.errors.length === 0
  };
};

// ========================================
// 3. PREDEFINED STRESS TEST SUITES
// ========================================

export const STRESS_TEST_SUITES = {
  small: {
    name: 'Small Patch Stress Test',
    nodeCount: 100,
    edgeDensity: 0.2,
    testDuration: 15000,
    expectedFPS: 60,
    expectedMemory: 100
  },
  
  medium: {
    name: 'Medium Patch Stress Test',
    nodeCount: 200,
    edgeDensity: 0.3,
    testDuration: 30000,
    expectedFPS: 45,
    expectedMemory: 200
  },
  
  large: {
    name: 'Large Patch Stress Test',
    nodeCount: 300,
    edgeDensity: 0.4,
    testDuration: 45000,
    expectedFPS: 30,
    expectedMemory: 400
  },
  
  extreme: {
    name: 'Extreme Patch Stress Test',
    nodeCount: 500,
    edgeDensity: 0.5,
    testDuration: 60000,
    expectedFPS: 20,
    expectedMemory: 600
  }
};

// ========================================
// 4. AUTOMATED TEST RUNNER
// ========================================

export const runAllStressTests = async () => {
  const results = [];
  
  for (const [testName, testConfig] of Object.entries(STRESS_TEST_SUITES)) {
    console.log(`Running ${testConfig.name}...`);
    
    try {
      const result = await runStressTest(testConfig);
      result.testName = testName;
      results.push(result);
      
      console.log(`${testConfig.name} completed:`, result.summary);
      
      // Brief pause between tests
      await new Promise(resolve => setTimeout(resolve, 2000));
    } catch (error) {
      console.error(`${testConfig.name} failed:`, error);
      results.push({
        testName,
        config: testConfig,
        error: error.message,
        passed: false
      });
    }
  }
  
  return results;
};

export default {
  generateStressTestNodes,
  generateStressTestEdges,
  runStressTest,
  runAllStressTests,
  STRESS_TEST_SUITES
};
