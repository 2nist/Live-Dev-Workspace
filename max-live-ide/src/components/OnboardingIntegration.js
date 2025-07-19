/**
 * Onboarding Integration Helper
 * Utilities for integrating onboarding system with existing components
 */

import React, { createContext, useContext, useState, useCallback } from 'react';

// Onboarding Context
const OnboardingContext = createContext();

export const useOnboarding = () => {
  const context = useContext(OnboardingContext);
  if (!context) {
    throw new Error('useOnboarding must be used within OnboardingProvider');
  }
  return context;
};

// Onboarding Provider
export const OnboardingProvider = ({ children }) => {
  const [isOnboardingActive, setIsOnboardingActive] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [hasCompletedOnboarding, setHasCompletedOnboarding] = useState(
    localStorage.getItem('devible-onboarding-completed') === 'true'
  );
  const [onboardingData, setOnboardingData] = useState({});

  const startOnboarding = useCallback(() => {
    setIsOnboardingActive(true);
    setCurrentStep(0);
    setOnboardingData({});
  }, []);

  const completeOnboarding = useCallback(() => {
    setIsOnboardingActive(false);
    setHasCompletedOnboarding(true);
    localStorage.setItem('devible-onboarding-completed', 'true');
    localStorage.setItem('devible-onboarding-completed-at', new Date().toISOString());
  }, []);

  const resetOnboarding = useCallback(() => {
    setIsOnboardingActive(false);
    setCurrentStep(0);
    setHasCompletedOnboarding(false);
    setOnboardingData({});
    localStorage.removeItem('devible-onboarding-completed');
    localStorage.removeItem('devible-onboarding-completed-at');
  }, []);

  const setOnboardingStep = useCallback((step) => {
    setCurrentStep(step);
  }, []);

  const updateOnboardingData = useCallback((data) => {
    setOnboardingData(prev => ({ ...prev, ...data }));
  }, []);

  const value = {
    isOnboardingActive,
    currentStep,
    hasCompletedOnboarding,
    onboardingData,
    startOnboarding,
    completeOnboarding,
    resetOnboarding,
    setOnboardingStep,
    updateOnboardingData
  };

  return (
    <OnboardingContext.Provider value={value}>
      {children}
    </OnboardingContext.Provider>
  );
};

// HOC for adding onboarding support to components
export const withOnboarding = (WrappedComponent, onboardingConfig = {}) => {
  return React.forwardRef((props, ref) => {
    const onboarding = useOnboarding();
    
    return (
      <WrappedComponent
        {...props}
        ref={ref}
        onboarding={onboarding}
        onboardingConfig={onboardingConfig}
      />
    );
  });
};

// Hook for marking onboarding targets
export const useOnboardingTarget = (targetId, options = {}) => {
  const { isOnboardingActive, currentStep } = useOnboarding();
  
  const isActiveTarget = isOnboardingActive && options.step === currentStep;
  
  const targetProps = {
    'data-onboarding-target': targetId,
    'data-onboarding-step': options.step,
    'data-onboarding-active': isActiveTarget,
    ...(isActiveTarget && {
      'aria-describedby': `onboarding-tooltip-${targetId}`,
      'data-spotlight': 'true'
    })
  };

  return {
    isActiveTarget,
    targetProps
  };
};

// Helper to check if user should see onboarding
export const shouldShowOnboarding = () => {
  const completed = localStorage.getItem('devible-onboarding-completed');
  const completedAt = localStorage.getItem('devible-onboarding-completed-at');
  
  // Never completed
  if (!completed) return true;
  
  // Completed more than 30 days ago (optional re-onboarding)
  if (completedAt) {
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    const completedDate = new Date(completedAt);
    
    if (completedDate < thirtyDaysAgo) {
      // Could offer re-onboarding, but respect user's choice
      return false;
    }
  }
  
  return false;
};

// Integration helpers for existing components
export const OnboardingHelpers = {
  // Add onboarding attributes to any element
  addOnboardingProps: (element, targetId, step) => {
    if (!React.isValidElement(element)) return element;
    
    return React.cloneElement(element, {
      'data-onboarding-target': targetId,
      'data-onboarding-step': step,
      ...element.props
    });
  },

  // Wrap component with onboarding detection
  wrapWithOnboarding: (component, targetId, step) => {
    return (
      <div 
        data-onboarding-target={targetId}
        data-onboarding-step={step}
      >
        {component}
      </div>
    );
  },

  // Create onboarding-aware refs
  createOnboardingRef: (baseRef, targetId) => {
    return (element) => {
      if (element) {
        element.setAttribute('data-onboarding-target', targetId);
      }
      if (baseRef) {
        if (typeof baseRef === 'function') {
          baseRef(element);
        } else {
          baseRef.current = element;
        }
      }
    };
  }
};

// Onboarding event system
class OnboardingEventEmitter {
  constructor() {
    this.events = {};
  }

  on(event, callback) {
    if (!this.events[event]) {
      this.events[event] = [];
    }
    this.events[event].push(callback);
  }

  off(event, callback) {
    if (!this.events[event]) return;
    this.events[event] = this.events[event].filter(cb => cb !== callback);
  }

  emit(event, data) {
    if (!this.events[event]) return;
    this.events[event].forEach(callback => callback(data));
  }
}

export const onboardingEvents = new OnboardingEventEmitter();

// Predefined onboarding steps configuration
export const ONBOARDING_STEPS = {
  WELCOME: 0,
  TOOLBAR: 1,
  CANVAS: 2,
  OBJECTS: 3,
  CONNECTIONS: 4,
  PROPERTIES: 5,
  TEMPLATES: 6,
  LIVE_STATUS: 7,
  COMPLETE: 8
};

// Default onboarding configuration
export const DEFAULT_ONBOARDING_CONFIG = {
  autoStart: false,
  showProgress: true,
  allowSkip: true,
  persistent: true,
  highlightStyle: 'spotlight',
  animationDuration: 300,
  stepDelay: 500
};

export default OnboardingContext;
