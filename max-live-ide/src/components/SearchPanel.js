import React, { useState, useEffect, useMemo } from 'react';
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
  CloseButton
} from '@mantine/core';
import { 
  IconSearch, 
  IconFilter, 
  IconTag, 
  IconChevronRight,
  IconMusic,
  IconWaveSquare,
  IconSettings
} from '@tabler/icons-react';
import './SearchPanel.css';

const SearchPanel = ({
  searchTerm,
  onSearch,
  searchResults,
  onJumpTo,
  onClose,
  nodes
}) => {
  const [localSearchTerm, setLocalSearchTerm] = useState(searchTerm || '');
  const [searchMode, setSearchMode] = useState('objects'); // 'objects', 'signals', 'subpatches'
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [searchHistory, setSearchHistory] = useState([]);
  const [filters, setFilters] = useState({
    objectType: 'all',
    status: 'all',
    tags: []
  });
  
  const searchInputRef = useRef(null);
  const resultsRef = useRef(null);

  // Focus search input when panel opens
  useEffect(() => {
    if (searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, []);

  // Handle search execution
  useEffect(() => {
    const debounceTimer = setTimeout(() => {
      if (localSearchTerm.trim()) {
        onSearch(localSearchTerm);
        
        // Add to search history
        if (!searchHistory.includes(localSearchTerm)) {
          setSearchHistory(prev => [localSearchTerm, ...prev.slice(0, 9)]); // Keep last 10
        }
      }
    }, 300);

    return () => clearTimeout(debounceTimer);
  }, [localSearchTerm, onSearch, searchHistory]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setSelectedIndex(prev => 
            Math.min(prev + 1, searchResults.length - 1)
          );
          break;
        case 'ArrowUp':
          e.preventDefault();
          setSelectedIndex(prev => Math.max(prev - 1, 0));
          break;
        case 'Enter':
          e.preventDefault();
          if (searchResults[selectedIndex]) {
            handleResultClick(searchResults[selectedIndex]);
          }
          break;
        case 'Escape':
          e.preventDefault();
          onClose();
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [selectedIndex, searchResults, onClose]);

  // Scroll selected result into view
  useEffect(() => {
    if (resultsRef.current) {
      const selectedElement = resultsRef.current.children[selectedIndex];
      if (selectedElement) {
        selectedElement.scrollIntoView({
          behavior: 'smooth',
          block: 'nearest'
        });
      }
    }
  }, [selectedIndex]);

  const handleResultClick = (result) => {
    onJumpTo(result.id);
    onClose();
  };

  const handleHistoryClick = (term) => {
    setLocalSearchTerm(term);
    onSearch(term);
  };

  const getFilteredResults = () => {
    let filtered = searchResults;

    // Apply object type filter
    if (filters.objectType !== 'all') {
      filtered = filtered.filter(result => 
        result.data.objectType === filters.objectType
      );
    }

    // Apply status filter
    if (filters.status !== 'all') {
      filtered = filtered.filter(result => 
        result.data.status === filters.status
      );
    }

    // Apply tag filters
    if (filters.tags.length > 0) {
      filtered = filtered.filter(result => 
        result.data.tags && filters.tags.every(tag => 
          result.data.tags.includes(tag)
        )
      );
    }

    return filtered;
  };

  const filteredResults = getFilteredResults();

  const getResultIcon = (result) => {
    switch (result.data.objectType) {
      case 'audio': return '🎵';
      case 'midi': return '🎹';
      case 'live-api': return '🎛️';
      case 'utility': return '🔧';
      default: return '📦';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'connected': return '🟢';
      case 'running': return '🟡';
      case 'error': return '🔴';
      case 'disabled': return '⚫';
      default: return '⚪';
    }
  };

  const highlightMatch = (text, searchTerm) => {
    if (!searchTerm) return text;
    
    const regex = new RegExp(`(${searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
  };

  const getAllTags = () => {
    const tagSet = new Set();
    // Handle case where nodes might be undefined
    if (nodes && Array.isArray(nodes)) {
      nodes.forEach(node => {
        if (node.data && node.data.tags) {
          node.data.tags.forEach(tag => tagSet.add(tag));
        }
      });
    }
    return Array.from(tagSet).sort();
  };

  return (
    <Paper 
      className="search-panel-overlay" 
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.7)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000
      }}
    >
      <Paper 
        shadow="xl"
        radius="md"
        p="lg"
        style={{
          width: '90%',
          maxWidth: 800,
          maxHeight: '80vh',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        {/* Header */}
        <Group justify="space-between" mb="md">
          <Text size="lg" fw={600}>🔍 Search & Navigate</Text>
          <CloseButton onClick={onClose} size="lg" />
        </Group>

        {/* Search Mode Tabs */}
        <Group mb="md">
          <Button
            variant={searchMode === 'objects' ? 'filled' : 'light'}
            size="xs"
            onClick={() => setSearchMode('objects')}
            leftSection={<IconMusic size={14} />}
          >
            Objects
          </Button>
          <Button
            variant={searchMode === 'signals' ? 'filled' : 'light'}
            size="xs"
            onClick={() => setSearchMode('signals')}
            leftSection={<IconWaveSquare size={14} />}
          >
            Signals
          </Button>
          <Button
            variant={searchMode === 'subpatches' ? 'filled' : 'light'}
            size="xs"
            onClick={() => setSearchMode('subpatches')}
            leftSection={<IconSettings size={14} />}
          >
            Subpatches
          </Button>
        </Group>

        {/* Search Input */}
        <Stack mb="md">
          <TextInput
            ref={searchInputRef}
            placeholder={`Search ${searchMode}...`}
            value={localSearchTerm}
            onChange={(e) => setLocalSearchTerm(e.target.value)}
            leftSection={<IconSearch size={16} />}
            size="md"
            styles={{
              input: {
                fontSize: '16px',
              }
            }}
          />
          
          {/* Search History */}
          {searchHistory.length > 0 && (
            <div>
              <Text size="xs" c="dimmed" mb="xs">Recent searches:</Text>
              <Group gap="xs">
                {searchHistory.slice(0, 5).map((term, index) => (
                  <Badge
                    key={index}
                    variant="light"
                    style={{ cursor: 'pointer' }}
                    onClick={() => handleHistoryClick(term)}
                  >
                    {term}
                  </Badge>
                ))}
              </Group>
            </div>
          )}
        </Stack>

        {/* Filters */}
        <Paper p="sm" mb="md" withBorder>
          <Group>
            <div>
              <Text size="xs" c="dimmed" mb="xs">Type:</Text>
              <Button
                variant={filters.objectType === 'all' ? 'filled' : 'light'}
                size="xs"
                onClick={() => setFilters(prev => ({ ...prev, objectType: 'all' }))}
              >
                All
              </Button>
            </div>
            
            <div>
              <Text size="xs" c="dimmed" mb="xs">Tags:</Text>
              <Group gap="xs">
                {getAllTags().slice(0, 6).map(tag => (
                  <Badge
                    key={tag}
                    variant={filters.tags.includes(tag) ? 'filled' : 'light'}
                    style={{ cursor: 'pointer' }}
                    onClick={() => {
                      setFilters(prev => ({
                        ...prev,
                        tags: prev.tags.includes(tag)
                          ? prev.tags.filter(t => t !== tag)
                          : [...prev.tags, tag]
                      }));
                    }}
                    leftSection={<IconTag size={12} />}
                  >
                    {tag}
                  </Badge>
                ))}
              </Group>
            </div>
          </Group>
        </Paper>

        {/* Results */}
        <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          <Group justify="space-between" mb="sm">
            <Text size="sm" c="dimmed">
              {filteredResults.length} of {searchResults.length} results
            </Text>
            {localSearchTerm && (
              <Text size="sm" c="orange">for "{localSearchTerm}"</Text>
            )}
          </Group>

          <ScrollArea flex={1} type="hover">
            <Stack gap="xs">
              {filteredResults.map((result, index) => (
                <Paper
                  key={result.id}
                  p="sm"
                  withBorder
                  style={{
                    cursor: 'pointer',
                    backgroundColor: index === selectedIndex ? 'var(--mantine-color-orange-light)' : undefined,
                    transition: 'background-color 0.2s ease'
                  }}
                  onClick={() => handleResultClick(result)}
                >
                  <Group>
                    <Text size="xl">{getResultIcon(result)}</Text>
                    <div style={{ flex: 1 }}>
                      <Text fw={500} size="sm">
                        <span 
                          dangerouslySetInnerHTML={{
                            __html: highlightMatch(result.data.label, localSearchTerm)
                          }}
                        />
                      </Text>
                      <Group gap="xs" mt="xs">
                        <Badge variant="light" size="xs">{result.data.objectType}</Badge>
                        <Text size="xs" c="dimmed">
                          ({Math.round(result.position.x)}, {Math.round(result.position.y)})
                        </Text>
                        {result.data.tags && result.data.tags.slice(0, 3).map(tag => (
                          <Badge key={tag} variant="outline" size="xs">{tag}</Badge>
                        ))}
                      </Group>
                    </div>
                    <ActionIcon variant="subtle" size="sm">
                      <IconChevronRight size={16} />
                    </ActionIcon>
                    <Text size="lg">{getStatusIcon(result.data.status)}</Text>
                  </Group>
                </Paper>
              ))}

              {filteredResults.length === 0 && localSearchTerm && (
                <Paper p="xl" ta="center">
                  <Text size="xl" mb="sm">🔍</Text>
                  <Text fw={500} mb="xs">
                    No {searchMode} found matching "{localSearchTerm}"
                  </Text>
                  <Text size="sm" c="dimmed">
                    Try adjusting your search term or filters
                  </Text>
                </Paper>
              )}

              {!localSearchTerm && (
                <Paper p="lg" ta="center">
                  <Text size="xl" mb="sm">💡</Text>
                  <Text fw={500} mb="md">Search Tips:</Text>
                  <Stack gap="xs" ta="left" style={{ maxWidth: 400, margin: '0 auto' }}>
                    <Text size="sm">• Type object names: "osc", "gain", "filter"</Text>
                    <Text size="sm">• Search by tags: "audio", "generator", "effect"</Text>
                    <Text size="sm">• Use filters to narrow results</Text>
                    <Text size="sm">• Navigate with ↑↓ keys, Enter to jump</Text>
                  </Stack>
                </Paper>
              )}
            </Stack>
          </ScrollArea>
        </div>

        {/* Keyboard Shortcuts */}
        <Divider mt="md" mb="sm" />
        <Group justify="center" gap="md">
          <Group gap="xs">
            <Kbd>↑↓</Kbd>
            <Text size="xs" c="dimmed">Navigate</Text>
          </Group>
          <Group gap="xs">
            <Kbd>Enter</Kbd>
            <Text size="xs" c="dimmed">Jump to</Text>
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
    </Paper>
  );
};

export default SearchPanel;
