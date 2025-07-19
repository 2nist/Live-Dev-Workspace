# Devible Branding & SVG Icon Customization Guide

## SVG Basics

### Core SVG Attributes
```xml
<svg 
  width={size}           // Physical width
  height={size}          // Physical height  
  viewBox="0 0 24 24"    // Coordinate system (x y width height)
  fill="none"            // Default fill color
  xmlns="http://www.w3.org/2000/svg"  // SVG namespace declaration
>
```

### Path Elements
```xml
<path 
  d="M8 5.14v13.72L19 12L8 5.14z"  // Path data (move, line, curve commands)
  fill={color}                        // Fill color
  stroke={color}                      // Outline color
  strokeWidth="2"                     // Outline thickness
  fillRule="evenodd"                  // How overlapping paths are filled
/>
```

## Branding Customization Options

### 1. Color System
Your icons already use CSS custom properties for brand colors:
- `var(--devible-primary-600)`
- `var(--devible-secondary-500)` 
- `var(--devible-tertiary-500)`
- `var(--devible-success)`
- `var(--devible-error)`
- `var(--devible-warning)`

### 2. Icon Styling Techniques

#### Solid Fill Icons
```jsx
<path d="..." fill={color} />
```

#### Outlined Icons  
```jsx
<path d="..." stroke={color} strokeWidth="2" fill="none" />
```

#### Gradient Fill
```jsx
<defs>
  <linearGradient id="brand-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stopColor="var(--devible-primary-600)"/>
    <stop offset="100%" stopColor="var(--devible-secondary-500)"/>
  </linearGradient>
</defs>
<path d="..." fill="url(#brand-gradient)" />
```

#### Drop Shadow & Effects
```jsx
<defs>
  <filter id="drop-shadow">
    <feDropShadow dx="2" dy="2" stdDeviation="3" floodOpacity="0.3"/>
  </filter>
</defs>
<path d="..." filter="url(#drop-shadow)" />
```

### 3. Brand-Specific Enhancements

#### Add Brand Gradients
```jsx
export const BrandedPlayIcon = ({ size = 24, className = '' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" className={className}>
    <defs>
      <linearGradient id="play-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="var(--devible-primary-500)"/>
        <stop offset="50%" stopColor="var(--devible-secondary-400)"/>
        <stop offset="100%" stopColor="var(--devible-tertiary-400)"/>
      </linearGradient>
    </defs>
    <path 
      d="M8 5.14v13.72L19 12L8 5.14z" 
      fill="url(#play-gradient)"
    />
  </svg>
);
```

#### Add Animation
```jsx
export const AnimatedRecordIcon = ({ size = 24, className = '' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" className={className}>
    <circle cx="12" cy="12" r="8" fill="#ef4444">
      <animate attributeName="r" values="6;8;6" dur="2s" repeatCount="indefinite"/>
    </circle>
  </svg>
);
```

## CSS Styling Integration

### Icon-Specific CSS Classes
```css
.devible-icon {
  transition: all 0.2s ease;
}

.devible-icon:hover {
  transform: scale(1.1);
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
}

.devible-logo {
  filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));
}
```

### Brand Color Variables
```css
:root {
  --devible-primary-500: #3b82f6;
  --devible-primary-600: #2563eb;
  --devible-secondary-400: #a855f7;
  --devible-secondary-500: #8b5cf6;
  --devible-tertiary-400: #06b6d4;
  --devible-tertiary-500: #0891b2;
}
```

## Icon Creation & Editing Tools

### 1. Design Tools
- **Figma** (free) - Great for icon design with SVG export
- **Adobe Illustrator** - Professional vector editor
- **Inkscape** (free) - Open-source SVG editor
- **SVG-Edit** (browser-based) - Simple online editor

### 2. SVG Optimization
- **SVGO** - Command-line SVG optimizer
- **SVG OMG** - Web-based SVG optimizer

### 3. Path Editing
SVG paths use these commands:
- `M` = Move to
- `L` = Line to  
- `H` = Horizontal line
- `V` = Vertical line
- `C` = Cubic bezier curve
- `Q` = Quadratic bezier curve
- `A` = Arc
- `Z` = Close path

Example: `"M8 5.14v13.72L19 12L8 5.14z"`
- Move to (8, 5.14)
- Draw vertical line 13.72 units down
- Line to (19, 12)  
- Line back to (8, 5.14)
- Close path

## Advanced Branding Techniques

### 1. Dynamic Color System
```jsx
export const ThemeAwareIcon = ({ icon: Icon, theme = 'light', ...props }) => {
  const colorMap = {
    light: 'var(--devible-primary-600)',
    dark: 'var(--devible-primary-400)',
    brand: 'url(#brand-gradient)'
  };
  
  return <Icon color={colorMap[theme]} {...props} />;
};
```

### 2. Context-Aware Icons
```jsx
export const StatusAwareIcon = ({ status, ...props }) => {
  const statusIcons = {
    success: ConnectedIcon,
    error: DisconnectedIcon,
    warning: WarningIcon,
    loading: LoadingIcon
  };
  
  const Icon = statusIcons[status] || HelpIcon;
  return <Icon {...props} />;
};
```

### 3. Icon Variants System
```jsx
export const createIconVariant = (baseIcon, variant = {}) => {
  const { gradient, shadow, animation, ...iconProps } = variant;
  
  return ({ ...props }) => (
    <svg {...iconProps} {...props}>
      {gradient && (
        <defs>
          <linearGradient id={gradient.id} {...gradient.props}>
            {gradient.stops.map((stop, i) => (
              <stop key={i} {...stop} />
            ))}
          </linearGradient>
        </defs>
      )}
      {/* Render base icon with modifications */}
    </svg>
  );
};
```

## Implementation Examples

### Brand-Consistent Play Button
```jsx
export const BrandPlayIcon = ({ size = 24, variant = 'default' }) => {
  const variants = {
    default: { fill: 'var(--devible-primary-500)' },
    gradient: { fill: 'url(#devible-gradient)' },
    outlined: { fill: 'none', stroke: 'var(--devible-primary-500)', strokeWidth: 2 }
  };
  
  return (
    <svg width={size} height={size} viewBox="0 0 24 24">
      <defs>
        <linearGradient id="devible-gradient">
          <stop offset="0%" stopColor="var(--devible-primary-600)"/>
          <stop offset="100%" stopColor="var(--devible-secondary-500)"/>
        </linearGradient>
      </defs>
      <path 
        d="M8 5.14v13.72L19 12L8 5.14z" 
        {...variants[variant]}
      />
    </svg>
  );
};
```

## Next Steps for Your Branding

1. **Define Brand Colors** - Create a comprehensive color system
2. **Create Icon Variants** - Solid, outlined, gradient versions
3. **Add Animations** - Subtle hover effects and state transitions  
4. **Consistency System** - Standardize sizing, spacing, and visual weight
5. **Accessibility** - Ensure proper contrast and alternative text
6. **Documentation** - Create a style guide for your icon system
