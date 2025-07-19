import React, { useRef, useEffect, useState, useCallback } from 'react';

/**
 * Enhanced Keyboard Navigation Hook
 * Provides comprehensive keyboard navigation for complex UI components
 */
export const useKeyboardNavigation = (containerRef) => {
  const [focusableElements, setFocusableElements] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(-1);
  
  useEffect(() => {
    if (!containerRef.current) return;
    
    const updateFocusableElements = () => {
      const selector = [
        'button:not([disabled])',
        'input:not([disabled])',
        'select:not([disabled])',
        'textarea:not([disabled])',
        '[tabindex]:not([tabindex="-1"])',
        '[role="button"]:not([disabled])',
        '.max-object-node',
        '.react-flow__node'
      ].join(', ');
      
      const elements = Array.from(containerRef.current.querySelectorAll(selector));
      setFocusableElements(elements);
    };
    
    updateFocusableElements();
    
    const observer = new MutationObserver(updateFocusableElements);
    observer.observe(containerRef.current, { childList: true, subtree: true });
    
    return () => observer.disconnect();
  }, [containerRef]);
  
  const handleKeyDown = useCallback((event) => {
    if (!focusableElements.length) return;
    
    switch (event.key) {
      case 'Tab':
        event.preventDefault();
        const nextIndex = event.shiftKey 
          ? (currentIndex - 1 + focusableElements.length) % focusableElements.length
          : (currentIndex + 1) % focusableElements.length;
        
        setCurrentIndex(nextIndex);
        focusableElements[nextIndex]?.focus();
        break;
        
      case 'Enter':
      case ' ':
        if (currentIndex >= 0) {
          event.preventDefault();
          focusableElements[currentIndex]?.click();
        }
        break;
        
      case 'Escape':
        event.preventDefault();
        // Close any open modals or return to main area
        document.querySelector('[role="main"]')?.focus();
        break;
    }
  }, [focusableElements, currentIndex]);
  
  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);
  
  return {
    currentFocusIndex: currentIndex,
    focusableElements,
    setFocusIndex: setCurrentIndex
  };
};

/**
 * Screen reader announcement utility
 */
export const announceToScreenReader = (message, priority = 'polite') => {
  const announcement = document.createElement('div');
  announcement.setAttribute('aria-live', priority);
  announcement.setAttribute('aria-atomic', 'true');
  announcement.className = 'sr-only';
  announcement.textContent = message;
  
  document.body.appendChild(announcement);
  
  setTimeout(() => {
    if (document.body.contains(announcement)) {
      document.body.removeChild(announcement);
    }
  }, 1000);
};

/**
 * Focus Management Hook
 * Handles focus restoration and management for modal dialogs and route changes
 */
export const useFocusManagement = () => {
  const previousFocusRef = useRef(null);
  
  const saveFocus = useCallback(() => {
    previousFocusRef.current = document.activeElement;
  }, []);
  
  const restoreFocus = useCallback(() => {
    if (previousFocusRef.current && typeof previousFocusRef.current.focus === 'function') {
      previousFocusRef.current.focus();
    }
  }, []);
  
  const trapFocus = useCallback((containerElement) => {
    if (!containerElement) return;
    
    const focusableElements = containerElement.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];
    
    const handleTabKey = (event) => {
      if (event.key !== 'Tab') return;
      
      if (event.shiftKey) {
        if (document.activeElement === firstElement) {
          event.preventDefault();
          lastElement.focus();
        }
      } else {
        if (document.activeElement === lastElement) {
          event.preventDefault();
          firstElement.focus();
        }
      }
    };
    
    containerElement.addEventListener('keydown', handleTabKey);
    
    // Focus first element
    if (firstElement) {
      firstElement.focus();
    }
    
    return () => {
      containerElement.removeEventListener('keydown', handleTabKey);
    };
  }, []);
  
  return {
    saveFocus,
    restoreFocus,
    trapFocus
  };
};

/**
 * ARIA Live Region Manager
 * Manages announcements and status updates for screen readers
 */
export const useAriaLiveRegion = () => {
  const [announcements, setAnnouncements] = useState([]);
  
  const announce = useCallback((message, priority = 'polite') => {
    const id = Date.now().toString();
    const announcement = {
      id,
      message,
      priority,
      timestamp: Date.now()
    };
    
    setAnnouncements(prev => [...prev, announcement]);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      setAnnouncements(prev => prev.filter(a => a.id !== id));
    }, 5000);
  }, []);
  
  const announceError = useCallback((message) => {
    announce(message, 'assertive');
  }, [announce]);
  
  const announceSuccess = useCallback((message) => {
    announce(message, 'polite');
  }, [announce]);
  
  return {
    announcements,
    announce,
    announceError,
    announceSuccess
  };
};

/**
 * Color Contrast Checker
 * Validates WCAG contrast requirements
 */
export const checkColorContrast = (foreground, background) => {
  // Convert hex to RGB
  const hexToRgb = (hex) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : null;
  };
  
  // Calculate relative luminance
  const getLuminance = (r, g, b) => {
    const [rs, gs, bs] = [r, g, b].map(c => {
      c = c / 255;
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
  };
  
  const fg = hexToRgb(foreground);
  const bg = hexToRgb(background);
  
  if (!fg || !bg) return null;
  
  const fgLuminance = getLuminance(fg.r, fg.g, fg.b);
  const bgLuminance = getLuminance(bg.r, bg.g, bg.b);
  
  const contrast = (Math.max(fgLuminance, bgLuminance) + 0.05) / 
                   (Math.min(fgLuminance, bgLuminance) + 0.05);
  
  return {
    ratio: contrast,
    wcagAA: contrast >= 4.5,
    wcagAAA: contrast >= 7,
    wcagAALarge: contrast >= 3
  };
};

/**
 * Reduced Motion Hook
 * Respects user's motion preferences
 */
export const useReducedMotion = () => {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);
  
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);
    
    const handleChange = (event) => {
      setPrefersReducedMotion(event.matches);
    };
    
    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);
  
  return prefersReducedMotion;
};

/**
 * High Contrast Detection Hook
 */
export const useHighContrast = () => {
  const [prefersHighContrast, setPrefersHighContrast] = useState(false);
  
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-contrast: high)');
    setPrefersHighContrast(mediaQuery.matches);
    
    const handleChange = (event) => {
      setPrefersHighContrast(event.matches);
    };
    
    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);
  
  return prefersHighContrast;
};

export default {
  useKeyboardNavigation,
  announceToScreenReader,
  useFocusManagement,
  useAriaLiveRegion,
  checkColorContrast,
  useReducedMotion,
  useHighContrast
};
