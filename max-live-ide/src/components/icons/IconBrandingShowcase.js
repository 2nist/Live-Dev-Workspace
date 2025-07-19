import React, { useState } from 'react';
import BrandedIcons from './BrandedIcons';
import './branded-icons.css';
import './IconBrandingShowcase.css';

/**
 * Icon Branding Showcase
 * Demonstrates the enhanced branded icon system with interactive examples
 */
const IconBrandingShowcase = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('connected');
  const [waveformAnimated, setWaveformAnimated] = useState(false);

  const handleRecordToggle = () => {
    setIsRecording(!isRecording);
  };

  const cycleConnectionStatus = () => {
    const statuses = ['connected', 'disconnected', 'warning'];
    const currentIndex = statuses.indexOf(connectionStatus);
    const nextIndex = (currentIndex + 1) % statuses.length;
    setConnectionStatus(statuses[nextIndex]);
  };

  return (
    <div className="icon-branding-showcase">
      <div className="showcase-header">
        <BrandedIcons.Logo size={48} variant="glow" animated />
        <h1>Devible Icon Branding System</h1>
        <p>Interactive demonstration of enhanced SVG icons with advanced styling</p>
      </div>

      {/* Basic Icons */}
      <section className="showcase-section">
        <h2>Basic Branded Icons</h2>
        <div className="icon-grid">
          <div className="icon-demo">
            <BrandedIcons.Play size={32} variant="gradient" />
            <span>Play (Gradient)</span>
          </div>
          <div className="icon-demo">
            <BrandedIcons.Play size={32} variant="solid" />
            <span>Play (Solid)</span>
          </div>
          <div className="icon-demo">
            <BrandedIcons.Play size={32} variant="glow" animated />
            <span>Play (Glow + Animated)</span>
          </div>
        </div>
      </section>

      {/* Interactive Icons */}
      <section className="showcase-section">
        <h2>Interactive Icons</h2>
        <div className="icon-grid">
          <div className="icon-demo interactive">
            <button onClick={handleRecordToggle} className="icon-button">
              <BrandedIcons.Record 
                size={32} 
                recording={isRecording}
                variant="gradient"
              />
            </button>
            <span>{isRecording ? 'Recording...' : 'Click to Record'}</span>
          </div>
          
          <div className="icon-demo interactive">
            <button onClick={cycleConnectionStatus} className="icon-button">
              <BrandedIcons.Status 
                size={32} 
                status={connectionStatus}
                animated={connectionStatus === 'connected'}
              />
            </button>
            <span>Status: {connectionStatus}</span>
          </div>
          
          <div className="icon-demo interactive">
            <button 
              onClick={() => setWaveformAnimated(!waveformAnimated)} 
              className="icon-button"
            >
              <BrandedIcons.Waveform 
                size={32} 
                animated={waveformAnimated}
              />
            </button>
            <span>{waveformAnimated ? 'Animated' : 'Click to Animate'}</span>
          </div>
        </div>
      </section>

      {/* 3D Effects */}
      <section className="showcase-section">
        <h2>3D Enhanced Icons</h2>
        <div className="icon-grid">
          <div className="icon-demo">
            <BrandedIcons.Mixer size={32} variant="3d" />
            <span>3D Mixer</span>
          </div>
          <div className="icon-demo">
            <BrandedIcons.Mixer size={32} variant="flat" />
            <span>Flat Mixer</span>
          </div>
        </div>
      </section>

      {/* Theme Variants */}
      <section className="showcase-section">
        <h2>Theme Variants</h2>
        <div className="icon-grid">
          {['primary', 'secondary', 'tertiary', 'success', 'warning', 'error'].map(theme => (
            <div key={theme} className="icon-demo">
              <BrandedIcons.ThemedIcon 
                icon={BrandedIcons.Play}
                theme={theme}
                size={32}
              />
              <span className={`theme-${theme}`}>{theme}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Size Variants */}
      <section className="showcase-section">
        <h2>Size Variants</h2>
        <div className="icon-grid size-demo">
          {[16, 20, 24, 32, 48].map(size => (
            <div key={size} className="icon-demo">
              <BrandedIcons.Logo size={size} variant="gradient" />
              <span>{size}px</span>
            </div>
          ))}
        </div>
      </section>

      {/* Button Integration */}
      <section className="showcase-section">
        <h2>Button Integration</h2>
        <div className="button-grid">
          <button className="btn-devible-icon btn-devible-icon-primary">
            <BrandedIcons.Play size={20} />
            <span>Play</span>
          </button>
          <button className="btn-devible-icon btn-devible-icon-secondary">
            <BrandedIcons.Record size={20} />
            <span>Record</span>
          </button>
          <button className="btn-devible-icon btn-devible-icon-danger">
            <BrandedIcons.Status size={20} status="disconnected" />
            <span>Stop</span>
          </button>
        </div>
      </section>

      {/* Code Examples */}
      <section className="showcase-section">
        <h2>Usage Examples</h2>
        <div className="code-examples">
          <div className="code-example">
            <h3>Basic Branded Icon</h3>
            <pre><code>{`<BrandedIcons.Play 
  size={32} 
  variant="gradient" 
/>`}</code></pre>
          </div>
          
          <div className="code-example">
            <h3>Interactive Record Button</h3>
            <pre><code>{`<BrandedIcons.Record 
  size={32} 
  recording={isRecording}
  variant="gradient"
/>`}</code></pre>
          </div>
          
          <div className="code-example">
            <h3>Themed Icon</h3>
            <pre><code>{`<BrandedIcons.ThemedIcon 
  icon={BrandedIcons.Play}
  theme="primary"
  size={32}
/>`}</code></pre>
          </div>
          
          <div className="code-example">
            <h3>Enhanced Logo</h3>
            <pre><code>{`<BrandedIcons.Logo 
  size={48} 
  variant="glow" 
  animated 
/>`}</code></pre>
          </div>
        </div>
      </section>
    </div>
  );
};

export default IconBrandingShowcase;
