import React from 'react';

/**
 * Devible SVG Icon Library
 * Professional iconography matching the Devible brand aesthetic
 * Replaces emoji usage with scalable, consistent SVG icons
 */

// === CORE INTERFACE ICONS ===

export const PlayIcon = ({ size = 24, color = 'currentColor', className = '' }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    className={`devible-icon ${className}`}
    xmlns="http://www.w3.org/2000/svg"
  >
    <path 
      d="M8 5.14v13.72L19 12L8 5.14z" 
      fill={color}
      fillRule="evenodd"
      clipRule="evenodd"
    />
  </svg>
);

export const PauseIcon = ({ size = 24, color = 'currentColor', className = '' }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    className={`devible-icon ${className}`}
    xmlns="http://www.w3.org/2000/svg"
  >
    <rect x="6" y="4" width="4" height="16" fill={color} rx="1"/>
    <rect x="14" y="4" width="4" height="16" fill={color} rx="1"/>
  </svg>
);

export const StopIcon = ({ size = 24, color = 'currentColor', className = '' }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    className={`devible-icon ${className}`}
    xmlns="http://www.w3.org/2000/svg"
  >
    <rect x="5" y="5" width="14" height="14" fill={color} rx="2"/>
  </svg>
);

export const RecordIcon = ({ size = 24, color = '#ef4444', className = '' }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    className={`devible-icon ${className}`}
    xmlns="http://www.w3.org/2000/svg"
  >
    <circle cx="12" cy="12" r="8" fill={color}/>
  </svg>
);

// === AUDIO/MUSIC PRODUCTION ICONS ===

export const WaveformIcon = ({ size = 24, color = 'currentColor', className = '' }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    className={`devible-icon ${className}`}
    xmlns="http://www.w3.org/2000/svg"
  >
    <rect x="2" y="10" width="1.5" height="4" fill={color} rx="0.75"/>
    <rect x="5" y="8" width="1.5" height="8" fill={color} rx="0.75"/>
    <rect x="8" y="6" width="1.5" height="12" fill={color} rx="0.75"/>
    <rect x="11" y="4" width="1.5" height="16" fill={color} rx="0.75"/>
    <rect x="14" y="7" width="1.5" height="10" fill={color} rx="0.75"/>
    <rect x="17" y="9" width="1.5" height="6" fill={color} rx="0.75"/>
    <rect x="20" y="11" width="1.5" height="2" fill={color} rx="0.75"/>
  </svg>
);

export const MixerIcon = ({ size = 24, color = 'currentColor', className = '' }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    className={`devible-icon ${className}`}
    xmlns="http://www.w3.org/2000/svg"
  >
    <rect x="3" y="2" width="2" height="20" fill={color} rx="1"/>
    <rect x="11" y="2" width="2" height="20" fill={color} rx="1"/>
    <rect x="19" y="2" width="2" height="20" fill={color} rx="1"/>
    <circle cx="4" cy="8" r="2" fill="var(--devible-secondary-500)"/>
    <circle cx="12" cy="12" r="2" fill="var(--devible-secondary-500)"/>
    <circle cx="20" cy="6" r="2" fill="var(--devible-secondary-500)"/>
  </svg>
);

export const SynthIcon = ({ size = 24, color = 'currentColor', className = '' }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    className={`devible-icon ${className}`}
    xmlns="http://www.w3.org/2000/svg"
  >
    <rect x="2" y="8" width="20" height="8" stroke={color} strokeWidth="2" fill="none" rx="2"/>
    <rect x="4" y="10" width="2" height="4" fill={color} rx="0.5"/>
    <rect x="7" y="10" width="2" height="4" fill={color} rx="0.5"/>
    <rect x="10" y="10" width="2" height="4" fill={color} rx="0.5"/>
    <rect x="13" y="10" width="2" height="4" fill={color} rx="0.5"/>
    <rect x="16" y="10" width="2" height="4" fill={color} rx="0.5"/>
    <rect x="19" y="10" width="2" height="4" fill={color} rx="0.5"/>
    <circle cx="6" cy="5" r="1" fill="var(--devible-tertiary-500)"/>
    <circle cx="12" cy="5" r="1" fill="var(--devible-tertiary-500)"/>
    <circle cx="18" cy="5" r="1" fill="var(--devible-tertiary-500)"/>
  </svg>
);

export const EffectIcon = ({ size = 24, color = 'currentColor', className = '' }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    className={`devible-icon ${className}`}
    xmlns="http://www.w3.org/2000/svg"
  >
    <path 
      d="M12 2L15.09 8.26L22 9L17 14.74L18.18 21.02L12 17.27L5.82 21.02L7 14.74L2 9L8.91 8.26L12 2Z" 
      stroke={color} 
      strokeWidth="2" 
      fill="none"
    />
    <circle cx="12" cy="12" r="3" fill="var(--devible-secondary-500)"/>
  </svg>
);

// === CONNECTIVITY & STATUS ICONS ===

export const ConnectedIcon = ({ size = 24, color = 'var(--devible-success)', className = '' }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    className={`devible-icon ${className}`}
    xmlns="http://www.w3.org/2000/svg"
  >
    <path 
      d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zM9.29 16.29L5.7 12.7c-.39-.39-.39-1.02 0-1.41.39-.39 1.02-.39 1.41 0L10 14.17l6.88-6.88c.39-.39 1.02-.39 1.41 0 .39.39.39 1.02 0 1.41l-7.59 7.59c-.38.39-1.02.39-1.41 0z" 
      fill={color}
    />
  </svg>
);

export const DisconnectedIcon = ({ size = 24, color = 'var(--devible-error)', className = '' }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    className={`devible-icon ${className}`}
    xmlns="http://www.w3.org/2000/svg"
  >
    <path 
      d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm3.5 6L12 10.5 8.5 8 7 9.5 10.5 12 7 15.5 8.5 17 12 13.5 15.5 17 17 15.5 13.5 12 17 8.5 15.5 6z" 
      fill={color}
    />
  </svg>
);

export const WarningIcon = ({ size = 24, color = 'var(--devible-warning)', className = '' }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    className={`devible-icon ${className}`}
    xmlns="http://www.w3.org/2000/svg"
  >
    <path 
      d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z" 
      fill={color}
    />
  </svg>
);

// === NAVIGATION & UI ICONS ===

export const MenuIcon = ({ size = 24, color = 'currentColor', className = '' }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    className={`devible-icon ${className}`}
    xmlns="http://www.w3.org/2000/svg"
  >
    <path 
      d="M3 12h18M3 6h18M3 18h18" 
      stroke={color} 
      strokeWidth="2" 
      strokeLinecap="round"
    />
  </svg>
);

export const CloseIcon = ({ size = 24, color = 'currentColor', className = '' }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    className={`devible-icon ${className}`}
    xmlns="http://www.w3.org/2000/svg"
  >
    <path 
      d="M18 6L6 18M6 6l12 12" 
      stroke={color} 
      strokeWidth="2" 
      strokeLinecap="round"
    />
  </svg>
);

export const SettingsIcon = ({ size = 24, color = 'currentColor', className = '' }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    className={`devible-icon ${className}`}
    xmlns="http://www.w3.org/2000/svg"
  >
    <circle cx="12" cy="12" r="3" stroke={color} strokeWidth="2" fill="none"/>
    <path 
      d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" 
      stroke={color} 
      strokeWidth="2" 
      fill="none"
    />
  </svg>
);

export const HelpIcon = ({ size = 24, color = 'currentColor', className = '' }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    className={`devible-icon ${className}`}
    xmlns="http://www.w3.org/2000/svg"
  >
    <circle cx="12" cy="12" r="10" stroke={color} strokeWidth="2" fill="none"/>
    <path 
      d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" 
      stroke={color} 
      strokeWidth="2" 
      strokeLinecap="round" 
      fill="none"
    />
    <circle cx="12" cy="17" r="1" fill={color}/>
  </svg>
);

// === ACTION ICONS ===

export const AddIcon = ({ size = 24, color = 'currentColor', className = '' }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    className={`devible-icon ${className}`}
    xmlns="http://www.w3.org/2000/svg"
  >
    <circle cx="12" cy="12" r="10" stroke={color} strokeWidth="2" fill="none"/>
    <path 
      d="M12 8v8M8 12h8" 
      stroke={color} 
      strokeWidth="2" 
      strokeLinecap="round"
    />
  </svg>
);

export const DeleteIcon = ({ size = 24, color = 'var(--devible-error)', className = '' }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    className={`devible-icon ${className}`}
    xmlns="http://www.w3.org/2000/svg"
  >
    <path 
      d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2m3 0v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6h14zM10 11v6M14 11v6" 
      stroke={color} 
      strokeWidth="2" 
      strokeLinecap="round"
    />
  </svg>
);

export const TestIcon = ({ size = 24, color = 'currentColor', className = '' }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    className={`devible-icon ${className}`}
    xmlns="http://www.w3.org/2000/svg"
  >
    {/* Test tube body */}
    <path 
      d="M14.5 3a1 1 0 0 1 1 1v1.5M9.5 3a1 1 0 0 0-1 1v1.5" 
      stroke={color} 
      strokeWidth="2" 
      strokeLinecap="round"
    />
    <path 
      d="M8.5 5.5v2c0 .5.5 1 1 1h5c.5 0 1-.5 1-1v-2" 
      stroke={color} 
      strokeWidth="2" 
      strokeLinecap="round"
    />
    {/* Test tube main body */}
    <path 
      d="M10 8.5v8c0 2.5 1.5 4.5 4 4.5s4-2 4-4.5v-8" 
      stroke={color} 
      strokeWidth="2" 
      strokeLinecap="round"
      fill="none"
    />
    {/* Liquid inside */}
    <rect x="11" y="12" width="6" height="6" fill={color} opacity="0.3" rx="1"/>
    <circle cx="13" cy="14" r="1" fill={color} opacity="0.6"/>
    <circle cx="16" cy="16" r="0.5" fill={color} opacity="0.8"/>
  </svg>
);

export const EditIcon = ({ size = 24, color = 'currentColor', className = '' }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    className={`devible-icon ${className}`}
    xmlns="http://www.w3.org/2000/svg"
  >
    <path 
      d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" 
      stroke={color} 
      strokeWidth="2" 
      strokeLinecap="round" 
      fill="none"
    />
    <path 
      d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" 
      stroke={color} 
      strokeWidth="2" 
      strokeLinecap="round" 
      fill="none"
    />
  </svg>
);

export const DocumentIcon = ({ size = 24, color = 'currentColor', className = '' }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    className={`devible-icon ${className}`}
    xmlns="http://www.w3.org/2000/svg"
  >
    <path 
      d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" 
      stroke={color} 
      strokeWidth="2" 
      strokeLinecap="round" 
      fill="none"
    />
    <polyline points="14,2 14,8 20,8" stroke={color} strokeWidth="2" fill="none"/>
    <line x1="16" y1="13" x2="8" y2="13" stroke={color} strokeWidth="2"/>
    <line x1="16" y1="17" x2="8" y2="17" stroke={color} strokeWidth="2"/>
    <polyline points="10,9 9,9 8,9" stroke={color} strokeWidth="2"/>
  </svg>
);

export const CopyIcon = ({ size = 24, color = 'currentColor', className = '' }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    className={`devible-icon ${className}`}
    xmlns="http://www.w3.org/2000/svg"
  >
    <rect 
      x="9" 
      y="9" 
      width="13" 
      height="13" 
      rx="2" 
      ry="2" 
      stroke={color} 
      strokeWidth="2" 
      fill="none"
    />
    <path 
      d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" 
      stroke={color} 
      strokeWidth="2" 
      strokeLinecap="round" 
      fill="none"
    />
  </svg>
);

// === FILE & PROJECT ICONS ===

export const SaveIcon = ({ size = 24, color = 'currentColor', className = '' }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    className={`devible-icon ${className}`}
    xmlns="http://www.w3.org/2000/svg"
  >
    <path 
      d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" 
      stroke={color} 
      strokeWidth="2" 
      strokeLinecap="round" 
      fill="none"
    />
    <polyline points="17,21 17,13 7,13 7,21" stroke={color} strokeWidth="2" fill="none"/>
    <polyline points="7,3 7,8 15,8" stroke={color} strokeWidth="2" fill="none"/>
  </svg>
);

export const LoadIcon = ({ size = 24, color = 'currentColor', className = '' }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    className={`devible-icon ${className}`}
    xmlns="http://www.w3.org/2000/svg"
  >
    <path 
      d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" 
      stroke={color} 
      strokeWidth="2" 
      strokeLinecap="round" 
      fill="none"
    />
    <polyline points="14,2 14,8 20,8" stroke={color} strokeWidth="2" fill="none"/>
    <line x1="16" y1="13" x2="8" y2="13" stroke={color} strokeWidth="2"/>
    <line x1="16" y1="17" x2="8" y2="17" stroke={color} strokeWidth="2"/>
    <polyline points="10,9 9,9 8,9" stroke={color} strokeWidth="2"/>
  </svg>
);

export const ExportIcon = ({ size = 24, color = 'currentColor', className = '' }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    className={`devible-icon ${className}`}
    xmlns="http://www.w3.org/2000/svg"
  >
    <path 
      d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5-5 5 5M12 15V5" 
      stroke={color} 
      strokeWidth="2" 
      strokeLinecap="round" 
      fill="none"
    />
  </svg>
);

// === BRAND & LOGO ICONS ===

export const DevibleLogoIcon = ({ size = 32, className = '' }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 32 32" 
    fill="none" 
    className={`devible-logo ${className}`}
    xmlns="http://www.w3.org/2000/svg"
  >
    <defs>
      <linearGradient id="devible-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="var(--devible-primary-600)"/>
        <stop offset="50%" stopColor="var(--devible-secondary-500)"/>
        <stop offset="100%" stopColor="var(--devible-tertiary-500)"/>
      </linearGradient>
    </defs>
    <rect x="2" y="2" width="28" height="28" rx="6" fill="url(#devible-gradient)"/>
    <path 
      d="M8 24V8h5.6c3.2 0 5.6 2.4 5.6 5.6v4.8c0 3.2-2.4 5.6-5.6 5.6H8z" 
      fill="white"
    />
    <circle cx="21" cy="13" r="3" fill="white"/>
    <rect x="19" y="18" width="4" height="4" fill="white" rx="1"/>
  </svg>
);

export const AbletonLiveIcon = ({ size = 24, color = 'currentColor', className = '' }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    className={`devible-icon ${className}`}
    xmlns="http://www.w3.org/2000/svg"
  >
    <rect x="2" y="4" width="4" height="16" fill={color} rx="1"/>
    <rect x="8" y="8" width="4" height="12" fill={color} rx="1"/>
    <rect x="14" y="6" width="4" height="14" fill={color} rx="1"/>
    <rect x="20" y="10" width="2" height="8" fill={color} rx="1"/>
  </svg>
);

// === ACCESSIBILITY ICONS ===

export const AccessibilityIcon = ({ size = 24, color = 'currentColor', className = '' }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    className={`devible-icon ${className}`}
    xmlns="http://www.w3.org/2000/svg"
  >
    <circle cx="12" cy="4" r="2" fill={color}/>
    <path 
      d="M19 13v-2c0-1.1-.9-2-2-2h-4l3-4H9l3 4H8c-1.1 0-2 .9-2 2v2M7 19h2v-6H7v6zM15 19h2v-6h-2v6z" 
      fill={color}
    />
  </svg>
);

export const KeyboardIcon = ({ size = 24, color = 'currentColor', className = '' }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    className={`devible-icon ${className}`}
    xmlns="http://www.w3.org/2000/svg"
  >
    <rect x="2" y="6" width="20" height="12" rx="2" stroke={color} strokeWidth="2" fill="none"/>
    <line x1="6" y1="10" x2="6.01" y2="10" stroke={color} strokeWidth="2" strokeLinecap="round"/>
    <line x1="10" y1="10" x2="10.01" y2="10" stroke={color} strokeWidth="2" strokeLinecap="round"/>
    <line x1="14" y1="10" x2="14.01" y2="10" stroke={color} strokeWidth="2" strokeLinecap="round"/>
    <line x1="18" y1="10" x2="18.01" y2="10" stroke={color} strokeWidth="2" strokeLinecap="round"/>
    <line x1="8" y1="14" x2="16" y2="14" stroke={color} strokeWidth="2" strokeLinecap="round"/>
  </svg>
);

// === TOUCH & MOBILE ICONS ===

export const TouchIcon = ({ size = 24, color = 'currentColor', className = '' }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    className={`devible-icon ${className}`}
    xmlns="http://www.w3.org/2000/svg"
  >
    <path 
      d="M9 11H7a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2v-8a2 2 0 0 0-2-2h-2" 
      stroke={color} 
      strokeWidth="2" 
      fill="none"
    />
    <path 
      d="M9 7a3 3 0 0 1 6 0v4a3 3 0 0 1-6 0V7z" 
      stroke={color} 
      strokeWidth="2" 
      fill="none"
    />
  </svg>
);

export const GestureIcon = ({ size = 24, color = 'currentColor', className = '' }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    className={`devible-icon ${className}`}
    xmlns="http://www.w3.org/2000/svg"
  >
    <path 
      d="M18 15l-6-6M22 9L6 25M2 13l10-10" 
      stroke={color} 
      strokeWidth="2" 
      strokeLinecap="round"
    />
    <circle cx="18" cy="9" r="2" fill={color}/>
    <circle cx="6" cy="21" r="2" fill={color}/>
    <circle cx="8" cy="7" r="2" fill={color}/>
  </svg>
);

// === UTILITY COMPONENTS ===

/**
 * IconButton wrapper for consistent icon button styling
 */
export const IconButton = ({ 
  icon: Icon, 
  size = 24, 
  color = 'currentColor', 
  onClick, 
  disabled = false,
  variant = 'default',
  className = '',
  ariaLabel,
  ...props 
}) => {
  const baseClasses = 'devible-icon-button';
  const variantClasses = {
    default: 'btn-devible-icon-default',
    primary: 'btn-devible-icon-primary',
    secondary: 'btn-devible-icon-secondary',
    danger: 'btn-devible-icon-danger'
  };
  
  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]} ${className}`}
      onClick={onClick}
      disabled={disabled}
      aria-label={ariaLabel}
      {...props}
    >
      <Icon size={size} color={color} />
    </button>
  );
};

/**
 * Icon with status indicator
 */
export const StatusIcon = ({ 
  icon: Icon, 
  status = 'disconnected', 
  size = 24, 
  className = '' 
}) => {
  const statusColors = {
    connected: 'var(--devible-success)',
    disconnected: 'var(--devible-error)',
    warning: 'var(--devible-warning)',
    info: 'var(--devible-info)'
  };
  
  return (
    <div className={`status-icon-wrapper ${className}`}>
      <Icon size={size} color="currentColor" />
      <div 
        className={`status-indicator status-${status}`}
        style={{ backgroundColor: statusColors[status] }}
      />
    </div>
  );
};

// Export all icons for easy importing
export const DevibleIcons = {
  // Playback
  Play: PlayIcon,
  Pause: PauseIcon,
  Stop: StopIcon,
  Record: RecordIcon,
  
  // Audio
  Waveform: WaveformIcon,
  Mixer: MixerIcon,
  Synth: SynthIcon,
  Effect: EffectIcon,
  
  // Status
  Connected: ConnectedIcon,
  Disconnected: DisconnectedIcon,
  Warning: WarningIcon,
  
  // Navigation
  Menu: MenuIcon,
  Close: CloseIcon,
  Settings: SettingsIcon,
  Help: HelpIcon,
  
  // Actions
  Add: AddIcon,
  Delete: DeleteIcon,
  Edit: EditIcon,
  Copy: CopyIcon,
  Test: TestIcon,
  
  // Files
  Save: SaveIcon,
  Load: LoadIcon,
  Export: ExportIcon,
  Document: DocumentIcon,
  
  // Brand
  DevibleLogo: DevibleLogoIcon,
  AbletonLive: AbletonLiveIcon,
  
  // Accessibility
  Accessibility: AccessibilityIcon,
  Keyboard: KeyboardIcon,
  
  // Mobile
  Touch: TouchIcon,
  Gesture: GestureIcon,
  
  // Utility
  IconButton,
  StatusIcon
};

export default DevibleIcons;
