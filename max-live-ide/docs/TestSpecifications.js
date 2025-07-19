/**
 * Test Specifications for Drag-to-Live and Real-Time Sync
 * Comprehensive test cases for manual and automated testing
 */

// Manual Test Case Specifications
export const MANUAL_TEST_CASES = {
  export: {
    basic: {
      id: 'EXPORT-001',
      title: 'Basic Export Flow',
      priority: 'High',
      prerequisites: [
        'Devible application is running',
        'Simple patch with 3-4 connected objects exists',
        'Ableton Live is installed (optional for this test)'
      ],
      steps: [
        {
          step: 1,
          action: 'Click "Export to Live" button in toolbar',
          expected: 'Export modal opens with progress bar at 0%'
        },
        {
          step: 2,
          action: 'Wait for export process to complete',
          expected: 'Progress bar advances through 6 stages: Validation (10%) → Conversion (30%) → Metadata (50%) → Package (70%) → Download (90%) → Complete (100%)'
        },
        {
          step: 3,
          action: 'Verify export completion',
          expected: 'Success message displayed with drag zone containing .amxd file'
        },
        {
          step: 4,
          action: 'Click "Download File" button',
          expected: 'Browser downloads .amxd file with correct filename'
        },
        {
          step: 5,
          action: 'Inspect downloaded file size',
          expected: 'File size > 0 bytes, typically 2-10KB for simple patches'
        }
      ],
      validation: [
        'Export completes without errors',
        'Generated .amxd file is valid',
        'Download functionality works',
        'File contains expected patch data'
      ]
    },
    
    complex: {
      id: 'EXPORT-002',
      title: 'Complex Patch Export',
      priority: 'High',
      prerequisites: [
        'Devible application is running',
        'Complex patch with 10+ objects exists',
        'Patch includes Live-specific objects (live.dial, live.gain~)',
        'Multiple parameter mappings configured'
      ],
      steps: [
        {
          step: 1,
          action: 'Open export settings modal',
          expected: 'Settings modal displays with all configuration options'
        },
        {
          step: 2,
          action: 'Configure export settings: Device Name="Test Complex", Author="Test User", Description="Complex device test"',
          expected: 'Settings are saved and modal can be closed'
        },
        {
          step: 3,
          action: 'Initiate export process',
          expected: 'Export proceeds with custom settings applied'
        },
        {
          step: 4,
          action: 'Verify exported device metadata',
          expected: 'Device name, author, and description match configured values'
        },
        {
          step: 5,
          action: 'Test drag-to-Live functionality (if Live available)',
          expected: 'Device can be dragged into Live browser and appears in User Library'
        }
      ],
      validation: [
        'Complex patches export successfully',
        'Live parameters are correctly mapped',
        'Custom metadata is preserved',
        'Drag-to-Live works with complex devices'
      ]
    },
    
    errorHandling: {
      id: 'EXPORT-003',
      title: 'Export Error Scenarios',
      priority: 'Medium',
      prerequisites: [
        'Devible application is running',
        'Ability to create empty/invalid patches'
      ],
      steps: [
        {
          step: 1,
          action: 'Create empty patch (no objects)',
          expected: 'Canvas is empty'
        },
        {
          step: 2,
          action: 'Attempt to export empty patch',
          expected: 'Export button shows as disabled OR error message displays'
        },
        {
          step: 3,
          action: 'Create patch with invalid object data',
          expected: 'Patch appears malformed in UI'
        },
        {
          step: 4,
          action: 'Attempt export of invalid patch',
          expected: 'Error notification appears with descriptive message'
        },
        {
          step: 5,
          action: 'Verify error recovery',
          expected: 'User can dismiss error and continue working'
        }
      ],
      validation: [
        'Empty patches are handled gracefully',
        'Invalid data triggers appropriate errors',
        'Error messages are user-friendly',
        'Application remains stable after errors'
      ]
    }
  },
  
  sync: {
    parameterSync: {
      id: 'SYNC-001',
      title: 'Bidirectional Parameter Sync',
      priority: 'Critical',
      prerequisites: [
        'Ableton Live is running',
        'AbletonJS plugin is installed and active',
        'Devible is connected to Live',
        'Device with parameters exists in Live'
      ],
      steps: [
        {
          step: 1,
          action: 'Verify connection status shows "Connected"',
          expected: 'Live Status Panel shows green connection indicator'
        },
        {
          step: 2,
          action: 'Create parameter control in Devible (e.g., live.dial)',
          expected: 'Parameter appears in Devible interface'
        },
        {
          step: 3,
          action: 'Modify parameter value in Devible',
          expected: 'Corresponding parameter in Live updates immediately (< 100ms delay)'
        },
        {
          step: 4,
          action: 'Modify same parameter directly in Live',
          expected: 'Devible parameter control updates to match Live value'
        },
        {
          step: 5,
          action: 'Perform rapid parameter changes (10+ per second)',
          expected: 'Both interfaces remain synchronized without lag or errors'
        }
      ],
      validation: [
        'Parameter changes sync bidirectionally',
        'Sync latency is < 100ms',
        'No parameter values are lost',
        'Rapid changes are handled smoothly'
      ]
    },
    
    connectionRecovery: {
      id: 'SYNC-002',
      title: 'Connection Recovery Testing',
      priority: 'High',
      prerequisites: [
        'Stable sync connection established',
        'Ability to disconnect Live or stop plugin'
      ],
      steps: [
        {
          step: 1,
          action: 'Establish stable sync connection',
          expected: 'Connection health shows 100%, all protocols active'
        },
        {
          step: 2,
          action: 'Simulate connection loss (close Live or disable plugin)',
          expected: 'Connection status changes to "Disconnected", error notification appears'
        },
        {
          step: 3,
          action: 'Make parameter changes while disconnected',
          expected: 'Changes are queued, UI shows disconnected state'
        },
        {
          step: 4,
          action: 'Restore connection (restart Live/plugin)',
          expected: 'Auto-reconnection occurs within 10 seconds'
        },
        {
          step: 5,
          action: 'Verify queued changes are applied',
          expected: 'All queued parameter changes are synchronized upon reconnection'
        }
      ],
      validation: [
        'Connection loss is detected immediately',
        'Auto-reconnection works reliably',
        'Parameter changes are queued during disconnection',
        'All queued changes apply upon reconnection'
      ]
    },
    
    performance: {
      id: 'SYNC-003',
      title: 'Sync Performance Testing',
      priority: 'Medium',
      prerequisites: [
        'Stable connection established',
        'Multiple parameters available for testing',
        'Performance monitoring tools available'
      ],
      steps: [
        {
          step: 1,
          action: 'Monitor baseline connection latency',
          expected: 'Latency consistently < 50ms under normal conditions'
        },
        {
          step: 2,
          action: 'Create 10+ simultaneous parameter changes',
          expected: 'All changes sync without significant latency increase'
        },
        {
          step: 3,
          action: 'Monitor memory usage during extended sync session (30+ minutes)',
          expected: 'Memory usage remains stable, no significant leaks'
        },
        {
          step: 4,
          action: 'Test sync under high CPU load',
          expected: 'Sync continues to function with acceptable degradation'
        },
        {
          step: 5,
          action: 'Verify connection health metrics accuracy',
          expected: 'Health percentages reflect actual connection quality'
        }
      ],
      validation: [
        'Latency remains acceptable under load',
        'Memory usage is stable over time',
        'High CPU load doesn\'t break sync',
        'Health metrics are accurate'
      ]
    }
  }
};

// Automated Test Specifications
export const AUTOMATED_TEST_SPECS = {
  unit: {
    exportComponent: {
      describe: 'DragToLiveExport Component',
      tests: [
        {
          it: 'should convert ReactFlow patch to Max format',
          setup: `
            const patchData = {
              nodes: [
                { id: 'osc1', data: { label: 'osc~ 440', objectType: 'audio' }, position: { x: 100, y: 100 } },
                { id: 'gain1', data: { label: 'live.gain~', objectType: 'live' }, position: { x: 100, y: 200 } }
              ],
              edges: [
                { id: 'e1', source: 'osc1', target: 'gain1', sourceHandle: 'outlet-0', targetHandle: 'inlet-0' }
              ]
            };
          `,
          test: `
            const maxPatch = convertToMaxPatch(patchData, {});
            expect(maxPatch.patcher.boxes).toHaveLength(2);
            expect(maxPatch.patcher.lines).toHaveLength(1);
            expect(maxPatch.patcher.boxes[0].maxclass).toBe('osc~');
            expect(maxPatch.patcher.boxes[1].maxclass).toBe('live.gain~');
          `
        },
        {
          it: 'should generate valid device metadata',
          setup: `
            const settings = {
              deviceName: 'Test Device',
              author: 'Test Author',
              version: '1.0.0',
              category: 'Instrument'
            };
          `,
          test: `
            const metadata = generateDeviceMetadata(settings);
            expect(metadata['live-device'].device.name).toBe('Test Device');
            expect(metadata['live-device'].device.author).toBe('Test Author');
            expect(metadata['live-device'].device.version).toBe('1.0.0');
            expect(metadata['live-device'].device.uuid).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i);
          `
        },
        {
          it: 'should handle empty patch data gracefully',
          setup: `
            const emptyPatch = { nodes: [], edges: [] };
          `,
          test: `
            expect(() => convertToMaxPatch(emptyPatch, {})).toThrow('No patch data to export');
          `
        },
        {
          it: 'should extract parameters from Live objects',
          setup: `
            const patchWithParams = {
              nodes: [
                { 
                  id: 'dial1', 
                  data: { 
                    label: 'live.dial @parameter_enable 1',
                    objectType: 'live',
                    parameter: 'frequency',
                    min: 20,
                    max: 20000,
                    default: 440
                  }
                }
              ],
              edges: []
            };
          `,
          test: `
            const parameters = extractParameters(patchWithParams);
            expect(parameters).toHaveLength(1);
            expect(parameters[0].name).toBe('frequency');
            expect(parameters[0].min).toBe(20);
            expect(parameters[0].max).toBe(20000);
            expect(parameters[0].default).toBe(440);
          `
        }
      ]
    },
    
    syncHook: {
      describe: 'useRealTimeSync Hook',
      tests: [
        {
          it: 'should initialize with disconnected state',
          setup: `
            const { result } = renderHook(() => useRealTimeSync());
          `,
          test: `
            expect(result.current.isConnected).toBe(false);
            expect(result.current.connectionState).toBe('disconnected');
            expect(result.current.syncedParameters.size).toBe(0);
          `
        },
        {
          it: 'should establish WebSocket connection',
          setup: `
            const mockWebSocket = new WebSocketMock('ws://localhost:8080');
            global.WebSocket = jest.fn(() => mockWebSocket);
            const { result } = renderHook(() => useRealTimeSync());
          `,
          test: `
            await act(async () => {
              result.current.connect();
              mockWebSocket.simulateOpen();
            });
            expect(result.current.isConnected).toBe(true);
            expect(result.current.connectionState).toBe('connected');
          `
        },
        {
          it: 'should sync parameter changes',
          setup: `
            const { result } = renderHook(() => useRealTimeSync());
            // Mock connected state
            act(() => {
              result.current.isConnected = true;
            });
          `,
          test: `
            await act(async () => {
              result.current.updateParameter('test.param', 64);
            });
            expect(result.current.parameterValues.get('test.param').value).toBe(64);
            expect(result.current.parameterValues.get('test.param').source).toBe('devible');
          `
        },
        {
          it: 'should handle connection errors gracefully',
          setup: `
            const mockWebSocket = new WebSocketMock('ws://localhost:8080');
            mockWebSocket.simulateError = jest.fn();
            global.WebSocket = jest.fn(() => mockWebSocket);
            const { result } = renderHook(() => useRealTimeSync());
          `,
          test: `
            await act(async () => {
              result.current.connect();
              mockWebSocket.simulateError(new Error('Connection failed'));
            });
            expect(result.current.connectionState).toBe('error');
            expect(result.current.syncErrors.length).toBeGreaterThan(0);
          `
        }
      ]
    },
    
    connectionManager: {
      describe: 'LiveConnectionManager',
      tests: [
        {
          it: 'should calculate health score correctly',
          setup: `
            const { result } = renderHook(() => useLiveConnection());
          `,
          test: `
            act(() => {
              result.current.updateConnectionHealth({
                websocket: true,
                http: true,
                udp: true,
                lastPing: 50
              });
            });
            expect(result.current.connectionHealth.overall).toBe(100);
          `
        },
        {
          it: 'should categorize errors appropriately',
          setup: `
            const { result } = renderHook(() => useLiveConnection());
          `,
          test: `
            act(() => {
              result.current.addConnectionError('live_not_running', 'Live is not responding');
            });
            const errors = result.current.connectionErrors;
            expect(errors[0].type).toBe('live_not_running');
            expect(errors[0].message).toBe('Live is not responding');
          `
        }
      ]
    }
  },
  
  integration: {
    exportWorkflow: {
      describe: 'Complete Export Workflow',
      tests: [
        {
          it: 'should complete full export process',
          setup: `
            // Setup test patch
            const testPatch = createTestPatch();
            render(<DragToLiveExport patchData={testPatch} />);
          `,
          test: `
            // 1. Click export button
            const exportButton = screen.getByText('Export to Live');
            fireEvent.click(exportButton);
            
            // 2. Wait for export completion
            await waitFor(() => {
              expect(screen.getByText(/Export Complete/i)).toBeInTheDocument();
            });
            
            // 3. Verify drag zone appears
            expect(screen.getByText(/Drag this to Ableton Live/i)).toBeInTheDocument();
            
            // 4. Test download functionality
            const downloadButton = screen.getByText('Download File');
            fireEvent.click(downloadButton);
            
            // 5. Verify file download
            expect(mockDownload).toHaveBeenCalledWith(expect.stringContaining('.amxd'));
          `
        }
      ]
    },
    
    syncWorkflow: {
      describe: 'Real-Time Sync Integration',
      tests: [
        {
          it: 'should maintain parameter sync across disconnection',
          setup: `
            const mockWebSocket = new WebSocketMock('ws://localhost:8080');
            global.WebSocket = jest.fn(() => mockWebSocket);
            const { result } = renderHook(() => useRealTimeSync());
          `,
          test: `
            // 1. Establish connection
            await act(async () => {
              result.current.connect();
              mockWebSocket.simulateOpen();
            });
            
            // 2. Sync initial parameters
            await act(async () => {
              result.current.updateParameter('test.param', 100);
            });
            
            // 3. Simulate disconnection
            await act(async () => {
              mockWebSocket.simulateClose();
            });
            
            // 4. Queue parameter changes during disconnection
            await act(async () => {
              result.current.updateParameter('test.param', 75);
            });
            
            // 5. Reconnect and verify sync
            await act(async () => {
              mockWebSocket.simulateOpen();
            });
            
            expect(result.current.parameterValues.get('test.param').value).toBe(75);
          `
        }
      ]
    }
  },
  
  e2e: {
    completeUserJourney: {
      describe: 'End-to-End User Journey',
      tests: [
        {
          it: 'should support complete patch creation and export workflow',
          test: `
            // 1. Open Devible application
            cy.visit('/');
            
            // 2. Create new patch
            cy.get('[data-testid="new-patch-button"]').click();
            
            // 3. Add objects to canvas
            cy.get('[data-testid="object-library"]').should('be.visible');
            cy.get('[data-testid="osc-object"]').drag('[data-testid="canvas"]');
            cy.get('[data-testid="gain-object"]').drag('[data-testid="canvas"]');
            
            // 4. Connect objects
            cy.get('[data-testid="osc-outlet"]').drag('[data-testid="gain-inlet"]');
            
            // 5. Configure export settings
            cy.get('[data-testid="export-button"]').click();
            cy.get('[data-testid="export-settings"]').click();
            cy.get('[data-testid="device-name"]').type('Test Device');
            cy.get('[data-testid="save-settings"]').click();
            
            // 6. Complete export
            cy.get('[data-testid="start-export"]').click();
            cy.get('[data-testid="export-progress"]').should('contain', '100%');
            
            // 7. Verify export success
            cy.get('[data-testid="export-success"]').should('be.visible');
            cy.get('[data-testid="download-button"]').should('be.enabled');
          `
        },
        {
          it: 'should handle Live connection and parameter sync',
          test: `
            // 1. Start with Live connection
            cy.visit('/', {
              onBeforeLoad: (win) => {
                // Mock WebSocket for Live connection
                win.WebSocket = MockWebSocket;
              }
            });
            
            // 2. Verify connection status
            cy.get('[data-testid="connection-status"]').should('contain', 'Connected');
            
            // 3. Create parameter control
            cy.get('[data-testid="live-dial"]').drag('[data-testid="canvas"]');
            
            // 4. Test parameter sync
            cy.get('[data-testid="parameter-control"]').invoke('val', 75);
            cy.get('[data-testid="parameter-value"]').should('contain', '75');
            
            // 5. Simulate Live parameter change
            cy.window().then((win) => {
              win.mockWebSocket.simulateMessage({
                type: 'parameter_update',
                parameterId: 'dial1.value',
                value: 50
              });
            });
            
            // 6. Verify UI updates
            cy.get('[data-testid="parameter-control"]').should('have.value', '50');
          `
        }
      ]
    }
  }
};

// Test Utilities and Mocks
export const TEST_UTILITIES = {
  mocks: {
    webSocket: `
      class WebSocketMock {
        constructor(url) {
          this.url = url;
          this.readyState = WebSocket.CONNECTING;
          setTimeout(() => this.simulateOpen(), 100);
        }
        
        simulateOpen() {
          this.readyState = WebSocket.OPEN;
          if (this.onopen) this.onopen();
        }
        
        simulateClose() {
          this.readyState = WebSocket.CLOSED;
          if (this.onclose) this.onclose();
        }
        
        simulateError(error) {
          if (this.onerror) this.onerror(error);
        }
        
        simulateMessage(data) {
          if (this.onmessage) {
            this.onmessage({ data: JSON.stringify(data) });
          }
        }
        
        send(data) {
          this.lastSentMessage = JSON.parse(data);
        }
        
        close() {
          this.simulateClose();
        }
      }
    `,
    
    testPatch: `
      function createTestPatch() {
        return {
          nodes: [
            {
              id: 'osc1',
              type: 'maxObject',
              position: { x: 100, y: 100 },
              data: {
                label: 'osc~ 440',
                objectType: 'audio',
                inputs: ['frequency'],
                outputs: ['signal']
              }
            },
            {
              id: 'gain1',
              type: 'maxObject',
              position: { x: 100, y: 200 },
              data: {
                label: 'live.gain~ @parameter_enable 1',
                objectType: 'live',
                inputs: ['signal'],
                outputs: ['signal'],
                parameter: 'volume'
              }
            },
            {
              id: 'dac1',
              type: 'maxObject',
              position: { x: 100, y: 300 },
              data: {
                label: 'dac~',
                objectType: 'audio',
                inputs: ['left', 'right'],
                outputs: []
              }
            }
          ],
          edges: [
            {
              id: 'e1',
              source: 'osc1',
              target: 'gain1',
              sourceHandle: 'outlet-0',
              targetHandle: 'inlet-0'
            },
            {
              id: 'e2',
              source: 'gain1',
              target: 'dac1',
              sourceHandle: 'outlet-0',
              targetHandle: 'inlet-0'
            }
          ]
        };
      }
    `
  },
  
  helpers: {
    setup: `
      // Test setup helpers
      export const setupTestEnvironment = () => {
        // Mock notifications
        jest.mock('@mantine/notifications', () => ({
          notifications: {
            show: jest.fn(),
            hide: jest.fn(),
            clean: jest.fn()
          }
        }));
        
        // Mock file downloads
        global.URL.createObjectURL = jest.fn(() => 'mock-blob-url');
        global.URL.revokeObjectURL = jest.fn();
        
        // Mock drag and drop
        global.DataTransfer = class {
          constructor() {
            this.data = {};
            this.files = [];
          }
          setData(format, data) {
            this.data[format] = data;
          }
          getData(format) {
            return this.data[format];
          }
        };
      };
    `,
    
    cleanup: `
      export const cleanupTestEnvironment = () => {
        jest.clearAllMocks();
        delete global.WebSocket;
        delete global.URL.createObjectURL;
        delete global.URL.revokeObjectURL;
        delete global.DataTransfer;
      };
    `
  }
};

// Test Configuration
export const TEST_CONFIG = {
  jest: {
    testEnvironment: 'jsdom',
    setupFilesAfterEnv: ['<rootDir>/src/setupTests.js'],
    moduleNameMapping: {
      '\\.(css|less|scss|sass)$': 'identity-obj-proxy'
    },
    testTimeout: 10000,
    collectCoverageFrom: [
      'src/components/**/*.{js,jsx}',
      'src/hooks/**/*.{js,jsx}',
      '!src/**/*.test.{js,jsx}',
      '!src/index.js'
    ],
    coverageThreshold: {
      global: {
        branches: 80,
        functions: 80,
        lines: 80,
        statements: 80
      }
    }
  },
  
  cypress: {
    baseUrl: 'http://localhost:3000',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: true,
    screenshotOnRunFailure: true,
    defaultCommandTimeout: 10000,
    retries: {
      runMode: 2,
      openMode: 0
    }
  }
};

export default {
  MANUAL_TEST_CASES,
  AUTOMATED_TEST_SPECS,
  TEST_UTILITIES,
  TEST_CONFIG
};
