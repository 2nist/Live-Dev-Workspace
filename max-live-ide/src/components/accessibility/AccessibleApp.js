import React, { useRef, useEffect } from 'react';
import { MantineProvider } from '@mantine/core';
import { Notifications } from '@mantine/notifications';
import { useFocusManagement, useAriaLiveRegion, announceToScreenReader } from '../accessibility/AccessibilityHooks';

/**
 * Accessible App Wrapper Component
 * Provides comprehensive accessibility infrastructure for the entire application
 */
const AccessibleApp = ({ children }) => {
  const appRef = useRef(null);
  const skipLinkRef = useRef(null);
  const { saveFocus, restoreFocus, trapFocus } = useFocusManagement();
  const { announcements, announce, announceError, announceSuccess } = useAriaLiveRegion();
  
  // Track interaction method for appropriate focus styling
  useEffect(() => {
    let isMouseUser = false;
    
    const handleMouseDown = () => {
      isMouseUser = true;
      document.body.classList.add('mouse-user');
      document.body.classList.remove('keyboard-user');
    };
    
    const handleKeyDown = (event) => {
      if (event.key === 'Tab') {
        isMouseUser = false;
        document.body.classList.add('keyboard-user');
        document.body.classList.remove('mouse-user');
      }
    };
    
    document.addEventListener('mousedown', handleMouseDown);
    document.addEventListener('keydown', handleKeyDown);
    
    return () => {
      document.removeEventListener('mousedown', handleMouseDown);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, []);
  
  // Focus management for route changes
  useEffect(() => {
    const handleRouteChange = () => {
      // Announce page changes to screen readers
      const pageTitle = document.title || 'Devible - Max for Live IDE';
      announceToScreenReader(`Navigated to ${pageTitle}`);
      
      // Focus management
      const mainContent = document.querySelector('[role="main"]');
      if (mainContent) {
        mainContent.focus();
      }
    };
    
    // Listen for route changes (adjust based on your routing solution)
    window.addEventListener('popstate', handleRouteChange);
    
    // Initial page load announcement
    announceToScreenReader('Devible application loaded. Use Tab to navigate, or press Alt+1 for shortcuts.');
    
    return () => window.removeEventListener('popstate', handleRouteChange);
  }, []);
  
  // Global keyboard shortcuts
  useEffect(() => {
    const handleGlobalKeyDown = (event) => {
      // Alt + 1: Skip to main content
      if (event.altKey && event.key === '1') {
        event.preventDefault();
        const mainContent = document.querySelector('[role="main"]');
        if (mainContent) {
          mainContent.focus();
          announceToScreenReader('Moved to main content area');
        }
      }
      
      // Alt + 2: Skip to toolbar
      if (event.altKey && event.key === '2') {
        event.preventDefault();
        const toolbar = document.querySelector('[role="toolbar"]');
        if (toolbar) {
          toolbar.focus();
          announceToScreenReader('Moved to toolbar');
        }
      }
      
      // Alt + 3: Skip to object library
      if (event.altKey && event.key === '3') {
        event.preventDefault();
        const objectLibrary = document.querySelector('#object-library');
        if (objectLibrary) {
          objectLibrary.focus();
          announceToScreenReader('Moved to object library');
        }
      }
      
      // Escape: Close any modals or return to main
      if (event.key === 'Escape') {
        const modal = document.querySelector('[role="dialog"]');
        if (modal) {
          // Let modal handle its own escape
          return;
        }
        
        const mainContent = document.querySelector('[role="main"]');
        if (mainContent) {
          mainContent.focus();
          announceToScreenReader('Returned to main content');
        }
      }
      
      // F1: Show keyboard shortcuts help
      if (event.key === 'F1') {
        event.preventDefault();
        showKeyboardShortcutsHelp();
      }
    };
    
    document.addEventListener('keydown', handleGlobalKeyDown);
    return () => document.removeEventListener('keydown', handleGlobalKeyDown);
  }, []);
  
  const showKeyboardShortcutsHelp = () => {
    const shortcuts = [
      'Tab / Shift+Tab: Navigate between elements',
      'Enter / Space: Activate buttons and links',
      'Alt+1: Skip to main content',
      'Alt+2: Skip to toolbar', 
      'Alt+3: Skip to object library',
      'Escape: Close modals or return to main',
      'F1: Show this help',
      'Arrow keys: Navigate within components',
      'I: Toggle object information panel',
      'P: Open object properties',
      'Delete: Remove selected object'
    ];
    
    announceToScreenReader(`Keyboard shortcuts: ${shortcuts.join('. ')}`);
    
    // Could also show a visual modal here
  };
  
  const handleSkipToMain = (event) => {
    event.preventDefault();
    const mainContent = document.querySelector('[role="main"]');
    if (mainContent) {
      mainContent.focus();
      mainContent.scrollIntoView({ behavior: 'smooth', block: 'start' });
      announceToScreenReader('Moved to main content area');
    }
  };
  
  const handleSkipToToolbar = (event) => {
    event.preventDefault();
    const toolbar = document.querySelector('[role="toolbar"]');
    if (toolbar) {
      toolbar.focus();
      toolbar.scrollIntoView({ behavior: 'smooth', block: 'start' });
      announceToScreenReader('Moved to toolbar');
    }
  };
  
  const handleSkipToLibrary = (event) => {
    event.preventDefault();
    const objectLibrary = document.querySelector('#object-library');
    if (objectLibrary) {
      objectLibrary.focus();
      objectLibrary.scrollIntoView({ behavior: 'smooth', block: 'start' });
      announceToScreenReader('Moved to object library');
    }
  };
  
  return (
    <div ref={appRef} className="accessible-app" role="application" aria-label="Devible Max for Live IDE">
      {/* Skip Navigation Links */}
      <div className="skip-links" role="navigation" aria-label="Skip links">
        <a 
          ref={skipLinkRef}
          href="#main-content"
          className="skip-link"
          onClick={handleSkipToMain}
        >
          Skip to main content (Alt+1)
        </a>
        <a 
          href="#toolbar" 
          className="skip-link"
          onClick={handleSkipToToolbar}
        >
          Skip to toolbar (Alt+2)
        </a>
        <a 
          href="#object-library" 
          className="skip-link"
          onClick={handleSkipToLibrary}
        >
          Skip to object library (Alt+3)
        </a>
      </div>
      
      {/* Live Regions for Screen Reader Announcements */}
      <div
        id="announcements"
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
        role="status"
      >
        {announcements
          .filter(a => a.priority === 'polite')
          .map(announcement => (
            <div key={announcement.id}>
              {announcement.message}
            </div>
          ))
        }
      </div>
      
      {/* Error/Alert Announcements */}
      <div
        id="error-announcements"
        aria-live="assertive"
        aria-atomic="true"
        className="sr-only"
        role="alert"
      >
        {announcements
          .filter(a => a.priority === 'assertive')
          .map(announcement => (
            <div key={announcement.id}>
              {announcement.message}
            </div>
          ))
        }
      </div>
      
      {/* Application Status */}
      <div
        id="app-status"
        aria-live="polite"
        aria-atomic="false"
        className="sr-only"
        role="status"
      ></div>
      
      {/* Main Application Content */}
      <MantineProvider 
        theme={{
          // Enhanced theme for accessibility
          focusRing: 'always',
          focusRingStyles: {
            styles: () => ({
              outline: '3px solid #3b82f6',
              outlineOffset: '2px'
            })
          }
        }}
      >
        <Notifications 
          position="top-right" 
          autoClose={5000}
          // Make notifications accessible
          aria-live="polite"
        />
        
        {/* Keyboard Shortcuts Help (hidden by default) */}
        <div 
          id="keyboard-help" 
          className="sr-only" 
          role="region" 
          aria-label="Keyboard shortcuts help"
        >
          <h2>Keyboard Shortcuts</h2>
          <ul>
            <li>Tab / Shift+Tab: Navigate between elements</li>
            <li>Enter / Space: Activate buttons and links</li>
            <li>Alt+1: Skip to main content</li>
            <li>Alt+2: Skip to toolbar</li>
            <li>Alt+3: Skip to object library</li>
            <li>Escape: Close modals or return to main</li>
            <li>F1: Show keyboard shortcuts help</li>
            <li>Arrow keys: Navigate within components</li>
            <li>I: Toggle object information panel</li>
            <li>P: Open object properties</li>
            <li>Delete: Remove selected object</li>
          </ul>
        </div>
        
        {/* Apple Pencil Pressure Indicator */}
        <div className="pencil-pressure-indicator">
          <div className="pressure-fill"></div>
        </div>
        
        {children}
      </MantineProvider>
    </div>
  );
};

export default AccessibleApp;
