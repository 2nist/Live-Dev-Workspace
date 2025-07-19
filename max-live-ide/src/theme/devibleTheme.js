import { MantineThemeOverride } from '@mantine/core';

/**
 * Devible Brand Theme Configuration for Mantine
 * Professional music production interface with accessibility compliance
 */
export const devibleTheme: MantineThemeOverride = {
  // Color scheme
  colorScheme: 'dark',
  
  // Primary colors matching Devible brand
  primaryColor: 'devible-primary',
  primaryShade: { light: 6, dark: 5 },
  
  // Color palette
  colors: {
    'devible-primary': [
      '#f5f5ff',    // 50
      '#ebebff',    // 100
      '#d6d6ff',    // 200
      '#b8b8ff',    // 300
      '#9999ff',    // 400
      '#7575ff',    // 500
      '#5656e6',    // 600
      '#3838cc',    // 700
      '#23227e',    // 800 - Primary brand color
      '#1a1a5c',    // 900
    ],
    'devible-secondary': [
      '#f0fffe',    // 50
      '#ccfff8',    // 100
      '#99fff0',    // 200
      '#66ffe8',    // 300
      '#33ffe0',    // 400
      '#17e2c3',    // 500 - Secondary brand color
      '#14c2a8',    // 600
      '#11a28d',    // 700
      '#0e8272',    // 800
      '#0b6257',    // 900
    ],
    'devible-tertiary': [
      '#fff8f0',    // 50
      '#ffedcc',    // 100
      '#ffd999',    // 200
      '#ffc566',    // 300
      '#ffb133',    // 400
      '#ffa500',    // 500 - Tertiary brand color
      '#e6940e',    // 600
      '#cc831c',    // 700
      '#b3722a',    // 800
      '#996138',    // 900
    ],
    // Override default grays for better consistency
    gray: [
      '#f9fafb',    // 50
      '#f3f4f6',    // 100
      '#e5e7eb',    // 200
      '#d1d5db',    // 300
      '#9ca3af',    // 400
      '#6b7280',    // 500
      '#4b5563',    // 600
      '#374151',    // 700
      '#1f2937',    // 800
      '#111827',    // 900
    ],
  },
  
  // Typography
  fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif',
  fontFamilyMonospace: 'JetBrains Mono, Fira Code, Source Code Pro, monospace',
  
  headings: {
    fontFamily: 'Cal Sans, Inter, sans-serif',
    fontWeight: 700,
    sizes: {
      h1: { 
        fontSize: '3rem',
        lineHeight: 1.25,
        fontWeight: 800
      },
      h2: { 
        fontSize: '2.25rem',
        lineHeight: 1.25,
        fontWeight: 700
      },
      h3: { 
        fontSize: '1.875rem',
        lineHeight: 1.3,
        fontWeight: 600
      },
      h4: { 
        fontSize: '1.5rem',
        lineHeight: 1.4,
        fontWeight: 600
      },
      h5: { 
        fontSize: '1.25rem',
        lineHeight: 1.5,
        fontWeight: 500
      },
      h6: { 
        fontSize: '1.125rem',
        lineHeight: 1.5,
        fontWeight: 500
      },
    },
  },
  
  fontSizes: {
    xs: '0.75rem',     // 12px
    sm: '0.875rem',    // 14px
    md: '1rem',        // 16px
    lg: '1.125rem',    // 18px
    xl: '1.25rem',     // 20px
  },
  
  // Spacing
  spacing: {
    xs: '0.5rem',      // 8px
    sm: '0.75rem',     // 12px
    md: '1rem',        // 16px
    lg: '1.5rem',      // 24px
    xl: '2rem',        // 32px
  },
  
  // Border radius
  radius: {
    xs: '0.125rem',    // 2px
    sm: '0.25rem',     // 4px
    md: '0.375rem',    // 6px
    lg: '0.5rem',      // 8px
    xl: '0.75rem',     // 12px
  },
  
  // Shadows
  shadows: {
    xs: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    sm: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    // Brand-specific shadows
    primary: '0 4px 14px 0 rgba(35, 34, 126, 0.15)',
    secondary: '0 4px 14px 0 rgba(23, 226, 195, 0.15)',
    tertiary: '0 4px 14px 0 rgba(255, 165, 0, 0.15)',
  },
  
  // Focus ring for accessibility
  focusRing: 'always',
  focusRingStyles: {
    styles: (theme) => ({
      outline: `3px solid ${theme.colors['devible-primary'][5]}`,
      outlineOffset: '2px',
    }),
    resetStyles: () => ({ outline: 'none' }),
    inputStyles: (theme) => ({
      outline: `2px solid ${theme.colors['devible-primary'][5]}`,
      outlineOffset: '1px',
    }),
  },
  
  // Component-specific overrides
  components: {
    // Button component
    Button: {
      styles: (theme) => ({
        root: {
          fontWeight: 600,
          transition: 'all 0.2s ease',
          '&:hover': {
            transform: 'translateY(-1px)',
          },
        },
      }),
      variants: {
        'devible-primary': (theme) => ({
          root: {
            background: `linear-gradient(135deg, ${theme.colors['devible-primary'][6]} 0%, ${theme.colors['devible-primary'][8]} 100%)`,
            color: theme.white,
            border: 'none',
            boxShadow: theme.shadows.primary,
            '&:hover': {
              background: `linear-gradient(135deg, ${theme.colors['devible-primary'][5]} 0%, ${theme.colors['devible-primary'][7]} 100%)`,
              boxShadow: theme.shadows.lg,
            },
          },
        }),
        'devible-secondary': (theme) => ({
          root: {
            background: `linear-gradient(135deg, ${theme.colors['devible-secondary'][4]} 0%, ${theme.colors['devible-secondary'][6]} 100%)`,
            color: theme.colors.gray[9],
            border: 'none',
            boxShadow: theme.shadows.secondary,
            '&:hover': {
              background: `linear-gradient(135deg, ${theme.colors['devible-secondary'][3]} 0%, ${theme.colors['devible-secondary'][5]} 100%)`,
              boxShadow: theme.shadows.lg,
            },
          },
        }),
        'devible-outline': (theme) => ({
          root: {
            background: 'transparent',
            color: theme.colors['devible-primary'][5],
            border: `2px solid ${theme.colors['devible-primary'][5]}`,
            '&:hover': {
              background: theme.colors['devible-primary'][5],
              color: theme.white,
            },
          },
        }),
      },
    },
    
    // Card component
    Card: {
      styles: (theme) => ({
        root: {
          backgroundColor: theme.colorScheme === 'dark' ? theme.colors.gray[8] : theme.white,
          borderColor: theme.colorScheme === 'dark' ? theme.colors.gray[7] : theme.colors.gray[2],
          transition: 'all 0.2s ease',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: theme.shadows.md,
          },
        },
      }),
      variants: {
        'devible-premium': (theme) => ({
          root: {
            background: `linear-gradient(135deg, ${theme.colors['devible-primary'][6]} 0%, ${theme.colors['devible-secondary'][5]} 50%, ${theme.colors['devible-tertiary'][5]} 100%)`,
            color: theme.white,
            border: 'none',
            boxShadow: theme.shadows.lg,
          },
        }),
      },
    },
    
    // Input components
    TextInput: {
      styles: (theme) => ({
        input: {
          backgroundColor: theme.colorScheme === 'dark' ? theme.colors.gray[8] : theme.white,
          borderColor: theme.colorScheme === 'dark' ? theme.colors.gray[6] : theme.colors.gray[3],
          '&:focus': {
            borderColor: theme.colors['devible-primary'][5],
            boxShadow: `0 0 0 2px ${theme.colors['devible-primary'][2]}`,
          },
        },
      }),
    },
    
    // Notification component
    Notification: {
      styles: (theme) => ({
        root: {
          backgroundColor: theme.colorScheme === 'dark' ? theme.colors.gray[8] : theme.white,
          borderColor: theme.colorScheme === 'dark' ? theme.colors.gray[7] : theme.colors.gray[2],
        },
      }),
    },
    
    // Modal component
    Modal: {
      styles: (theme) => ({
        modal: {
          backgroundColor: theme.colorScheme === 'dark' ? theme.colors.gray[8] : theme.white,
        },
        overlay: {
          backgroundColor: 'rgba(0, 0, 0, 0.75)',
          backdropFilter: 'blur(4px)',
        },
      }),
    },
    
    // Tooltip component
    Tooltip: {
      styles: (theme) => ({
        tooltip: {
          backgroundColor: theme.colorScheme === 'dark' ? theme.colors.gray[9] : theme.colors.gray[8],
          color: theme.white,
          fontSize: theme.fontSizes.sm,
          fontWeight: 500,
        },
      }),
    },
    
    // AppShell component for layout
    AppShell: {
      styles: (theme) => ({
        main: {
          backgroundColor: theme.colorScheme === 'dark' ? theme.colors.gray[9] : theme.colors.gray[0],
        },
        header: {
          backgroundColor: theme.colorScheme === 'dark' ? theme.colors.gray[8] : theme.white,
          borderColor: theme.colorScheme === 'dark' ? theme.colors.gray[7] : theme.colors.gray[2],
        },
        navbar: {
          backgroundColor: theme.colorScheme === 'dark' ? theme.colors.gray[8] : theme.white,
          borderColor: theme.colorScheme === 'dark' ? theme.colors.gray[7] : theme.colors.gray[2],
        },
        aside: {
          backgroundColor: theme.colorScheme === 'dark' ? theme.colors.gray[8] : theme.white,
          borderColor: theme.colorScheme === 'dark' ? theme.colors.gray[7] : theme.colors.gray[2],
        },
      }),
    },
    
    // Badge component for status indicators
    Badge: {
      styles: (theme) => ({
        root: {
          fontWeight: 600,
          textTransform: 'none',
        },
      }),
      variants: {
        'devible-connected': (theme) => ({
          root: {
            background: 'rgba(16, 185, 129, 0.1)',
            color: '#10b981',
            border: '1px solid rgba(16, 185, 129, 0.2)',
          },
        }),
        'devible-disconnected': (theme) => ({
          root: {
            background: 'rgba(239, 68, 68, 0.1)',
            color: '#ef4444',
            border: '1px solid rgba(239, 68, 68, 0.2)',
          },
        }),
        'devible-warning': (theme) => ({
          root: {
            background: 'rgba(245, 158, 11, 0.1)',
            color: '#f59e0b',
            border: '1px solid rgba(245, 158, 11, 0.2)',
          },
        }),
      },
    },
  },
  
  // Global styles
  globalStyles: (theme) => ({
    '*, *::before, *::after': {
      boxSizing: 'border-box',
    },
    
    body: {
      fontFamily: theme.fontFamily,
      backgroundColor: theme.colorScheme === 'dark' ? theme.colors.gray[9] : theme.colors.gray[0],
      color: theme.colorScheme === 'dark' ? theme.colors.gray[0] : theme.colors.gray[9],
      lineHeight: 1.5,
      fontSize: theme.fontSizes.md,
    },
    
    // Custom scrollbar styling
    '::-webkit-scrollbar': {
      width: '8px',
      height: '8px',
    },
    
    '::-webkit-scrollbar-track': {
      background: theme.colorScheme === 'dark' ? theme.colors.gray[8] : theme.colors.gray[1],
    },
    
    '::-webkit-scrollbar-thumb': {
      background: theme.colorScheme === 'dark' ? theme.colors.gray[6] : theme.colors.gray[4],
      borderRadius: '4px',
    },
    
    '::-webkit-scrollbar-thumb:hover': {
      background: theme.colorScheme === 'dark' ? theme.colors.gray[5] : theme.colors.gray[5],
    },
    
    // Selection styling
    '::selection': {
      backgroundColor: theme.colors['devible-primary'][5],
      color: theme.white,
    },
    
    // Focus visible for better accessibility
    ':focus-visible': {
      outline: `3px solid ${theme.colors['devible-primary'][5]}`,
      outlineOffset: '2px',
    },
    
    // Reduced motion support
    '@media (prefers-reduced-motion: reduce)': {
      '*, *::before, *::after': {
        animationDuration: '0.01ms !important',
        animationIterationCount: '1 !important',
        transitionDuration: '0.01ms !important',
        scrollBehavior: 'auto !important',
      },
    },
  }),
  
  // Breakpoints for responsive design
  breakpoints: {
    xs: '30em',    // 480px
    sm: '48em',    // 768px
    md: '64em',    // 1024px
    lg: '74em',    // 1184px
    xl: '90em',    // 1440px
  },
  
  // Default radius for components
  defaultRadius: 'md',
  
  // Default gradient for components that support it
  defaultGradient: {
    from: 'devible-primary.6',
    to: 'devible-primary.8',
    deg: 135,
  },
  
  // Other settings
  cursorType: 'pointer',
  respectReducedMotion: true,
  
  // White and black colors override
  white: '#ffffff',
  black: '#000000',
};

export default devibleTheme;
