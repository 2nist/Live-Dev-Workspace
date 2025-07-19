/**
 * Sequence Diagrams for Export and Sync Flows
 * 
 * This file contains Mermaid sequence diagrams documenting the 
 * drag-to-Live export process and real-time parameter sync flows.
 */

// Export Sequence Diagram
export const EXPORT_SEQUENCE_DIAGRAM = `
sequenceDiagram
    participant User
    participant Devible
    participant ExportComponent
    participant MaxConverter
    participant FileSystem
    participant Browser
    participant AbletonLive as Ableton Live
    
    Note over User, AbletonLive: Drag-to-Live Export Flow
    
    User->>Devible: Click "Export to Live"
    Devible->>ExportComponent: initiate export
    
    Note over ExportComponent: Step 1: Validation (10%)
    ExportComponent->>ExportComponent: validate patch data
    ExportComponent->>User: show progress (10%)
    
    Note over ExportComponent: Step 2: Convert to Max (30%)
    ExportComponent->>MaxConverter: convertToMaxPatch(patchData)
    MaxConverter->>MaxConverter: convert ReactFlow nodes to Max objects
    MaxConverter->>MaxConverter: convert ReactFlow edges to patch cords
    MaxConverter->>MaxConverter: add Live-specific attributes
    MaxConverter-->>ExportComponent: return maxPatch
    ExportComponent->>User: show progress (30%)
    
    Note over ExportComponent: Step 3: Generate Metadata (50%)
    ExportComponent->>ExportComponent: generateDeviceMetadata()
    ExportComponent->>ExportComponent: extract parameters
    ExportComponent->>ExportComponent: create device UUID
    ExportComponent->>User: show progress (50%)
    
    Note over ExportComponent: Step 4: Create .amxd Package (70%)
    ExportComponent->>ExportComponent: createAmxdPackage()
    ExportComponent->>ExportComponent: bundle Max patch + metadata
    ExportComponent->>ExportComponent: add README and assets
    ExportComponent->>User: show progress (70%)
    
    Note over ExportComponent: Step 5: Generate Download (90%)
    ExportComponent->>FileSystem: create Blob with .amxd data
    FileSystem-->>ExportComponent: return blob URL
    ExportComponent->>User: show progress (90%)
    
    Note over ExportComponent: Step 6: Enable Drag & Drop (100%)
    ExportComponent->>ExportComponent: setup drag handlers
    ExportComponent->>User: show success + drag zone
    ExportComponent->>User: show progress (100%)
    
    alt Drag to Live Browser
        User->>Browser: drag .amxd file
        Browser->>AbletonLive: drop file event
        AbletonLive->>AbletonLive: install device to User Library
        AbletonLive-->>User: device appears in browser
    else Download File
        User->>ExportComponent: click download
        ExportComponent->>Browser: trigger download
        Browser->>FileSystem: save .amxd file
        FileSystem-->>User: file downloaded
    end
    
    Note over User, AbletonLive: Device Ready for Use
`;

// Real-Time Sync Sequence Diagram
export const SYNC_SEQUENCE_DIAGRAM = `
sequenceDiagram
    participant User
    participant Devible
    participant SyncHook
    participant WebSocket
    participant LivePlugin as Live Plugin
    participant AbletonLive as Ableton Live
    
    Note over User, AbletonLive: Real-Time Parameter Sync Flow
    
    User->>Devible: start application
    Devible->>SyncHook: initialize useRealTimeSync()
    
    Note over SyncHook: Connection Establishment
    SyncHook->>WebSocket: connect to ws://localhost:8080
    WebSocket->>LivePlugin: WebSocket connection
    LivePlugin->>AbletonLive: check Live status
    AbletonLive-->>LivePlugin: Live is running
    LivePlugin-->>WebSocket: connection confirmed
    WebSocket-->>SyncHook: connection established
    SyncHook->>Devible: update connection state
    
    Note over SyncHook: Initial Parameter Discovery
    SyncHook->>WebSocket: send request_parameters
    WebSocket->>LivePlugin: forward request
    LivePlugin->>AbletonLive: scan for Live devices
    AbletonLive-->>LivePlugin: return device list
    LivePlugin->>LivePlugin: extract parameters
    LivePlugin-->>WebSocket: send parameter_list
    WebSocket-->>SyncHook: receive parameters
    SyncHook->>Devible: update syncedParameters
    
    Note over User, AbletonLive: Bidirectional Parameter Sync
    
    rect rgb(240, 248, 255)
        Note over User, AbletonLive: Devible → Live Parameter Update
        User->>Devible: modify parameter in UI
        Devible->>SyncHook: updateParameter(id, value)
        SyncHook->>WebSocket: send parameter_update
        WebSocket->>LivePlugin: forward update
        LivePlugin->>AbletonLive: set parameter value
        AbletonLive-->>LivePlugin: parameter updated
        LivePlugin-->>WebSocket: send confirmation
        WebSocket-->>SyncHook: receive confirmation
        SyncHook->>Devible: update local state
    end
    
    rect rgb(248, 255, 240)
        Note over User, AbletonLive: Live → Devible Parameter Update
        User->>AbletonLive: modify parameter in Live UI
        AbletonLive->>LivePlugin: parameter changed event
        LivePlugin->>WebSocket: send parameter_update
        WebSocket->>SyncHook: receive update
        SyncHook->>Devible: trigger parameter change callback
        Devible->>Devible: update UI with new value
    end
    
    Note over SyncHook: Heartbeat & Health Monitoring
    loop Every 50ms
        SyncHook->>WebSocket: send heartbeat
        WebSocket->>LivePlugin: forward heartbeat
        LivePlugin-->>WebSocket: heartbeat response
        WebSocket-->>SyncHook: receive response
        SyncHook->>SyncHook: calculate latency
        SyncHook->>Devible: update connection health
    end
    
    Note over User, AbletonLive: Error Handling & Recovery
    
    alt Connection Lost
        WebSocket->>SyncHook: connection closed
        SyncHook->>SyncHook: detect connection loss
        SyncHook->>Devible: show connection error
        SyncHook->>SyncHook: start reconnection attempts
        
        loop Retry with backoff
            SyncHook->>WebSocket: attempt reconnection
            alt Reconnection Successful
                WebSocket-->>SyncHook: connection restored
                SyncHook->>Devible: show reconnection success
            else Reconnection Failed
                SyncHook->>SyncHook: wait with exponential backoff
            end
        end
    end
    
    alt Parameter Sync Error
        SyncHook->>WebSocket: send parameter_update
        WebSocket->>LivePlugin: forward update
        LivePlugin-->>WebSocket: send error response
        WebSocket-->>SyncHook: receive error
        SyncHook->>Devible: show parameter sync error
        SyncHook->>SyncHook: queue parameter for retry
    end
`;

// Connection Health Monitoring Diagram
export const CONNECTION_HEALTH_DIAGRAM = `
sequenceDiagram
    participant HealthMonitor
    participant WebSocket
    participant HTTP
    participant UDP
    participant LivePlugin as Live Plugin
    participant AbletonLive as Ableton Live
    
    Note over HealthMonitor, AbletonLive: Multi-Protocol Health Check
    
    HealthMonitor->>HealthMonitor: start health monitoring
    
    par WebSocket Health Check
        HealthMonitor->>WebSocket: ping with timestamp
        WebSocket->>LivePlugin: forward ping
        LivePlugin-->>WebSocket: pong with timestamp
        WebSocket-->>HealthMonitor: receive pong
        HealthMonitor->>HealthMonitor: calculate WebSocket latency
    and HTTP Health Check
        HealthMonitor->>HTTP: GET /ping
        HTTP->>AbletonLive: HTTP API call
        AbletonLive-->>HTTP: 200 OK response
        HTTP-->>HealthMonitor: response received
        HealthMonitor->>HealthMonitor: mark HTTP as healthy
    and UDP Health Check
        HealthMonitor->>UDP: send UDP packet
        UDP->>LivePlugin: UDP message
        LivePlugin-->>UDP: UDP response
        UDP-->>HealthMonitor: response received
        HealthMonitor->>HealthMonitor: mark UDP as healthy
    end
    
    HealthMonitor->>HealthMonitor: calculate overall health score
    Note over HealthMonitor: Health Score = WebSocket(40%) + HTTP(30%) + UDP(20%) + Latency(10%)
    
    HealthMonitor->>HealthMonitor: update health metrics
    
    alt All Protocols Healthy
        HealthMonitor->>HealthMonitor: health score = 100%
    else Some Protocols Failed
        HealthMonitor->>HealthMonitor: calculate partial health score
        HealthMonitor->>HealthMonitor: identify failed protocols
    else All Protocols Failed
        HealthMonitor->>HealthMonitor: health score = 0%
        HealthMonitor->>HealthMonitor: trigger connection recovery
    end
`;

// Export the diagrams for use in documentation
export const SEQUENCE_DIAGRAMS = {
  export: EXPORT_SEQUENCE_DIAGRAM,
  sync: SYNC_SEQUENCE_DIAGRAM,
  health: CONNECTION_HEALTH_DIAGRAM
};

// Mermaid configuration for rendering
export const MERMAID_CONFIG = {
  theme: 'base',
  themeVariables: {
    primaryColor: '#23227e',
    primaryTextColor: '#ffffff',
    primaryBorderColor: '#17e2c3',
    lineColor: '#17e2c3',
    secondaryColor: '#ffa500',
    tertiaryColor: '#f8f9fa',
    background: '#ffffff',
    mainBkg: '#ffffff',
    secondBkg: '#f8f9fa',
    tertiaryBkg: '#e9ecef'
  },
  sequence: {
    diagramMarginX: 50,
    diagramMarginY: 10,
    actorMargin: 50,
    width: 150,
    height: 65,
    boxMargin: 10,
    boxTextMargin: 5,
    noteMargin: 10,
    messageMargin: 35,
    mirrorActors: true,
    bottomMarginAdj: 1,
    useMaxWidth: true,
    rightAngles: false,
    showSequenceNumbers: false
  }
};

export default {
  SEQUENCE_DIAGRAMS,
  MERMAID_CONFIG
};
