import React, { useRef, useEffect, useState, useCallback } from 'react';

/**
 * Responsive Layout Hook for Tablet Optimization
 * Detects device capabilities and optimizes layout accordingly
 */
export const useResponsiveLayout = () => {
  const [layout, setLayout] = useState('desktop');
  const [orientation, setOrientation] = useState('landscape');
  const [touchCapabilities, setTouchCapabilities] = useState({
    hasTouch: false,
    hasPen: false,
    maxTouchPoints: 0,
    supportsCoarsePointer: false,
    supportsFinePointer: false
  });
  const [deviceInfo, setDeviceInfo] = useState({
    isIOS: false,
    isAndroid: false,
    isSafari: false,
    isIPad: false
  });
  
  useEffect(() => {
    const updateLayout = () => {
      const width = window.innerWidth;
      const height = window.innerHeight;
      const aspectRatio = width / height;
      
      // Determine layout type with refined breakpoints
      if (width <= 480) {
        setLayout('mobile');
      } else if (width <= 768) {
        setLayout('mobile-large');
      } else if (width <= 1024) {
        setLayout('tablet');
      } else if (width <= 1440) {
        setLayout('desktop');
      } else {
        setLayout('desktop-large');
      }
      
      // Determine orientation
      setOrientation(aspectRatio > 1 ? 'landscape' : 'portrait');
      
      // Detect touch capabilities
      const hasTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
      const maxTouchPoints = navigator.maxTouchPoints || 0;
      const hasPen = maxTouchPoints > 1;
      
      // Detect pointer capabilities
      const supportsCoarsePointer = window.matchMedia('(pointer: coarse)').matches;
      const supportsFinePointer = window.matchMedia('(pointer: fine)').matches;
      
      setTouchCapabilities({
        hasTouch,
        hasPen,
        maxTouchPoints,
        supportsCoarsePointer,
        supportsFinePointer
      });
      
      // Detect device/browser info
      const userAgent = navigator.userAgent;
      const isIOS = /iPad|iPhone|iPod/.test(userAgent);
      const isAndroid = /Android/.test(userAgent);
      const isSafari = /Safari/.test(userAgent) && !/Chrome/.test(userAgent);
      const isIPad = /iPad/.test(userAgent) || 
                     (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
      
      setDeviceInfo({
        isIOS,
        isAndroid,
        isSafari,
        isIPad
      });
    };
    
    updateLayout();
    
    // Listen for various resize events
    window.addEventListener('resize', updateLayout);
    window.addEventListener('orientationchange', updateLayout);
    
    // Delayed update for orientation change (iOS fix)
    const handleOrientationChange = () => {
      setTimeout(updateLayout, 100);
    };
    window.addEventListener('orientationchange', handleOrientationChange);
    
    return () => {
      window.removeEventListener('resize', updateLayout);
      window.removeEventListener('orientationchange', updateLayout);
      window.removeEventListener('orientationchange', handleOrientationChange);
    };
  }, []);
  
  return {
    layout,
    orientation,
    touchCapabilities,
    deviceInfo,
    // Convenience flags
    isTablet: layout === 'tablet',
    isMobile: layout === 'mobile' || layout === 'mobile-large',
    isDesktop: layout === 'desktop' || layout === 'desktop-large',
    isPortrait: orientation === 'portrait',
    isLandscape: orientation === 'landscape',
    hasTouch: touchCapabilities.hasTouch,
    hasPen: touchCapabilities.hasPen,
    isIPad: deviceInfo.isIPad,
    isTouchPrimary: touchCapabilities.supportsCoarsePointer && !touchCapabilities.supportsFinePointer
  };
};

/**
 * Advanced Touch Gesture Hook for iPad/Tablet
 * Handles complex multi-touch gestures with precision
 */
export const useTouchGestures = (canvasRef, options = {}) => {
  const {
    onPan,
    onZoom,
    onRotate,
    onTap,
    onDoubleTap,
    onLongPress,
    enableRotation = false,
    longPressDelay = 500,
    doubleTapDelay = 300
  } = options;
  
  const [gestureState, setGestureState] = useState({
    isPanning: false,
    isZooming: false,
    isPinching: false,
    isRotating: false,
    isUsingPencil: false,
    lastTouchCount: 0,
    velocity: { x: 0, y: 0 },
    momentum: false
  });
  
  const gestureRecognizer = useRef({
    touches: [],
    lastPinchDistance: 0,
    lastPanPosition: { x: 0, y: 0 },
    lastRotation: 0,
    tapCount: 0,
    lastTapTime: 0,
    longPressTimer: null,
    velocityTracker: [],
    momentumTimer: null
  });
  
  // Calculate distance between two touches
  const getTouchDistance = useCallback((touch1, touch2) => {
    return Math.sqrt(
      Math.pow(touch2.clientX - touch1.clientX, 2) +
      Math.pow(touch2.clientY - touch1.clientY, 2)
    );
  }, []);
  
  // Calculate angle between two touches
  const getTouchAngle = useCallback((touch1, touch2) => {
    return Math.atan2(
      touch2.clientY - touch1.clientY,
      touch2.clientX - touch1.clientX
    ) * 180 / Math.PI;
  }, []);
  
  // Calculate center point of touches
  const getTouchCenter = useCallback((touches) => {
    const x = touches.reduce((sum, touch) => sum + touch.clientX, 0) / touches.length;
    const y = touches.reduce((sum, touch) => sum + touch.clientY, 0) / touches.length;
    return { x, y };
  }, []);
  
  // Create visual feedback for touch
  const createTouchFeedback = useCallback((x, y, type = 'tap') => {
    const feedback = document.createElement('div');
    feedback.className = `gesture-feedback gesture-${type}`;
    feedback.style.left = `${x - 20}px`;
    feedback.style.top = `${y - 20}px`;
    feedback.style.width = '40px';
    feedback.style.height = '40px';
    feedback.style.pointerEvents = 'none';
    feedback.style.position = 'fixed';
    feedback.style.zIndex = '10000';
    
    document.body.appendChild(feedback);
    
    // Animate and remove
    requestAnimationFrame(() => {
      feedback.style.transform = 'scale(1.5)';
      feedback.style.opacity = '0';
    });
    
    setTimeout(() => {
      if (document.body.contains(feedback)) {
        document.body.removeChild(feedback);
      }
    }, 600);
  }, []);
  
  // Track velocity for momentum
  const trackVelocity = useCallback((x, y) => {
    const now = Date.now();
    const tracker = gestureRecognizer.current.velocityTracker;
    
    tracker.push({ x, y, time: now });
    
    // Keep only last 100ms of data
    while (tracker.length > 0 && now - tracker[0].time > 100) {
      tracker.shift();
    }
    
    if (tracker.length >= 2) {
      const latest = tracker[tracker.length - 1];
      const earliest = tracker[0];
      const timeDiff = latest.time - earliest.time;
      
      if (timeDiff > 0) {
        const velocity = {
          x: (latest.x - earliest.x) / timeDiff,
          y: (latest.y - earliest.y) / timeDiff
        };
        
        setGestureState(prev => ({ ...prev, velocity }));
      }
    }
  }, []);
  
  const handleTouchStart = useCallback((event) => {
    event.preventDefault();
    
    const touches = Array.from(event.touches);
    gestureRecognizer.current.touches = touches;
    
    // Clear any existing timers
    if (gestureRecognizer.current.longPressTimer) {
      clearTimeout(gestureRecognizer.current.longPressTimer);
    }
    if (gestureRecognizer.current.momentumTimer) {
      clearTimeout(gestureRecognizer.current.momentumTimer);
    }
    
    setGestureState(prev => ({
      ...prev,
      lastTouchCount: touches.length,
      momentum: false
    }));
    
    if (touches.length === 1) {
      // Single touch - start panning or tap detection
      const touch = touches[0];
      gestureRecognizer.current.lastPanPosition = {
        x: touch.clientX,
        y: touch.clientY
      };
      
      setGestureState(prev => ({ ...prev, isPanning: true }));
      
      // Start long press detection
      gestureRecognizer.current.longPressTimer = setTimeout(() => {
        if (onLongPress && gestureState.isPanning) {
          onLongPress(touch.clientX, touch.clientY);
          createTouchFeedback(touch.clientX, touch.clientY, 'long-press');
        }
      }, longPressDelay);
      
      // Visual feedback for touch
      createTouchFeedback(touch.clientX, touch.clientY);
      
      // Track velocity
      trackVelocity(touch.clientX, touch.clientY);
      
    } else if (touches.length === 2) {
      // Two finger touch - start pinch zoom/rotate
      const distance = getTouchDistance(touches[0], touches[1]);
      gestureRecognizer.current.lastPinchDistance = distance;
      
      if (enableRotation) {
        const angle = getTouchAngle(touches[0], touches[1]);
        gestureRecognizer.current.lastRotation = angle;
      }
      
      setGestureState(prev => ({
        ...prev,
        isPinching: true,
        isZooming: true,
        isRotating: enableRotation,
        isPanning: false
      }));
      
      // Create feedback for both touches
      touches.forEach(touch => {
        createTouchFeedback(touch.clientX, touch.clientY, 'pinch');
      });
    }
  }, [longPressDelay, enableRotation, onLongPress, trackVelocity, createTouchFeedback, gestureState.isPanning]);
  
  const handleTouchMove = useCallback((event) => {
    event.preventDefault();
    
    const touches = Array.from(event.touches);
    
    // Clear long press timer on movement
    if (gestureRecognizer.current.longPressTimer) {
      clearTimeout(gestureRecognizer.current.longPressTimer);
      gestureRecognizer.current.longPressTimer = null;
    }
    
    if (touches.length === 1 && gestureState.isPanning) {
      // Handle panning
      const touch = touches[0];
      const deltaX = touch.clientX - gestureRecognizer.current.lastPanPosition.x;
      const deltaY = touch.clientY - gestureRecognizer.current.lastPanPosition.y;
      
      // Minimum threshold to prevent jitter
      if (Math.abs(deltaX) > 2 || Math.abs(deltaY) > 2) {
        onPan?.(deltaX, deltaY, touch.clientX, touch.clientY);
        
        gestureRecognizer.current.lastPanPosition = {
          x: touch.clientX,
          y: touch.clientY
        };
        
        // Track velocity
        trackVelocity(touch.clientX, touch.clientY);
      }
      
    } else if (touches.length === 2 && gestureState.isPinching) {
      // Handle pinch zoom and rotation
      const distance = getTouchDistance(touches[0], touches[1]);
      const scale = distance / gestureRecognizer.current.lastPinchDistance;
      const center = getTouchCenter(touches);
      
      if (Math.abs(scale - 1) > 0.01) {
        onZoom?.(scale, center.x, center.y);
        gestureRecognizer.current.lastPinchDistance = distance;
      }
      
      // Handle rotation if enabled
      if (enableRotation && onRotate) {
        const angle = getTouchAngle(touches[0], touches[1]);
        const deltaAngle = angle - gestureRecognizer.current.lastRotation;
        
        if (Math.abs(deltaAngle) > 1) {
          onRotate(deltaAngle, center.x, center.y);
          gestureRecognizer.current.lastRotation = angle;
        }
      }
    }
  }, [gestureState, onPan, onZoom, onRotate, enableRotation, trackVelocity, getTouchDistance, getTouchCenter, getTouchAngle]);
  
  const handleTouchEnd = useCallback((event) => {
    const touches = Array.from(event.touches);
    const changedTouches = Array.from(event.changedTouches);
    
    // Clear timers
    if (gestureRecognizer.current.longPressTimer) {
      clearTimeout(gestureRecognizer.current.longPressTimer);
      gestureRecognizer.current.longPressTimer = null;
    }
    
    if (touches.length === 0) {
      // All touches ended
      const now = Date.now();
      const lastTouch = changedTouches[0];
      
      // Check for tap/double tap
      if (gestureState.isPanning && !gestureState.momentum) {
        const timeSinceLastTap = now - gestureRecognizer.current.lastTapTime;
        
        if (timeSinceLastTap < doubleTapDelay) {
          // Double tap
          gestureRecognizer.current.tapCount++;
          if (gestureRecognizer.current.tapCount === 2) {
            onDoubleTap?.(lastTouch.clientX, lastTouch.clientY);
            createTouchFeedback(lastTouch.clientX, lastTouch.clientY, 'double-tap');
            gestureRecognizer.current.tapCount = 0;
          }
        } else {
          // Single tap (with delay to check for double tap)
          gestureRecognizer.current.tapCount = 1;
          setTimeout(() => {
            if (gestureRecognizer.current.tapCount === 1) {
              onTap?.(lastTouch.clientX, lastTouch.clientY);
              gestureRecognizer.current.tapCount = 0;
            }
          }, doubleTapDelay);
        }
        
        gestureRecognizer.current.lastTapTime = now;
      }
      
      // Start momentum if there's sufficient velocity
      const velocity = gestureState.velocity;
      if (velocity && (Math.abs(velocity.x) > 0.5 || Math.abs(velocity.y) > 0.5)) {
        setGestureState(prev => ({ ...prev, momentum: true }));
        
        const applyMomentum = () => {
          const damping = 0.95;
          const minVelocity = 0.1;
          
          if (Math.abs(velocity.x) > minVelocity || Math.abs(velocity.y) > minVelocity) {
            onPan?.(velocity.x * 10, velocity.y * 10);
            velocity.x *= damping;
            velocity.y *= damping;
            
            gestureRecognizer.current.momentumTimer = setTimeout(applyMomentum, 16);
          } else {
            setGestureState(prev => ({ ...prev, momentum: false }));
          }
        };
        
        applyMomentum();
      }
      
      // Reset gesture state
      setGestureState(prev => ({
        ...prev,
        isPanning: false,
        isZooming: false,
        isPinching: false,
        isRotating: false,
        lastTouchCount: 0
      }));
      
      // Clear velocity tracker
      gestureRecognizer.current.velocityTracker = [];
      
    } else if (touches.length === 1 && gestureState.isPinching) {
      // Transition from pinch to pan
      const touch = touches[0];
      gestureRecognizer.current.lastPanPosition = {
        x: touch.clientX,
        y: touch.clientY
      };
      
      setGestureState(prev => ({
        ...prev,
        isPinching: false,
        isZooming: false,
        isRotating: false,
        isPanning: true
      }));
      
      // Start velocity tracking
      trackVelocity(touch.clientX, touch.clientY);
    }
  }, [gestureState, doubleTapDelay, onTap, onDoubleTap, onPan, trackVelocity, createTouchFeedback]);
  
  // Apple Pencil and stylus support
  const handlePointerDown = useCallback((event) => {
    if (event.pointerType === 'pen') {
      setGestureState(prev => ({ ...prev, isUsingPencil: true }));
      
      // Show pressure indicator
      const pressureIndicator = document.querySelector('.pencil-pressure-indicator');
      if (pressureIndicator) {
        pressureIndicator.style.display = 'block';
        pressureIndicator.style.left = `${event.clientX - 25}px`;
        pressureIndicator.style.top = `${event.clientY - 25}px`;
      }
    }
  }, []);
  
  const handlePointerMove = useCallback((event) => {
    if (event.pointerType === 'pen') {
      // Update pressure indicator
      const pressure = event.pressure || 0.5;
      const pressureIndicator = document.querySelector('.pencil-pressure-indicator');
      if (pressureIndicator) {
        pressureIndicator.style.left = `${event.clientX - 25}px`;
        pressureIndicator.style.top = `${event.clientY - 25}px`;
        
        const pressureFill = pressureIndicator.querySelector('.pressure-fill');
        if (pressureFill) {
          pressureFill.style.transform = `scale(${0.3 + pressure * 0.7})`;
          pressureFill.style.opacity = pressure;
        }
      }
    }
  }, []);
  
  const handlePointerUp = useCallback((event) => {
    if (event.pointerType === 'pen') {
      setGestureState(prev => ({ ...prev, isUsingPencil: false }));
      
      // Hide pressure indicator
      const pressureIndicator = document.querySelector('.pencil-pressure-indicator');
      if (pressureIndicator) {
        pressureIndicator.style.display = 'none';
      }
    }
  }, []);
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    // Touch events
    canvas.addEventListener('touchstart', handleTouchStart, { passive: false });
    canvas.addEventListener('touchmove', handleTouchMove, { passive: false });
    canvas.addEventListener('touchend', handleTouchEnd, { passive: false });
    canvas.addEventListener('touchcancel', handleTouchEnd, { passive: false });
    
    // Pointer events (for Apple Pencil and other styluses)
    canvas.addEventListener('pointerdown', handlePointerDown);
    canvas.addEventListener('pointermove', handlePointerMove);
    canvas.addEventListener('pointerup', handlePointerUp);
    canvas.addEventListener('pointercancel', handlePointerUp);
    
    return () => {
      canvas.removeEventListener('touchstart', handleTouchStart);
      canvas.removeEventListener('touchmove', handleTouchMove);
      canvas.removeEventListener('touchend', handleTouchEnd);
      canvas.removeEventListener('touchcancel', handleTouchEnd);
      canvas.removeEventListener('pointerdown', handlePointerDown);
      canvas.removeEventListener('pointermove', handlePointerMove);
      canvas.removeEventListener('pointerup', handlePointerUp);
      canvas.removeEventListener('pointercancel', handlePointerUp);
      
      // Clean up timers
      if (gestureRecognizer.current.longPressTimer) {
        clearTimeout(gestureRecognizer.current.longPressTimer);
      }
      if (gestureRecognizer.current.momentumTimer) {
        clearTimeout(gestureRecognizer.current.momentumTimer);
      }
    };
  }, [handleTouchStart, handleTouchMove, handleTouchEnd, handlePointerDown, handlePointerMove, handlePointerUp]);
  
  return gestureState;
};

/**
 * Viewport Management Hook
 * Handles safe areas, orientation changes, and viewport scaling
 */
export const useViewportManagement = () => {
  const [viewport, setViewport] = useState({
    width: window.innerWidth,
    height: window.innerHeight,
    safeAreaInsets: {
      top: 0,
      right: 0,
      bottom: 0,
      left: 0
    },
    scale: 1,
    orientation: 0
  });
  
  useEffect(() => {
    const updateViewport = () => {
      // Get safe area insets (for devices with notches)
      const safeAreaInsets = {
        top: parseInt(getComputedStyle(document.documentElement).getPropertyValue('--safe-area-inset-top') || '0'),
        right: parseInt(getComputedStyle(document.documentElement).getPropertyValue('--safe-area-inset-right') || '0'),
        bottom: parseInt(getComputedStyle(document.documentElement).getPropertyValue('--safe-area-inset-bottom') || '0'),
        left: parseInt(getComputedStyle(document.documentElement).getPropertyValue('--safe-area-inset-left') || '0')
      };
      
      setViewport({
        width: window.innerWidth,
        height: window.innerHeight,
        safeAreaInsets,
        scale: window.devicePixelRatio || 1,
        orientation: screen.orientation?.angle || 0
      });
    };
    
    updateViewport();
    
    window.addEventListener('resize', updateViewport);
    window.addEventListener('orientationchange', updateViewport);
    
    // Listen for safe area changes
    if ('visualViewport' in window) {
      window.visualViewport.addEventListener('resize', updateViewport);
    }
    
    return () => {
      window.removeEventListener('resize', updateViewport);
      window.removeEventListener('orientationchange', updateViewport);
      
      if ('visualViewport' in window) {
        window.visualViewport.removeEventListener('resize', updateViewport);
      }
    };
  }, []);
  
  return viewport;
};

export default {
  useResponsiveLayout,
  useTouchGestures,
  useViewportManagement
};
