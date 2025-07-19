/**
 * State Management Service - Redux-powered real-time state synchronization
 * Professional-grade state management with persistence and sync
 */

const { configureStore, createSlice, createAsyncThunk } = require('@reduxjs/toolkit');
const WebSocket = require('ws');
const EventEmitter = require('events');
const fs = require('fs').promises;
const path = require('path');

// Patch state slice
const patchSlice = createSlice({
    name: 'patch',
    initialState: {
        currentPatch: null,
        patches: {},
        history: [],
        isDirty: false,
        isLoading: false,
        error: null,
        collaborators: {},
        version: 0
    },
    reducers: {
        setPatch: (state, action) => {
            state.currentPatch = action.payload;
            state.isDirty = false;
            state.version += 1;
        },
        updatePatch: (state, action) => {
            if (state.currentPatch) {
                Object.assign(state.currentPatch, action.payload);
                state.isDirty = true;
                state.version += 1;
            }
        },
        addPatchObject: (state, action) => {
            if (state.currentPatch?.objects) {
                state.currentPatch.objects.push(action.payload);
                state.isDirty = true;
                state.version += 1;
            }
        },
        removePatchObject: (state, action) => {
            if (state.currentPatch?.objects) {
                state.currentPatch.objects = state.currentPatch.objects.filter(
                    obj => obj.id !== action.payload
                );
                state.isDirty = true;
                state.version += 1;
            }
        },
        updatePatchObject: (state, action) => {
            if (state.currentPatch?.objects) {
                const index = state.currentPatch.objects.findIndex(
                    obj => obj.id === action.payload.id
                );
                if (index !== -1) {
                    state.currentPatch.objects[index] = action.payload;
                    state.isDirty = true;
                    state.version += 1;
                }
            }
        },
        addConnection: (state, action) => {
            if (state.currentPatch?.connections) {
                state.currentPatch.connections.push(action.payload);
                state.isDirty = true;
                state.version += 1;
            }
        },
        removeConnection: (state, action) => {
            if (state.currentPatch?.connections) {
                state.currentPatch.connections = state.currentPatch.connections.filter(
                    conn => conn.id !== action.payload
                );
                state.isDirty = true;
                state.version += 1;
            }
        },
        pushHistory: (state, action) => {
            state.history.push({
                action: action.payload,
                timestamp: Date.now(),
                version: state.version,
                state: JSON.parse(JSON.stringify(state.currentPatch))
            });
            
            // Keep only last 100 history entries
            if (state.history.length > 100) {
                state.history = state.history.slice(-100);
            }
        },
        undo: (state) => {
            if (state.history.length > 0) {
                const lastState = state.history.pop();
                state.currentPatch = lastState.state;
                state.version = lastState.version;
                state.isDirty = true;
            }
        },
        setCollaborator: (state, action) => {
            state.collaborators[action.payload.id] = action.payload;
        },
        removeCollaborator: (state, action) => {
            delete state.collaborators[action.payload];
        },
        setLoading: (state, action) => {
            state.isLoading = action.payload;
        },
        setError: (state, action) => {
            state.error = action.payload;
        },
        clearError: (state) => {
            state.error = null;
        }
    }
});

// Live state slice
const liveSlice = createSlice({
    name: 'live',
    initialState: {
        isConnected: false,
        transport: {
            isPlaying: false,
            tempo: 120,
            position: 0,
            loopStart: 0,
            loopEnd: 0,
            isLooping: false
        },
        tracks: [],
        devices: [],
        parameters: {},
        scenes: [],
        isRecording: false,
        error: null
    },
    reducers: {
        setConnectionStatus: (state, action) => {
            state.isConnected = action.payload;
        },
        updateTransport: (state, action) => {
            Object.assign(state.transport, action.payload);
        },
        setTracks: (state, action) => {
            state.tracks = action.payload;
        },
        updateTrack: (state, action) => {
            const index = state.tracks.findIndex(track => track.id === action.payload.id);
            if (index !== -1) {
                state.tracks[index] = action.payload;
            }
        },
        setDevices: (state, action) => {
            state.devices = action.payload;
        },
        updateDevice: (state, action) => {
            const index = state.devices.findIndex(device => device.id === action.payload.id);
            if (index !== -1) {
                state.devices[index] = action.payload;
            }
        },
        updateParameter: (state, action) => {
            state.parameters[action.payload.id] = action.payload;
        },
        setScenes: (state, action) => {
            state.scenes = action.payload;
        },
        setRecording: (state, action) => {
            state.isRecording = action.payload;
        },
        setLiveError: (state, action) => {
            state.error = action.payload;
        }
    }
});

// UI state slice
const uiSlice = createSlice({
    name: 'ui',
    initialState: {
        selectedObjects: [],
        clipboard: null,
        zoom: 1.0,
        panX: 0,
        panY: 0,
        gridSize: 20,
        snapToGrid: true,
        showGrid: true,
        theme: 'dark',
        sidebarCollapsed: false,
        inspectorVisible: true,
        browserVisible: false,
        consoleVisible: false,
        isMobile: false,
        touchMode: false,
        modifiers: {
            shift: false,
            ctrl: false,
            alt: false
        }
    },
    reducers: {
        selectObjects: (state, action) => {
            state.selectedObjects = action.payload;
        },
        addSelection: (state, action) => {
            if (!state.selectedObjects.includes(action.payload)) {
                state.selectedObjects.push(action.payload);
            }
        },
        removeSelection: (state, action) => {
            state.selectedObjects = state.selectedObjects.filter(id => id !== action.payload);
        },
        clearSelection: (state) => {
            state.selectedObjects = [];
        },
        setClipboard: (state, action) => {
            state.clipboard = action.payload;
        },
        setZoom: (state, action) => {
            state.zoom = Math.max(0.1, Math.min(5.0, action.payload));
        },
        setPan: (state, action) => {
            state.panX = action.payload.x;
            state.panY = action.payload.y;
        },
        setGridSize: (state, action) => {
            state.gridSize = action.payload;
        },
        toggleSnapToGrid: (state) => {
            state.snapToGrid = !state.snapToGrid;
        },
        toggleGrid: (state) => {
            state.showGrid = !state.showGrid;
        },
        setTheme: (state, action) => {
            state.theme = action.payload;
        },
        toggleSidebar: (state) => {
            state.sidebarCollapsed = !state.sidebarCollapsed;
        },
        toggleInspector: (state) => {
            state.inspectorVisible = !state.inspectorVisible;
        },
        toggleBrowser: (state) => {
            state.browserVisible = !state.browserVisible;
        },
        toggleConsole: (state) => {
            state.consoleVisible = !state.consoleVisible;
        },
        setMobileMode: (state, action) => {
            state.isMobile = action.payload;
        },
        setTouchMode: (state, action) => {
            state.touchMode = action.payload;
        },
        setModifiers: (state, action) => {
            Object.assign(state.modifiers, action.payload);
        }
    }
});

// Templates state slice  
const templatesSlice = createSlice({
    name: 'templates',
    initialState: {
        categories: [],
        templates: {},
        favorites: [],
        recentlyUsed: [],
        searchResults: [],
        isLoading: false,
        error: null
    },
    reducers: {
        setCategories: (state, action) => {
            state.categories = action.payload;
        },
        setTemplates: (state, action) => {
            state.templates = action.payload;
        },
        addTemplate: (state, action) => {
            const template = action.payload;
            if (!state.templates[template.category]) {
                state.templates[template.category] = [];
            }
            state.templates[template.category].push(template);
        },
        toggleFavorite: (state, action) => {
            const templateId = action.payload;
            if (state.favorites.includes(templateId)) {
                state.favorites = state.favorites.filter(id => id !== templateId);
            } else {
                state.favorites.push(templateId);
            }
        },
        addToRecentlyUsed: (state, action) => {
            const templateId = action.payload;
            state.recentlyUsed = [
                templateId,
                ...state.recentlyUsed.filter(id => id !== templateId)
            ].slice(0, 20); // Keep only 20 recent items
        },
        setSearchResults: (state, action) => {
            state.searchResults = action.payload;
        },
        setTemplatesLoading: (state, action) => {
            state.isLoading = action.payload;
        },
        setTemplatesError: (state, action) => {
            state.error = action.payload;
        }
    }
});

// AI state slice
const aiSlice = createSlice({
    name: 'ai',
    initialState: {
        suggestions: [],
        isAnalyzing: false,
        patterns: [],
        optimizations: [],
        chatHistory: [],
        isEnabled: true,
        confidence: 0,
        lastAnalysis: null
    },
    reducers: {
        setSuggestions: (state, action) => {
            state.suggestions = action.payload;
        },
        addSuggestion: (state, action) => {
            state.suggestions.push(action.payload);
        },
        removeSuggestion: (state, action) => {
            state.suggestions = state.suggestions.filter(s => s.id !== action.payload);
        },
        setAnalyzing: (state, action) => {
            state.isAnalyzing = action.payload;
        },
        setPatterns: (state, action) => {
            state.patterns = action.payload;
        },
        setOptimizations: (state, action) => {
            state.optimizations = action.payload;
        },
        addChatMessage: (state, action) => {
            state.chatHistory.push({
                ...action.payload,
                timestamp: Date.now()
            });
        },
        clearChatHistory: (state) => {
            state.chatHistory = [];
        },
        setAIEnabled: (state, action) => {
            state.isEnabled = action.payload;
        },
        setConfidence: (state, action) => {
            state.confidence = action.payload;
        },
        setLastAnalysis: (state, action) => {
            state.lastAnalysis = action.payload;
        }
    }
});

class StateManager extends EventEmitter {
    constructor(options = {}) {
        super();
        
        this.options = {
            persistPath: path.join(process.cwd(), 'data', 'state'),
            syncInterval: 1000,
            maxHistorySize: 1000,
            ...options
        };

        this.store = configureStore({
            reducer: {
                patch: patchSlice.reducer,
                live: liveSlice.reducer,
                ui: uiSlice.reducer,
                templates: templatesSlice.reducer,
                ai: aiSlice.reducer
            },
            middleware: (getDefaultMiddleware) =>
                getDefaultMiddleware({
                    serializableCheck: {
                        ignoredActions: ['persist/PERSIST']
                    }
                }),
            devTools: process.env.NODE_ENV === 'development'
        });

        this.clients = new Map();
        this.lastState = null;
        this.syncTimer = null;
        
        this.setupStateSync();
        this.loadPersistedState();
    }

    setupStateSync() {
        // Listen to state changes
        this.store.subscribe(() => {
            const currentState = this.store.getState();
            
            // Check if state actually changed
            if (JSON.stringify(currentState) !== JSON.stringify(this.lastState)) {
                this.lastState = { ...currentState };
                this.emit('state-changed', currentState);
                
                // Sync to connected clients
                this.syncToClients(currentState);
                
                // Debounced persistence
                this.scheduleStatePersistence();
            }
        });
    }

    syncToClients(state) {
        const syncMessage = {
            type: 'state-sync',
            state,
            timestamp: Date.now()
        };

        this.clients.forEach((client, clientId) => {
            if (client.readyState === WebSocket.OPEN) {
                client.send(JSON.stringify(syncMessage));
            } else {
                this.clients.delete(clientId);
            }
        });
    }

    scheduleStatePersistence() {
        if (this.syncTimer) {
            clearTimeout(this.syncTimer);
        }
        
        this.syncTimer = setTimeout(() => {
            this.persistState();
        }, this.options.syncInterval);
    }

    async persistState() {
        try {
            const state = this.store.getState();
            const persistData = {
                patch: state.patch,
                ui: {
                    theme: state.ui.theme,
                    zoom: state.ui.zoom,
                    panX: state.ui.panX,
                    panY: state.ui.panY,
                    gridSize: state.ui.gridSize,
                    snapToGrid: state.ui.snapToGrid,
                    showGrid: state.ui.showGrid
                },
                templates: {
                    favorites: state.templates.favorites,
                    recentlyUsed: state.templates.recentlyUsed
                },
                ai: {
                    isEnabled: state.ai.isEnabled,
                    chatHistory: state.ai.chatHistory.slice(-50) // Keep last 50 messages
                },
                timestamp: Date.now()
            };

            await fs.mkdir(path.dirname(this.options.persistPath), { recursive: true });
            await fs.writeFile(
                this.options.persistPath + '.json',
                JSON.stringify(persistData, null, 2)
            );
            
            console.log('State persisted successfully');
        } catch (error) {
            console.error('Failed to persist state:', error);
        }
    }

    async loadPersistedState() {
        try {
            const data = await fs.readFile(this.options.persistPath + '.json', 'utf8');
            const persistedState = JSON.parse(data);
            
            // Restore persisted state
            if (persistedState.patch) {
                this.store.dispatch(patchSlice.actions.setPatch(persistedState.patch.currentPatch));
            }
            
            if (persistedState.ui) {
                Object.entries(persistedState.ui).forEach(([key, value]) => {
                    if (key === 'theme') this.store.dispatch(uiSlice.actions.setTheme(value));
                    if (key === 'zoom') this.store.dispatch(uiSlice.actions.setZoom(value));
                    if (key === 'panX' || key === 'panY') {
                        this.store.dispatch(uiSlice.actions.setPan({
                            x: persistedState.ui.panX || 0,
                            y: persistedState.ui.panY || 0
                        }));
                    }
                    if (key === 'gridSize') this.store.dispatch(uiSlice.actions.setGridSize(value));
                });
            }
            
            if (persistedState.templates) {
                if (persistedState.templates.favorites) {
                    persistedState.templates.favorites.forEach(id => {
                        this.store.dispatch(templatesSlice.actions.toggleFavorite(id));
                    });
                }
            }
            
            if (persistedState.ai) {
                if (persistedState.ai.chatHistory) {
                    persistedState.ai.chatHistory.forEach(message => {
                        this.store.dispatch(aiSlice.actions.addChatMessage(message));
                    });
                }
                this.store.dispatch(aiSlice.actions.setAIEnabled(persistedState.ai.isEnabled));
            }
            
            console.log('State loaded from persistence');
        } catch (error) {
            console.log('No persisted state found, starting fresh');
        }
    }

    addClient(ws, clientId) {
        this.clients.set(clientId, ws);
        
        // Send current state to new client
        const currentState = this.store.getState();
        ws.send(JSON.stringify({
            type: 'initial-state',
            state: currentState,
            timestamp: Date.now()
        }));
        
        console.log(`Client ${clientId} connected to state manager`);
    }

    removeClient(clientId) {
        this.clients.delete(clientId);
        console.log(`Client ${clientId} disconnected from state manager`);
    }

    dispatch(action) {
        return this.store.dispatch(action);
    }

    getState() {
        return this.store.getState();
    }

    // Action creators export
    get actions() {
        return {
            patch: patchSlice.actions,
            live: liveSlice.actions,
            ui: uiSlice.actions,
            templates: templatesSlice.actions,
            ai: aiSlice.actions
        };
    }
}

module.exports = {
    StateManager,
    patchSlice,
    liveSlice,
    uiSlice,
    templatesSlice,
    aiSlice
};
