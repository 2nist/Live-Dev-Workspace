import React from 'react';

/**
 * Enhanced Branded Icon Components
 * Demonstrates advanced SVG styling techniques for the Devible brand
 */

// === BRAND COLORS & GRADIENTS ===

export const BrandGradients = () => (
  <defs>
    {/* Primary Brand Gradient */}
    <linearGradient id="devible-primary" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stopColor="var(--devible-primary-600)" />
      <stop offset="50%" stopColor="var(--devible-secondary-500)" />
      <stop offset="100%" stopColor="var(--devible-tertiary-500)" />
    </linearGradient>
    
    {/* Success Gradient */}
    <linearGradient id="devible-success" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stopColor="#10b981" />
      <stop offset="100%" stopColor="#059669" />
    </linearGradient>
    
    {/* Warning Gradient */}
    <linearGradient id="devible-warning" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stopColor="#f59e0b" />
      <stop offset="100%" stopColor="#d97706" />
    </linearGradient>
    
    {/* Error Gradient */}
    <linearGradient id="devible-error" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stopColor="#ef4444" />
      <stop offset="100%" stopColor="#dc2626" />
    </linearGradient>
    
    {/* Metallic Gradient for 3D Effect */}
    <linearGradient id="devible-metallic" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stopColor="#f8fafc" />
      <stop offset="25%" stopColor="#e2e8f0" />
      <stop offset="50%" stopColor="#cbd5e1" />
      <stop offset="75%" stopColor="#94a3b8" />
      <stop offset="100%" stopColor="#64748b" />
    </linearGradient>
    
    {/* Drop Shadow Filter */}
    <filter id="devible-shadow" x="-50%" y="-50%" width="200%" height="200%">
      <feDropShadow dx="2" dy="2" stdDeviation="3" floodOpacity="0.25" floodColor="var(--devible-primary-800)" />
    </filter>
    
    {/* Glow Effect Filter */}
    <filter id="devible-glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge> 
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
);

// === ENHANCED BRANDED ICONS ===

export const BrandedPlayIcon = ({ 
  size = 24, 
  variant = 'gradient', 
  animated = false,
  className = '' 
}) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    className={`devible-icon devible-play-icon ${className}`}
    xmlns="http://www.w3.org/2000/svg"
  >
    <BrandGradients />
    <path 
      d="M8 5.14v13.72L19 12L8 5.14z" 
      fill={variant === 'gradient' ? 'url(#devible-primary)' : 'var(--devible-primary-500)'}
      filter={variant === 'glow' ? 'url(#devible-glow)' : 'url(#devible-shadow)'}
      className={animated ? 'animate-pulse' : ''}
    />
  </svg>
);

export const BrandedRecordIcon = ({ 
  size = 24, 
  variant = 'gradient',
  recording = false,
  className = '' 
}) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    className={`devible-icon devible-record-icon ${className}`}
    xmlns="http://www.w3.org/2000/svg"
  >
    <BrandGradients />
    <circle 
      cx="12" 
      cy="12" 
      r="8" 
      fill={variant === 'gradient' ? 'url(#devible-error)' : '#ef4444'}
      filter="url(#devible-shadow)"
    >
      {recording && (
        <animate 
          attributeName="r" 
          values="6;8;6" 
          dur="2s" 
          repeatCount="indefinite"
        />
      )}
    </circle>
    {recording && (
      <circle 
        cx="12" 
        cy="12" 
        r="10" 
        fill="none" 
        stroke="url(#devible-error)" 
        strokeWidth="1" 
        opacity="0.5"
      >
        <animate 
          attributeName="r" 
          values="8;12;8" 
          dur="2s" 
          repeatCount="indefinite"
        />
        <animate 
          attributeName="opacity" 
          values="0.5;0;0.5" 
          dur="2s" 
          repeatCount="indefinite"
        />
      </circle>
    )}
  </svg>
);

export const BrandedMixerIcon = ({ 
  size = 24, 
  variant = '3d',
  className = '' 
}) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    className={`devible-icon devible-mixer-icon ${className}`}
    xmlns="http://www.w3.org/2000/svg"
  >
    <BrandGradients />
    
    {/* Channel Strips */}
    <rect 
      x="3" y="2" width="2" height="20" 
      fill={variant === '3d' ? 'url(#devible-metallic)' : 'var(--devible-neutral-600)'} 
      rx="1"
      filter="url(#devible-shadow)"
    />
    <rect 
      x="11" y="2" width="2" height="20" 
      fill={variant === '3d' ? 'url(#devible-metallic)' : 'var(--devible-neutral-600)'} 
      rx="1"
      filter="url(#devible-shadow)"
    />
    <rect 
      x="19" y="2" width="2" height="20" 
      fill={variant === '3d' ? 'url(#devible-metallic)' : 'var(--devible-neutral-600)'} 
      rx="1"
      filter="url(#devible-shadow)"
    />
    
    {/* Fader Knobs */}
    <circle 
      cx="4" cy="8" r="2" 
      fill="url(#devible-primary)"
      filter="url(#devible-shadow)"
    />
    <circle 
      cx="12" cy="12" r="2" 
      fill="url(#devible-secondary)"
      filter="url(#devible-shadow)"
    />
    <circle 
      cx="20" cy="6" r="2" 
      fill="url(#devible-tertiary)"
      filter="url(#devible-shadow)"
    />
    
    {/* Indicator Dots */}
    <circle cx="4" cy="8" r="0.5" fill="white" opacity="0.8"/>
    <circle cx="12" cy="12" r="0.5" fill="white" opacity="0.8"/>
    <circle cx="20" cy="6" r="0.5" fill="white" opacity="0.8"/>
  </svg>
);

export const BrandedWaveformIcon = ({ 
  size = 24, 
  animated = false,
  className = '' 
}) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    className={`devible-icon devible-waveform-icon ${className}`}
    xmlns="http://www.w3.org/2000/svg"
  >
    <BrandGradients />
    
    {[
      { x: 2, height: 4, delay: '0s' },
      { x: 5, height: 8, delay: '0.1s' },
      { x: 8, height: 12, delay: '0.2s' },
      { x: 11, height: 16, delay: '0.3s' },
      { x: 14, height: 10, delay: '0.4s' },
      { x: 17, height: 6, delay: '0.5s' },
      { x: 20, height: 2, delay: '0.6s' }
    ].map((bar, index) => (
      <rect 
        key={index}
        x={bar.x} 
        y={12 - bar.height / 2} 
        width="1.5" 
        height={bar.height} 
        fill="url(#devible-primary)"
        rx="0.75"
        filter="url(#devible-shadow)"
      >
        {animated && (
          <animateTransform
            attributeName="transform"
            type="scale"
            values="1,1;1,0.5;1,1"
            dur="1.5s"
            repeatCount="indefinite"
            begin={bar.delay}
          />
        )}
      </rect>
    ))}
  </svg>
);

export const BrandedStatusIcon = ({ 
  status = 'connected', 
  size = 24,
  animated = true,
  className = '' 
}) => {
  const statusConfig = {
    connected: {
      gradient: 'devible-success',
      path: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zM9.29 16.29L5.7 12.7c-.39-.39-.39-1.02 0-1.41.39-.39 1.02-.39 1.41 0L10 14.17l6.88-6.88c.39-.39 1.02-.39 1.41 0 .39.39.39 1.02 0 1.41l-7.59 7.59c-.38.39-1.02.39-1.41 0z"
    },
    disconnected: {
      gradient: 'devible-error',
      path: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm3.5 6L12 10.5 8.5 8 7 9.5 10.5 12 7 15.5 8.5 17 12 13.5 15.5 17 17 15.5 13.5 12 17 8.5 15.5 6z"
    },
    warning: {
      gradient: 'devible-warning',
      path: "M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"
    }
  };
  
  const config = statusConfig[status];
  
  return (
    <svg 
      width={size} 
      height={size} 
      viewBox="0 0 24 24" 
      fill="none" 
      className={`devible-icon devible-status-icon status-${status} ${className}`}
      xmlns="http://www.w3.org/2000/svg"
    >
      <BrandGradients />
      <path 
        d={config.path}
        fill={`url(#${config.gradient})`}
        filter="url(#devible-shadow)"
      >
        {animated && status === 'connected' && (
          <animate 
            attributeName="opacity" 
            values="0.7;1;0.7" 
            dur="2s" 
            repeatCount="indefinite"
          />
        )}
      </path>
    </svg>
  );
};

// === LOGO WITH ADVANCED BRANDING ===

export const EnhancedDevibleLogo = ({ 
  size = 32, 
  variant = 'full',
  animated = false,
  className = '' 
}) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 32 32" 
    fill="none" 
    className={`devible-logo devible-logo-${variant} ${className}`}
    xmlns="http://www.w3.org/2000/svg"
  >
    <BrandGradients />
    
    {/* Background with gradient */}
    <rect 
      x="2" y="2" width="28" height="28" rx="6" 
      fill="url(#devible-primary)"
      filter="url(#devible-shadow)"
    >
      {animated && (
        <animate 
          attributeName="rx" 
          values="6;8;6" 
          dur="4s" 
          repeatCount="indefinite"
        />
      )}
    </rect>
    
    {/* Main "D" letter */}
    <path 
      d="M8 24V8h5.6c3.2 0 5.6 2.4 5.6 5.6v4.8c0 3.2-2.4 5.6-5.6 5.6H8z" 
      fill="white"
      filter="url(#devible-shadow)"
    />
    
    {/* Accent circle */}
    <circle 
      cx="21" cy="13" r="3" 
      fill="white"
      filter="url(#devible-shadow)"
    >
      {animated && (
        <animateTransform
          attributeName="transform"
          type="rotate"
          values="0 21 13;360 21 13"
          dur="8s"
          repeatCount="indefinite"
        />
      )}
    </circle>
    
    {/* Bottom accent */}
    <rect 
      x="19" y="18" width="4" height="4" 
      fill="white" rx="1"
      filter="url(#devible-shadow)"
    />
    
    {/* Optional glow effect */}
    {variant === 'glow' && (
      <rect 
        x="2" y="2" width="28" height="28" rx="6" 
        fill="none"
        stroke="url(#devible-primary)"
        strokeWidth="1"
        opacity="0.5"
        filter="url(#devible-glow)"
      />
    )}
  </svg>
);

// === UTILITY FUNCTIONS ===

/**
 * Create a branded version of any icon
 */
export const withBranding = (IconComponent, brandOptions = {}) => {
  const {
    gradient = 'devible-primary',
    shadow = true,
    glow = false,
    animated = false
  } = brandOptions;
  
  return (props) => (
    <IconComponent 
      {...props}
      className={`branded-icon ${props.className || ''}`}
      style={{
        filter: shadow ? 'url(#devible-shadow)' : glow ? 'url(#devible-glow)' : 'none',
        ...props.style
      }}
    />
  );
};

/**
 * Icon with dynamic theming
 */
export const ThemedIcon = ({ 
  icon: Icon, 
  theme = 'auto', 
  status,
  ...props 
}) => {
  const getThemeColor = () => {
    if (status) {
      return {
        connected: 'url(#devible-success)',
        disconnected: 'url(#devible-error)',
        warning: 'url(#devible-warning)'
      }[status];
    }
    
    return theme === 'auto' ? 'currentColor' : `url(#devible-${theme})`;
  };
  
  return (
    <Icon 
      {...props}
      color={getThemeColor()}
      className={`themed-icon theme-${theme} ${props.className || ''}`}
    />
  );
};

// Export enhanced icons
export const BrandedIcons = {
  Play: BrandedPlayIcon,
  Record: BrandedRecordIcon,
  Mixer: BrandedMixerIcon,
  Waveform: BrandedWaveformIcon,
  Status: BrandedStatusIcon,
  Logo: EnhancedDevibleLogo,
  
  // Utilities
  withBranding,
  ThemedIcon,
  BrandGradients
};

export default BrandedIcons;
