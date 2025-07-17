import React from 'react';
import { MantineProvider, createTheme } from '@mantine/core';
import '@mantine/core/styles.css';
import '@mantine/notifications/styles.css';
import '@mantine/spotlight/styles.css';

// Custom theme for Max Live IDE - Dark theme optimized for audio production
const theme = createTheme({
  /** Put your mantine theme override here */
  colorScheme: 'dark',
  primaryColor: 'orange',
  colors: {
    // Custom color palette for audio/music applications
    dark: [
      '#C1C2C5',
      '#A6A7AB',
      '#909296',
      '#5c5f66',
      '#373A40',
      '#2C2E33',
      '#25262b',
      '#1A1B1E',
      '#141517',
      '#101113',
    ],
    // Orange accent color for highlights
    orange: [
      '#fff4e6',
      '#ffe8cc',
      '#ffd19b',
      '#ffb366',
      '#ff9640',
      '#ff8026',
      '#ff7514',
      '#e8620a',
      '#d15302',
      '#b84500',
    ],
    // Blue for secondary actions
    blue: [
      '#e7f5ff',
      '#d0ebff',
      '#a5d8ff',
      '#74c0fc',
      '#4dabf7',
      '#339af0',
      '#228be6',
      '#1c7ed6',
      '#1971c2',
      '#1864ab',
    ]
  },
  fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif',
  headings: {
    fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif',
  },
  components: {
    Button: {
      styles: (theme) => ({
        root: {
          fontWeight: 500,
          borderRadius: theme.radius.sm,
        },
      }),
    },
    Paper: {
      styles: (theme) => ({
        root: {
          backgroundColor: theme.colors.dark[7],
          border: `1px solid ${theme.colors.dark[6]}`,
        },
      }),
    },
    Badge: {
      styles: (theme) => ({
        root: {
          textTransform: 'none',
          fontWeight: 500,
        },
      }),
    },
    TextInput: {
      styles: (theme) => ({
        input: {
          backgroundColor: theme.colors.dark[8],
          borderColor: theme.colors.dark[6],
          '&:focus': {
            borderColor: theme.colors.orange[5],
          },
        },
      }),
    },
  },
  globalStyles: (theme) => ({
    '*, *::before, *::after': {
      boxSizing: 'border-box',
    },
    body: {
      backgroundColor: theme.colors.dark[9],
      color: theme.colors.dark[0],
      lineHeight: theme.lineHeight,
    },
  }),
});

export function CustomMantineProvider({ children }) {
  return (
    <MantineProvider theme={theme} defaultColorScheme="dark">
      {children}
    </MantineProvider>
  );
}

export default CustomMantineProvider;
