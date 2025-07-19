/**
 * Drag-to-Live Export Component
 * Handles drag-and-drop .amxd export with HTML5 Drag API and fallback download
 */

import React, { useState, useRef, useCallback } from 'react';
import { 
  Button, 
  Group, 
  Text, 
  Paper, 
  Alert,
  Progress,
  Badge,
  ActionIcon,
  Tooltip,
  Modal,
  Stack,
  TextInput,
  Textarea,
  Switch
} from '@mantine/core';
import { 
  IconDownload, 
  IconDragDrop, 
  IconCheck, 
  IconX, 
  IconAlertCircle,
  IconSettings,
  IconMusic,
  IconFile
} from '@tabler/icons-react';
import { notifications } from '@mantine/notifications';
import './DragToLiveExport.css';

/**
 * Main drag-to-Live export component
 */
const DragToLiveExport = ({ 
  patchData,
  projectName = 'Untitled',
  isConnectedToLive = false,
  onExportStart,
  onExportComplete,
  onExportError 
}) => {
  const [isExporting, setIsExporting] = useState(false);
  const [exportProgress, setExportProgress] = useState(0);
  const [exportStatus, setExportStatus] = useState('idle'); // 'idle', 'exporting', 'success', 'error'
  const [exportData, setExportData] = useState(null);
  const [showSettings, setShowSettings] = useState(false);
  const [exportSettings, setExportSettings] = useState({
    deviceName: projectName,
    description: '',
    author: '',
    version: '1.0.0',
    category: 'Instrument',
    includePatchNotes: true,
    compressAssets: true,
    embedPresets: false
  });

  const dropZoneRef = useRef(null);
  const downloadLinkRef = useRef(null);

  // Export to .amxd format
  const exportToAmxd = useCallback(async () => {
    try {
      setIsExporting(true);
      setExportStatus('exporting');
      setExportProgress(0);
      
      onExportStart?.();

      // Step 1: Validate patch data (10%)
      setExportProgress(10);
      await new Promise(resolve => setTimeout(resolve, 100));
      
      if (!patchData || !patchData.nodes || patchData.nodes.length === 0) {
        throw new Error('No patch data to export');
      }

      // Step 2: Convert ReactFlow data to Max patch format (30%)
      setExportProgress(30);
      const maxPatch = await convertToMaxPatch(patchData, exportSettings);
      
      // Step 3: Generate device metadata (50%)
      setExportProgress(50);
      const deviceMetadata = generateDeviceMetadata(exportSettings);
      
      // Step 4: Create .amxd package structure (70%)
      setExportProgress(70);
      const amxdPackage = await createAmxdPackage(maxPatch, deviceMetadata, exportSettings);
      
      // Step 5: Generate downloadable blob (90%)
      setExportProgress(90);
      const blob = new Blob([amxdPackage], { type: 'application/octet-stream' });
      const url = URL.createObjectURL(blob);
      
      // Step 6: Complete export (100%)
      setExportProgress(100);
      
      const exportResult = {
        blob,
        url,
        filename: `${exportSettings.deviceName}.amxd`,
        size: blob.size,
        timestamp: new Date().toISOString()
      };
      
      setExportData(exportResult);
      setExportStatus('success');
      
      notifications.show({
        title: 'Export Complete',
        message: `${exportSettings.deviceName}.amxd ready for use in Live`,
        color: 'green',
        icon: <IconCheck size={16} />
      });

      onExportComplete?.(exportResult);
      
      return exportResult;
      
    } catch (error) {
      console.error('Export failed:', error);
      setExportStatus('error');
      
      notifications.show({
        title: 'Export Failed',
        message: error.message,
        color: 'red',
        icon: <IconX size={16} />
      });
      
      onExportError?.(error);
      throw error;
      
    } finally {
      setIsExporting(false);
    }
  }, [patchData, exportSettings, onExportStart, onExportComplete, onExportError]);

  // Convert ReactFlow patch to Max patch format
  const convertToMaxPatch = async (patchData, settings) => {
    const maxObjects = [];
    const connections = [];

    // Convert nodes to Max objects
    patchData.nodes.forEach(node => {
      const maxObject = {
        id: node.id,
        maxclass: getMaxClass(node.data.objectType),
        text: node.data.label,
        patching_rect: [
          node.position.x,
          node.position.y,
          node.data.width || 80,
          node.data.height || 20
        ],
        fontsize: 12,
        numinlets: node.data.inputs?.length || 1,
        numoutlets: node.data.outputs?.length || 1
      };

      // Add object-specific attributes
      if (node.data.objectType === 'live') {
        maxObject.parameter_enable = 1;
        maxObject.saved_object_attributes = {
          parameter_longname: node.data.parameter || node.id,
          parameter_shortname: node.data.shortName || node.id.substring(0, 8)
        };
      }

      maxObjects.push(maxObject);
    });

    // Convert edges to Max patch cords
    patchData.edges.forEach(edge => {
      const sourceNode = patchData.nodes.find(n => n.id === edge.source);
      const targetNode = patchData.nodes.find(n => n.id === edge.target);
      
      if (sourceNode && targetNode) {
        connections.push({
          patchline: {
            source: [sourceNode.id, parseInt(edge.sourceHandle?.split('-')[1]) || 0],
            destination: [targetNode.id, parseInt(edge.targetHandle?.split('-')[1]) || 0]
          }
        });
      }
    });

    return {
      patcher: {
        fileversion: 1,
        appversion: {
          major: 8,
          minor: 5,
          revision: 6,
          architecture: "x64",
          modernui: 1
        },
        classnamespace: "box",
        rect: [34, 87, 1372, 779],
        bglocked: 0,
        openinpresentation: 1,
        default_fontsize: 12,
        default_fontface: 0,
        default_fontname: "Arial",
        gridonopen: 1,
        gridsize: [15, 15],
        gridsnaponopen: 1,
        objectsnaponopen: 1,
        statusbarvisible: 2,
        toolbarvisible: 1,
        lefttoolbarpinned: 0,
        toptoolbarpinned: 0,
        righttoolbarpinned: 0,
        bottomtoolbarpinned: 0,
        toolbars_unpinned_last_save: 0,
        tallnewobj: 0,
        boxanimatetime: 200,
        enablehscroll: 1,
        enablevscroll: 1,
        devicewidth: 0,
        description: settings.description,
        digest: "",
        tags: "",
        style: "",
        subpatcher_template: "",
        assistshowspatchername: 0,
        boxes: maxObjects,
        lines: connections
      }
    };
  };

  // Generate device metadata
  const generateDeviceMetadata = (settings) => {
    return {
      "live-device": {
        device: {
          name: settings.deviceName,
          author: settings.author,
          description: settings.description,
          version: settings.version,
          uuid: generateUUID(),
          category: settings.category,
          device_type: getDeviceType(settings.category),
          creation_time: new Date().toISOString(),
          modification_time: new Date().toISOString()
        },
        parameters: extractParameters(patchData),
        presets: settings.embedPresets ? generatePresets() : []
      }
    };
  };

  // Create .amxd package (simplified ZIP-like structure)
  const createAmxdPackage = async (maxPatch, metadata, settings) => {
    const packageData = {
      'Device.amxd': JSON.stringify(maxPatch, null, 2),
      'DeviceMetadata.json': JSON.stringify(metadata, null, 2)
    };

    if (settings.includePatchNotes) {
      packageData['README.txt'] = generateReadme(settings);
    }

    // In a real implementation, this would create a proper ZIP file
    // For this demo, we'll create a JSON representation
    return JSON.stringify(packageData, null, 2);
  };

  // Helper functions
  const getMaxClass = (objectType) => {
    const typeMap = {
      'live': 'live.dial',
      'audio': 'dac~',
      'midi': 'notein',
      'math': '+',
      'logic': 'gate'
    };
    return typeMap[objectType] || 'newobj';
  };

  const getDeviceType = (category) => {
    const categoryMap = {
      'Instrument': 'instrument',
      'Audio Effect': 'audio_device',
      'MIDI Effect': 'midi_device',
      'Live Integration': 'max_device'
    };
    return categoryMap[category] || 'max_device';
  };

  const extractParameters = (patchData) => {
    return patchData.nodes
      .filter(node => node.data.objectType === 'live')
      .map(node => ({
        name: node.data.parameter || node.id,
        min: node.data.min || 0,
        max: node.data.max || 127,
        default: node.data.default || 64,
        type: node.data.paramType || 'float'
      }));
  };

  const generatePresets = () => {
    // Generate default presets based on parameters
    return [
      {
        name: 'Default',
        parameters: {}
      }
    ];
  };

  const generateReadme = (settings) => {
    return `${settings.deviceName} v${settings.version}
Created with Devible - Max for Live Development Platform

Device Information:
- Name: ${settings.deviceName}
- Author: ${settings.author}
- Category: ${settings.category}
- Description: ${settings.description}

Installation:
1. Drag this .amxd file into Ableton Live
2. The device will appear in your User Library
3. Drag onto a track to use

Created: ${new Date().toLocaleDateString()}
`;
  };

  const generateUUID = () => {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  };

  // Handle drag start for HTML5 drag-and-drop
  const handleDragStart = useCallback((event) => {
    if (!exportData) return;

    event.dataTransfer.effectAllowed = 'copy';
    event.dataTransfer.setData('application/octet-stream', exportData.url);
    event.dataTransfer.setData('DownloadURL', `application/octet-stream:${exportData.filename}:${exportData.url}`);
    
    // Create drag image
    const dragImage = new Image();
    dragImage.src = 'data:image/svg+xml;base64,' + btoa(`
      <svg width="100" height="40" xmlns="http://www.w3.org/2000/svg">
        <rect width="100" height="40" fill="#23227e" rx="5"/>
        <text x="50" y="25" text-anchor="middle" fill="white" font-size="12">
          📦 ${exportData.filename}
        </text>
      </svg>
    `);
    event.dataTransfer.setDragImage(dragImage, 50, 20);

    notifications.show({
      title: 'Drag to Live',
      message: 'Drop the device into Ableton Live\'s browser',
      color: 'blue'
    });
  }, [exportData]);

  // Handle fallback download
  const handleDownload = useCallback(() => {
    if (!exportData) return;

    const link = downloadLinkRef.current;
    link.href = exportData.url;
    link.download = exportData.filename;
    link.click();

    notifications.show({
      title: 'Download Started',
      message: `${exportData.filename} is downloading`,
      color: 'blue',
      icon: <IconDownload size={16} />
    });
  }, [exportData]);

  // Render export status
  const renderExportStatus = () => {
    switch (exportStatus) {
      case 'exporting':
        return (
          <Stack gap="sm">
            <Text size="sm" c="blue">Exporting device...</Text>
            <Progress value={exportProgress} size="sm" color="blue" animated />
            <Text size="xs" c="dimmed">{exportProgress}% complete</Text>
          </Stack>
        );
        
      case 'success':
        return (
          <Alert
            icon={<IconCheck size={16} />}
            title="Export Complete"
            color="green"
            variant="light"
          >
            <Text size="sm">
              Your device is ready! Drag it to Live or download the .amxd file.
            </Text>
          </Alert>
        );
        
      case 'error':
        return (
          <Alert
            icon={<IconAlertCircle size={16} />}
            title="Export Failed"
            color="red"
            variant="light"
          >
            <Text size="sm">
              There was an error exporting your device. Please try again.
            </Text>
          </Alert>
        );
        
      default:
        return null;
    }
  };

  return (
    <div className="drag-to-live-export">
      {/* Export Button & Controls */}
      <Group gap="sm">
        <Button
          leftSection={<IconMusic size={16} />}
          onClick={exportToAmxd}
          loading={isExporting}
          disabled={!patchData || patchData.nodes?.length === 0}
          color="#23227e"
          size="sm"
        >
          Export to Live
        </Button>

        <Tooltip label="Export Settings">
          <ActionIcon
            variant="light"
            onClick={() => setShowSettings(true)}
            disabled={isExporting}
          >
            <IconSettings size={16} />
          </ActionIcon>
        </Tooltip>

        {!isConnectedToLive && (
          <Badge color="orange" variant="light" size="sm">
            Live Disconnected
          </Badge>
        )}
      </Group>

      {/* Export Status */}
      {exportStatus !== 'idle' && (
        <Paper p="md" mt="sm" radius="md" withBorder>
          {renderExportStatus()}
        </Paper>
      )}

      {/* Drag Zone (when export is complete) */}
      {exportStatus === 'success' && exportData && (
        <Paper
          ref={dropZoneRef}
          p="lg"
          mt="sm"
          radius="md"
          className="drag-zone success"
          draggable
          onDragStart={handleDragStart}
        >
          <Stack align="center" gap="sm">
            <IconDragDrop size={32} color="#17e2c3" />
            <Text fw={600} size="sm">
              📦 {exportData.filename}
            </Text>
            <Text size="xs" c="dimmed" ta="center">
              Drag this to Ableton Live's browser or click to download
            </Text>
            <Group gap="sm">
              <Button
                leftSection={<IconDragDrop size={16} />}
                variant="light"
                size="xs"
                color="#17e2c3"
                draggable
                onDragStart={handleDragStart}
              >
                Drag to Live
              </Button>
              <Button
                leftSection={<IconDownload size={16} />}
                variant="outline"
                size="xs"
                onClick={handleDownload}
              >
                Download File
              </Button>
            </Group>
          </Stack>
        </Paper>
      )}

      {/* Hidden download link for fallback */}
      <a
        ref={downloadLinkRef}
        style={{ display: 'none' }}
        href="#"
        download
      >
        Download
      </a>

      {/* Export Settings Modal */}
      <Modal
        opened={showSettings}
        onClose={() => setShowSettings(false)}
        title="Export Settings"
        size="md"
      >
        <Stack gap="md">
          <TextInput
            label="Device Name"
            value={exportSettings.deviceName}
            onChange={(e) => setExportSettings(prev => ({
              ...prev,
              deviceName: e.target.value
            }))}
            required
          />

          <TextInput
            label="Author"
            value={exportSettings.author}
            onChange={(e) => setExportSettings(prev => ({
              ...prev,
              author: e.target.value
            }))}
            placeholder="Your name"
          />

          <Textarea
            label="Description"
            value={exportSettings.description}
            onChange={(e) => setExportSettings(prev => ({
              ...prev,
              description: e.target.value
            }))}
            placeholder="Describe your device"
            rows={3}
          />

          <Group grow>
            <TextInput
              label="Version"
              value={exportSettings.version}
              onChange={(e) => setExportSettings(prev => ({
                ...prev,
                version: e.target.value
              }))}
            />
            <TextInput
              label="Category"
              value={exportSettings.category}
              onChange={(e) => setExportSettings(prev => ({
                ...prev,
                category: e.target.value
              }))}
            />
          </Group>

          <Stack gap="xs">
            <Switch
              label="Include patch notes"
              checked={exportSettings.includePatchNotes}
              onChange={(e) => setExportSettings(prev => ({
                ...prev,
                includePatchNotes: e.currentTarget.checked
              }))}
            />
            <Switch
              label="Compress assets"
              checked={exportSettings.compressAssets}
              onChange={(e) => setExportSettings(prev => ({
                ...prev,
                compressAssets: e.currentTarget.checked
              }))}
            />
            <Switch
              label="Embed presets"
              checked={exportSettings.embedPresets}
              onChange={(e) => setExportSettings(prev => ({
                ...prev,
                embedPresets: e.currentTarget.checked
              }))}
            />
          </Stack>

          <Group justify="flex-end" mt="md">
            <Button variant="light" onClick={() => setShowSettings(false)}>
              Cancel
            </Button>
            <Button onClick={() => setShowSettings(false)}>
              Save Settings
            </Button>
          </Group>
        </Stack>
      </Modal>
    </div>
  );
};

export default DragToLiveExport;
