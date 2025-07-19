/**
 * useObjectTemplateBrowser Hook
 * Manages state and functionality for the Object & Template Browser
 */

import { useState, useCallback, useRef, useEffect } from 'react';

// Browser state management
export const useObjectTemplateBrowser = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedTags, setSelectedTags] = useState([]);
  const [favorites, setFavorites] = useState(new Set());
  const [recentlyUsed, setRecentlyUsed] = useState([]);
  const [selectedObject, setSelectedObject] = useState(null);

  // Persistence hooks
  useEffect(() => {
    // Load favorites from localStorage
    const savedFavorites = localStorage.getItem('max-live-ide-favorites');
    if (savedFavorites) {
      try {
        setFavorites(new Set(JSON.parse(savedFavorites)));
      } catch (e) {
        console.warn('Failed to load favorites:', e);
      }
    }

    // Load recently used
    const savedRecent = localStorage.getItem('max-live-ide-recent');
    if (savedRecent) {
      try {
        setRecentlyUsed(JSON.parse(savedRecent));
      } catch (e) {
        console.warn('Failed to load recent items:', e);
      }
    }
  }, []);

  // Save favorites to localStorage
  useEffect(() => {
    localStorage.setItem('max-live-ide-favorites', JSON.stringify([...favorites]));
  }, [favorites]);

  // Save recently used to localStorage  
  useEffect(() => {
    localStorage.setItem('max-live-ide-recent', JSON.stringify(recentlyUsed));
  }, [recentlyUsed]);

  const openBrowser = useCallback(() => {
    setIsOpen(true);
  }, []);

  const closeBrowser = useCallback(() => {
    setIsOpen(false);
    setSearchTerm('');
    setSelectedObject(null);
  }, []);

  const toggleFavorite = useCallback((item) => {
    const key = item.name || item.id;
    setFavorites(prev => {
      const updated = new Set(prev);
      if (updated.has(key)) {
        updated.delete(key);
      } else {
        updated.add(key);
      }
      return updated;
    });
  }, []);

  const addToRecent = useCallback((item) => {
    setRecentlyUsed(prev => {
      const key = item.name || item.id;
      const filtered = prev.filter(recent => (recent.name || recent.id) !== key);
      return [item, ...filtered].slice(0, 10); // Keep last 10
    });
  }, []);

  const clearRecent = useCallback(() => {
    setRecentlyUsed([]);
  }, []);

  const clearFavorites = useCallback(() => {
    setFavorites(new Set());
  }, []);

  const search = useCallback((term) => {
    setSearchTerm(term);
  }, []);

  const filterByCategory = useCallback((category) => {
    setSelectedCategory(category);
  }, []);

  const filterByTags = useCallback((tags) => {
    setSelectedTags(tags);
  }, []);

  const clearFilters = useCallback(() => {
    setSearchTerm('');
    setSelectedCategory('all');
    setSelectedTags([]);
  }, []);

  return {
    // State
    isOpen,
    searchTerm,
    selectedCategory,
    selectedTags,
    favorites,
    recentlyUsed,
    selectedObject,

    // Actions
    openBrowser,
    closeBrowser,
    toggleFavorite,
    addToRecent,
    clearRecent,
    clearFavorites,
    search,
    filterByCategory,
    filterByTags,
    clearFilters,
    setSelectedObject
  };
};

// Keyboard shortcuts hook
export const useObjectBrowserShortcuts = (browserControls) => {
  useEffect(() => {
    const handleKeyDown = (event) => {
      // Ctrl/Cmd + Shift + O to open browser
      if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'O') {
        event.preventDefault();
        browserControls.openBrowser();
      }

      // Escape to close browser
      if (event.key === 'Escape' && browserControls.isOpen) {
        event.preventDefault();
        browserControls.closeBrowser();
      }

      // Ctrl/Cmd + F to focus search when browser is open
      if ((event.ctrlKey || event.metaKey) && event.key === 'f' && browserControls.isOpen) {
        event.preventDefault();
        // Focus will be handled by the browser component
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [browserControls]);
};

// Object insertion hook for React Flow
export const useObjectInsertion = (setNodes, setEdges) => {
  const insertObject = useCallback((object, position = null) => {
    const newNode = {
      id: `${object.name || object.id}-${Date.now()}`,
      type: 'maxObject',
      position: position || { 
        x: Math.random() * 400 + 100, 
        y: Math.random() * 400 + 100 
      },
      data: {
        label: object.name,
        objectType: object.category,
        status: 'ready',
        tags: object.tags || [],
        inlets: object.inlets || 1,
        outlets: object.outlets || 1,
        parameters: object.parameters || [],
        usage: object.usage,
        example: object.example,
        description: object.description
      }
    };

    setNodes(nodes => [...nodes, newNode]);
    return newNode;
  }, [setNodes]);

  const insertTemplate = useCallback((template, position = null) => {
    if (!template.patch) {
      console.warn('Template has no patch data:', template);
      return;
    }

    const basePosition = position || { x: 100, y: 100 };
    const timestamp = Date.now();

    // Insert nodes with updated IDs and positions
    const newNodes = template.patch.nodes.map((node, index) => ({
      ...node,
      id: `${node.id}-${timestamp}`,
      position: {
        x: basePosition.x + node.position.x,
        y: basePosition.y + node.position.y
      }
    }));

    // Insert edges with updated node references
    const newEdges = template.patch.edges.map((edge, index) => ({
      ...edge,
      id: `${edge.id}-${timestamp}`,
      source: `${edge.source}-${timestamp}`,
      target: `${edge.target}-${timestamp}`
    }));

    setNodes(nodes => [...nodes, ...newNodes]);
    setEdges(edges => [...edges, ...newEdges]);
    
    return { nodes: newNodes, edges: newEdges };
  }, [setNodes, setEdges]);

  return {
    insertObject,
    insertTemplate
  };
};

// Search and filtering utilities
export const createObjectSearchFilter = () => {
  const filterObjects = (objects, { searchTerm, category, tags, difficulty }) => {
    let filtered = objects;

    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      filtered = filtered.filter(obj => 
        obj.name.toLowerCase().includes(search) ||
        obj.description.toLowerCase().includes(search) ||
        obj.tags?.some(tag => tag.toLowerCase().includes(search)) ||
        obj.category.toLowerCase().includes(search) ||
        obj.type?.toLowerCase().includes(search)
      );
    }

    if (category && category !== 'all') {
      filtered = filtered.filter(obj => obj.category === category);
    }

    if (tags && tags.length > 0) {
      filtered = filtered.filter(obj => 
        tags.some(tag => obj.tags?.includes(tag))
      );
    }

    if (difficulty && difficulty.length > 0) {
      filtered = filtered.filter(obj => 
        difficulty.includes(obj.difficulty)
      );
    }

    return filtered;
  };

  const sortObjects = (objects, sortBy = 'name') => {
    return [...objects].sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'category':
          return a.category.localeCompare(b.category);
        case 'difficulty':
          const difficultyOrder = { beginner: 1, intermediate: 2, advanced: 3 };
          return (difficultyOrder[a.difficulty] || 0) - (difficultyOrder[b.difficulty] || 0);
        case 'popularity':
          // Could be based on usage statistics
          return (b.usageCount || 0) - (a.usageCount || 0);
        default:
          return 0;
      }
    });
  };

  return { filterObjects, sortObjects };
};

// Analytics and usage tracking
export const useObjectAnalytics = () => {
  const [analytics, setAnalytics] = useState({
    searches: [],
    objectUsage: {},
    templateUsage: {},
    categoryPreferences: {}
  });

  const trackSearch = useCallback((searchTerm, resultCount) => {
    setAnalytics(prev => ({
      ...prev,
      searches: [...prev.searches, {
        term: searchTerm,
        resultCount,
        timestamp: Date.now()
      }].slice(-100) // Keep last 100 searches
    }));
  }, []);

  const trackObjectUsage = useCallback((objectName) => {
    setAnalytics(prev => ({
      ...prev,
      objectUsage: {
        ...prev.objectUsage,
        [objectName]: (prev.objectUsage[objectName] || 0) + 1
      }
    }));
  }, []);

  const trackTemplateUsage = useCallback((templateId) => {
    setAnalytics(prev => ({
      ...prev,
      templateUsage: {
        ...prev.templateUsage,
        [templateId]: (prev.templateUsage[templateId] || 0) + 1
      }
    }));
  }, []);

  const trackCategoryPreference = useCallback((category) => {
    setAnalytics(prev => ({
      ...prev,
      categoryPreferences: {
        ...prev.categoryPreferences,
        [category]: (prev.categoryPreferences[category] || 0) + 1
      }
    }));
  }, []);

  const getPopularObjects = useCallback((limit = 10) => {
    return Object.entries(analytics.objectUsage)
      .sort(([,a], [,b]) => b - a)
      .slice(0, limit)
      .map(([name, count]) => ({ name, count }));
  }, [analytics.objectUsage]);

  const getPopularSearches = useCallback((limit = 10) => {
    const searchCounts = analytics.searches.reduce((acc, search) => {
      acc[search.term] = (acc[search.term] || 0) + 1;
      return acc;
    }, {});

    return Object.entries(searchCounts)
      .sort(([,a], [,b]) => b - a)
      .slice(0, limit)
      .map(([term, count]) => ({ term, count }));
  }, [analytics.searches]);

  return {
    analytics,
    trackSearch,
    trackObjectUsage,
    trackTemplateUsage,
    trackCategoryPreference,
    getPopularObjects,
    getPopularSearches
  };
};

export default useObjectTemplateBrowser;
