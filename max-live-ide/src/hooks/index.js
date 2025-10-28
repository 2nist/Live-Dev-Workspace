import { useState, useEffect, useCallback, useRef } from 'react';

/**
 * Custom hook for canvas navigation and viewport management
 * Provides smooth transitions, zoom controls, and keyboard shortcuts
 */
export const useCanvasNavigation = (initialViewport = { x: 0, y: 0, zoom: 1 }) => {
  const [viewport, setViewport] = useState(initialViewport);
  const [isAnimating, setIsAnimating] = useState(false);
  const animationRef = useRef(null);

  // Smooth viewport transition
  const animateToViewport = useCallback((targetViewport, duration = 500) => {
    const startViewport = { ...viewport };
    const startTime = Date.now();
    setIsAnimating(true);

    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Easing function for smooth animation
      const easeOutCubic = 1 - Math.pow(1 - progress, 3);
      
      const currentViewport = {
        x: startViewport.x + (targetViewport.x - startViewport.x) * easeOutCubic,
        y: startViewport.y + (targetViewport.y - startViewport.y) * easeOutCubic,
        zoom: startViewport.zoom + (targetViewport.zoom - startViewport.zoom) * easeOutCubic
      };

      setViewport(currentViewport);

      if (progress < 1) {
        animationRef.current = requestAnimationFrame(animate);
      } else {
        setIsAnimating(false);
      }
    };

    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
    
    animationRef.current = requestAnimationFrame(animate);
  }, [viewport]);

  // Jump to specific node
  const jumpToNode = useCallback((nodeId, nodes, animate = true) => {
    const node = nodes.find(n => n.id === nodeId);
    if (!node) return;

    const targetViewport = {
      x: -node.position.x * viewport.zoom + window.innerWidth / 2,
      y: -node.position.y * viewport.zoom + window.innerHeight / 2,
      zoom: viewport.zoom
    };

    if (animate) {
      animateToViewport(targetViewport);
    } else {
      setViewport(targetViewport);
    }
  }, [viewport.zoom, animateToViewport]);

  // Fit all nodes in view
  const fitView = useCallback((nodes, padding = 100, animate = true) => {
    if (!nodes || nodes.length === 0) return;

    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    
    nodes.forEach(node => {
      minX = Math.min(minX, node.position.x);
      minY = Math.min(minY, node.position.y);
      maxX = Math.max(maxX, node.position.x + (node.width || 150));
      maxY = Math.max(maxY, node.position.y + (node.height || 100));
    });

    const contentWidth = maxX - minX + padding * 2;
    const contentHeight = maxY - minY + padding * 2;
    
    const scaleX = window.innerWidth / contentWidth;
    const scaleY = window.innerHeight / contentHeight;
    const newZoom = Math.min(scaleX, scaleY, 1.5); // Max zoom of 1.5x

    const centerX = (minX + maxX) / 2;
    const centerY = (minY + maxY) / 2;

    const targetViewport = {
      x: -centerX * newZoom + window.innerWidth / 2,
      y: -centerY * newZoom + window.innerHeight / 2,
      zoom: newZoom
    };

    if (animate) {
      animateToViewport(targetViewport);
    } else {
      setViewport(targetViewport);
    }
  }, [animateToViewport]);

  // Zoom controls
  const zoomIn = useCallback((factor = 1.2, animate = true) => {
    const newZoom = Math.min(viewport.zoom * factor, 3);
    const targetViewport = { ...viewport, zoom: newZoom };
    
    if (animate) {
      animateToViewport(targetViewport, 200);
    } else {
      setViewport(targetViewport);
    }
  }, [viewport, animateToViewport]);

  const zoomOut = useCallback((factor = 0.8, animate = true) => {
    const newZoom = Math.max(viewport.zoom * factor, 0.1);
    const targetViewport = { ...viewport, zoom: newZoom };
    
    if (animate) {
      animateToViewport(targetViewport, 200);
    } else {
      setViewport(targetViewport);
    }
  }, [viewport, animateToViewport]);

  const resetZoom = useCallback((animate = true) => {
    const targetViewport = { x: 0, y: 0, zoom: 1 };
    
    if (animate) {
      animateToViewport(targetViewport);
    } else {
      setViewport(targetViewport);
    }
  }, [animateToViewport]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Skip if user is typing in an input
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

      switch (e.key) {
        case '=':
        case '+':
          if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            zoomIn();
          }
          break;
        case '-':
          if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            zoomOut();
          }
          break;
        case '0':
          if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            resetZoom();
          }
          break;
        case 'f':
          if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            // This will be handled by the search panel
          }
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [zoomIn, zoomOut, resetZoom]);

  // Cleanup animation on unmount
  useEffect(() => {
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  return {
    viewport,
    setViewport,
    isAnimating,
    jumpToNode,
    fitView,
    zoomIn,
    zoomOut,
    resetZoom,
    animateToViewport
  };
};

/**
 * Custom hook for device search and filtering
 * Provides fuzzy search, filtering, and result management
 */
export const useDeviceSearch = (nodes = [], edges = []) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searchHistory, setSearchHistory] = useState([]);
  const [filters, setFilters] = useState({
    objectType: 'all',
    status: 'all',
    tags: []
  });

  // Fuzzy search implementation
  const fuzzyMatch = useCallback((text, pattern) => {
    if (!pattern) return { score: 1, indices: [] };
    
    const textLower = text.toLowerCase();
    const patternLower = pattern.toLowerCase();
    
    let score = 0;
    let indices = [];
    let patternIndex = 0;
    
    for (let i = 0; i < textLower.length && patternIndex < patternLower.length; i++) {
      if (textLower[i] === patternLower[patternIndex]) {
        indices.push(i);
        score += 1;
        patternIndex++;
      }
    }
    
    if (patternIndex === patternLower.length) {
      // Bonus for consecutive matches
      let consecutiveBonus = 0;
      for (let i = 1; i < indices.length; i++) {
        if (indices[i] === indices[i-1] + 1) {
          consecutiveBonus++;
        }
      }
      
      // Bonus for early matches
      const earlyBonus = Math.max(0, 10 - indices[0]);
      
      score = (score / pattern.length) + (consecutiveBonus * 0.1) + (earlyBonus * 0.01);
      return { score, indices };
    }
    
    return { score: 0, indices: [] };
  }, []);

  // Search function
  const performSearch = useCallback((term, mode = 'objects') => {
    if (!term.trim()) {
      setSearchResults([]);
      return;
    }

    let results = [];

    switch (mode) {
      case 'objects':
        results = nodes.map(node => {
          const labelMatch = fuzzyMatch(node.data.label || '', term);
          const typeMatch = fuzzyMatch(node.data.objectType || '', term);
          const tagMatch = node.data.tags ? 
            Math.max(...node.data.tags.map(tag => fuzzyMatch(tag, term).score)) : 0;
          
          const bestScore = Math.max(labelMatch.score, typeMatch.score, tagMatch);
          
          return {
            ...node,
            searchScore: bestScore,
            matchIndices: labelMatch.score >= typeMatch.score ? labelMatch.indices : []
          };
        }).filter(node => node.searchScore > 0);
        break;

      case 'signals':
        // Search through edges/connections
        results = edges.map(edge => {
          const labelMatch = fuzzyMatch(edge.label || '', term);
          const typeMatch = fuzzyMatch(edge.type || '', term);
          
          return {
            ...edge,
            searchScore: Math.max(labelMatch.score, typeMatch.score),
            matchIndices: labelMatch.indices
          };
        }).filter(edge => edge.searchScore > 0);
        break;

      case 'subpatches':
        // Search for nodes that contain subpatches
        results = nodes.filter(node => 
          node.data.hasSubpatch || node.data.objectType === 'subpatch'
        ).map(node => {
          const labelMatch = fuzzyMatch(node.data.label || '', term);
          return {
            ...node,
            searchScore: labelMatch.score,
            matchIndices: labelMatch.indices
          };
        }).filter(node => node.searchScore > 0);
        break;
    }

    // Sort by score (descending)
    results.sort((a, b) => b.searchScore - a.searchScore);
    
    // Apply filters
    let filteredResults = results;

    if (filters.objectType !== 'all') {
      filteredResults = filteredResults.filter(item => 
        item.data?.objectType === filters.objectType
      );
    }

    if (filters.status !== 'all') {
      filteredResults = filteredResults.filter(item => 
        item.data?.status === filters.status
      );
    }

    if (filters.tags.length > 0) {
      filteredResults = filteredResults.filter(item => 
        item.data?.tags && filters.tags.every(tag => 
          item.data.tags.includes(tag)
        )
      );
    }

    setSearchResults(filteredResults);

    // Add to search history
    if (term.trim() && !searchHistory.includes(term)) {
      setSearchHistory(prev => [term, ...prev.slice(0, 9)]); // Keep last 10
    }
  }, [nodes, edges, filters, fuzzyMatch, searchHistory]);

  // Debounced search
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (searchTerm) {
        performSearch(searchTerm);
      }
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchTerm, performSearch]);

  // Get available filter options
  const getFilterOptions = useCallback(() => {
    const objectTypes = new Set();
    const statuses = new Set();
    const tags = new Set();

    nodes.forEach(node => {
      if (node.data?.objectType) objectTypes.add(node.data.objectType);
      if (node.data?.status) statuses.add(node.data.status);
      if (node.data?.tags) {
        node.data.tags.forEach(tag => tags.add(tag));
      }
    });

    return {
      objectTypes: Array.from(objectTypes).sort(),
      statuses: Array.from(statuses).sort(),
      tags: Array.from(tags).sort()
    };
  }, [nodes]);

  // Clear search
  const clearSearch = useCallback(() => {
    setSearchTerm('');
    setSearchResults([]);
  }, []);

  // Search suggestions based on current content
  const getSearchSuggestions = useCallback(() => {
    const suggestions = new Set();

    // Add common object types
    nodes.forEach(node => {
      if (node.data?.objectType) suggestions.add(node.data.objectType);
      if (node.data?.tags) {
        node.data.tags.forEach(tag => suggestions.add(tag));
      }
    });

    return Array.from(suggestions).slice(0, 8);
  }, [nodes]);

  return {
    searchTerm,
    setSearchTerm,
    searchResults,
    searchHistory,
    filters,
    setFilters,
    performSearch,
    clearSearch,
    getFilterOptions,
    getSearchSuggestions
  };
};

/**
 * Custom hook for Live status monitoring
 * Provides real-time connection status, performance metrics, and device monitoring
 */
export const useLiveStatus = (webSocketUrl = 'ws://localhost:8080', httpUrl = 'http://localhost:8081') => {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionState, setConnectionState] = useState('disconnected'); // 'connecting', 'connected', 'disconnected', 'error'
  const [liveStatus, setLiveStatus] = useState({
    isPlaying: false,
    currentTime: 0,
    tempo: 120,
    timeSignature: [4, 4],
    isRecording: false,
    isOverdubbing: false
  });
  const [deviceStatuses, setDeviceStatuses] = useState(new Map());
  const [performanceMetrics, setPerformanceMetrics] = useState({
    latency: 0,
    cpuUsage: 0,
    memoryUsage: 0,
    messageRate: 0
  });
  const [errorLog, setErrorLog] = useState([]);
  
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  // WebSocket connection management
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    setConnectionState('connecting');
    
    try {
      wsRef.current = new WebSocket(webSocketUrl);

      wsRef.current.onopen = () => {
        console.log('Connected to Ableton Live');
        setIsConnected(true);
        setConnectionState('connected');
        reconnectAttempts.current = 0;
        
        // Request initial status
        wsRef.current.send(JSON.stringify({
          type: 'request_status'
        }));
      };

      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleLiveMessage(data);
        } catch (error) {
          console.error('Error parsing Live message:', error);
          addError('Message parsing error', error.message);
        }
      };

      wsRef.current.onclose = () => {
        // Only log on first disconnect
        if (isConnected) {
          console.log('Disconnected from Ableton Live');
        }
        setIsConnected(false);
        setConnectionState('disconnected');
        
        // Attempt reconnection with backoff
        if (reconnectAttempts.current < maxReconnectAttempts) {
          reconnectAttempts.current++;
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 10000);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        } else if (reconnectAttempts.current === maxReconnectAttempts) {
          console.log('ℹ️ Live WebSocket unavailable. IDE running in standalone mode.');
        }
      };

      wsRef.current.onerror = (error) => {
        // Suppress noisy errors when Live is not running
        if (reconnectAttempts.current === 0) {
          console.warn('⚠️ Ableton Live WebSocket not available (this is normal if Live is not running)');
        }
        setConnectionState('error');
        // Don't add error to log on every failed reconnect
        if (reconnectAttempts.current === 0) {
          addError('WebSocket error', 'Live connection unavailable');
        }
      };

    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      setConnectionState('error');
      addError('Connection error', error.message);
    }
  }, [webSocketUrl]);

  // Handle incoming Live messages
  const handleLiveMessage = useCallback((data) => {
    switch (data.type) {
      case 'status_update':
        setLiveStatus(prev => ({ ...prev, ...data.status }));
        break;
        
      case 'device_status':
        setDeviceStatuses(prev => {
          const newMap = new Map(prev);
          newMap.set(data.deviceId, {
            status: data.status,
            lastUpdate: Date.now(),
            ...data.details
          });
          return newMap;
        });
        break;
        
      case 'performance_metrics':
        setPerformanceMetrics(prev => ({ ...prev, ...data.metrics }));
        break;
        
      case 'error':
        addError('Live Error', data.message, data.details);
        break;
        
      default:
        console.log('Unknown message type:', data.type);
    }
  }, []);

  // Add error to log
  const addError = useCallback((type, message, details = null) => {
    setErrorLog(prev => [{
      id: Date.now(),
      type,
      message,
      details,
      timestamp: new Date().toISOString()
    }, ...prev.slice(0, 99)]); // Keep last 100 errors
  }, []);

  // HTTP API calls
  const sendLiveCommand = useCallback(async (command, params = {}) => {
    try {
      const response = await fetch(`${httpUrl}/api/command`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ command, params })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to send Live command:', error);
      addError('Command Error', `Failed to send ${command}: ${error.message}`);
      throw error;
    }
  }, [httpUrl, addError]);

  // Transport controls
  const playPause = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'transport',
        action: liveStatus.isPlaying ? 'stop' : 'play'
      }));
    }
  }, [liveStatus.isPlaying]);

  const stop = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'transport',
        action: 'stop'
      }));
    }
  }, []);

  const record = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'transport',
        action: 'record'
      }));
    }
  }, []);

  // Device control
  const updateDeviceStatus = useCallback((deviceId, status) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'device_control',
        deviceId,
        action: 'set_status',
        status
      }));
    }
  }, []);

  // Get device status
  const getDeviceStatus = useCallback((deviceId) => {
    return deviceStatuses.get(deviceId) || { status: 'unknown', lastUpdate: null };
  }, [deviceStatuses]);

  // Clear error log
  const clearErrors = useCallback(() => {
    setErrorLog([]);
  }, []);

  // Connect on mount
  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  // Performance monitoring
  useEffect(() => {
    const interval = setInterval(() => {
      if (isConnected && wsRef.current?.readyState === WebSocket.OPEN) {
        const startTime = Date.now();
        
        wsRef.current.send(JSON.stringify({
          type: 'ping',
          timestamp: startTime
        }));

        // Calculate message rate
        setPerformanceMetrics(prev => ({
          ...prev,
          messageRate: prev.messageRate * 0.9 + 0.1 // Simple moving average
        }));
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [isConnected]);

  return {
    isConnected,
    connectionState,
    liveStatus,
    deviceStatuses,
    performanceMetrics,
    errorLog,
    connect,
    playPause,
    stop,
    record,
    updateDeviceStatus,
    getDeviceStatus,
    sendLiveCommand,
    clearErrors,
    addError
  };
};
