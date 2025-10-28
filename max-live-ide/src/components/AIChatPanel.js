/**
 * AI Chat Panel - Interactive AI assistant for M4L development
 */

import React, { useState, useRef, useEffect } from 'react';
import {
  Paper,
  Stack,
  TextInput,
  Button,
  ScrollArea,
  Text,
  Group,
  Badge,
  ActionIcon,
  Divider,
  Code,
  ThemeIcon,
  Tooltip,
  Loader
} from '@mantine/core';
import {
  IconSend,
  IconRobot,
  IconUser,
  IconCopy,
  IconCheck,
  IconBulb,
  IconCode,
  IconBook
} from '@tabler/icons-react';
import { getAIService } from '../services/aiService';
const aiService = getAIService();

export function AIChatPanel({ currentPatch, onInsertCode, onCreateObject }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hi! I'm your M4L development assistant. I can help you:\n\n• Understand Max objects and their usage\n• Generate JavaScript code for js/jsui objects\n• Suggest patching techniques\n• Explain M4L concepts\n• Debug your patches\n\nWhat would you like to work on?",
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [copiedIndex, setCopiedIndex] = useState(null);
  const scrollAreaRef = useRef(null);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Build context from current patch
      const context = buildPatchContext(currentPatch);
      
      // Get AI response
      const response = await aiService.chat({
        messages: [...messages, userMessage],
        context,
        mode: 'm4l-assistant'
      });

      const assistantMessage = {
        role: 'assistant',
        content: response.message,
        suggestions: response.suggestions,
        codeBlocks: response.codeBlocks,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('AI chat error:', error);
      const errorMessage = {
        role: 'assistant',
        content: "I'm sorry, I encountered an error. Please try again or rephrase your question.",
        error: true,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const buildPatchContext = (patch) => {
    if (!patch?.nodes) return '';

    const objectTypes = patch.nodes.map(n => n.data?.type || 'unknown');
    const jsObjects = patch.nodes.filter(n => 
      n.data?.type === 'js' || n.data?.type === 'jsui'
    );

    return `
Current patch context:
- Total objects: ${patch.nodes.length}
- Object types: ${[...new Set(objectTypes)].join(', ')}
- JS objects: ${jsObjects.length}
${jsObjects.length > 0 ? `- JS object details: ${jsObjects.map(o => o.data?.label).join(', ')}` : ''}
    `.trim();
  };

  const copyToClipboard = async (text, index) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (error) {
      console.error('Copy failed:', error);
    }
  };

  const quickActions = [
    {
      icon: IconCode,
      label: 'Generate MIDI effect',
      prompt: 'Help me create a MIDI effect that...'
    },
    {
      icon: IconBulb,
      label: 'Explain concept',
      prompt: 'Explain how to use...'
    },
    {
      icon: IconBook,
      label: 'Show example',
      prompt: 'Show me an example of...'
    }
  ];

  return (
    <Paper shadow="sm" p="md" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Group justify="space-between" mb="md">
        <Group gap="xs">
          <ThemeIcon variant="light" size="lg">
            <IconRobot size={20} />
          </ThemeIcon>
          <div>
            <Text fw={600}>AI Assistant</Text>
            <Text size="xs" c="dimmed">M4L Development Helper</Text>
          </div>
        </Group>
        <Badge variant="dot" color="green">Online</Badge>
      </Group>

      {/* Quick Actions */}
      <Group gap="xs" mb="md">
        {quickActions.map((action, index) => (
          <Tooltip key={index} label={action.label}>
            <ActionIcon
              variant="light"
              size="lg"
              onClick={() => setInput(action.prompt)}
            >
              <action.icon size={16} />
            </ActionIcon>
          </Tooltip>
        ))}
      </Group>

      <Divider mb="md" />

      {/* Messages */}
      <ScrollArea
        style={{ flex: 1 }}
        viewportRef={scrollAreaRef}
        scrollbarSize={6}
      >
        <Stack gap="md" pr="xs">
          {messages.map((message, index) => (
            <MessageBubble
              key={index}
              message={message}
              index={index}
              copiedIndex={copiedIndex}
              onCopy={copyToClipboard}
              onInsertCode={onInsertCode}
              onCreateObject={onCreateObject}
            />
          ))}
          {isLoading && (
            <Group gap="xs">
              <Loader size="xs" />
              <Text size="sm" c="dimmed">Thinking...</Text>
            </Group>
          )}
          <div ref={messagesEndRef} />
        </Stack>
      </ScrollArea>

      {/* Input */}
      <Group gap="xs" mt="md" align="flex-end">
        <TextInput
          placeholder="Ask me anything about M4L development..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          style={{ flex: 1 }}
          disabled={isLoading}
        />
        <Button
          onClick={handleSend}
          loading={isLoading}
          leftSection={<IconSend size={16} />}
        >
          Send
        </Button>
      </Group>
    </Paper>
  );
}

function MessageBubble({ message, index, copiedIndex, onCopy, onInsertCode, onCreateObject }) {
  const isUser = message.role === 'user';
  const isError = message.error;

  return (
    <Group gap="xs" align="flex-start" wrap="nowrap">
      {!isUser && (
        <ThemeIcon
          variant="light"
          color={isError ? 'red' : 'blue'}
          size="md"
        >
          <IconRobot size={16} />
        </ThemeIcon>
      )}
      
      <Paper
        p="sm"
        withBorder
        style={{
          flex: 1,
          backgroundColor: isUser ? 'var(--mantine-color-blue-0)' : 'transparent',
          borderColor: isError ? 'var(--mantine-color-red-3)' : undefined
        }}
      >
        <Stack gap="xs">
          <Text size="sm" style={{ whiteSpace: 'pre-wrap' }}>
            {message.content}
          </Text>

          {/* Code blocks */}
          {message.codeBlocks?.map((block, i) => (
            <Paper key={i} p="xs" withBorder style={{ position: 'relative' }}>
              <Group justify="space-between" mb="xs">
                <Badge size="xs" variant="light">{block.language || 'code'}</Badge>
                <Group gap={4}>
                  <ActionIcon
                    size="xs"
                    variant="subtle"
                    onClick={() => onCopy(block.code, `${index}-${i}`)}
                  >
                    {copiedIndex === `${index}-${i}` ? (
                      <IconCheck size={14} />
                    ) : (
                      <IconCopy size={14} />
                    )}
                  </ActionIcon>
                  {block.language === 'javascript' && onInsertCode && (
                    <Button
                      size="xs"
                      variant="light"
                      onClick={() => onInsertCode(block.code)}
                    >
                      Insert
                    </Button>
                  )}
                </Group>
              </Group>
              <Code block style={{ fontSize: '0.75rem' }}>
                {block.code}
              </Code>
            </Paper>
          ))}

          {/* Suggestions */}
          {message.suggestions?.length > 0 && (
            <Stack gap={4}>
              <Text size="xs" fw={600} c="dimmed">Suggestions:</Text>
              {message.suggestions.map((suggestion, i) => (
                <Button
                  key={i}
                  size="xs"
                  variant="light"
                  onClick={() => {
                    if (suggestion.action === 'create') {
                      onCreateObject?.(suggestion.object);
                    }
                  }}
                >
                  {suggestion.text}
                </Button>
              ))}
            </Stack>
          )}

          <Text size="xs" c="dimmed">
            {message.timestamp.toLocaleTimeString()}
          </Text>
        </Stack>
      </Paper>

      {isUser && (
        <ThemeIcon variant="light" size="md">
          <IconUser size={16} />
        </ThemeIcon>
      )}
    </Group>
  );
}
