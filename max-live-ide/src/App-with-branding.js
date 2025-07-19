import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import MaxLiveIDE from '../components/MaxLiveIDE';
import IconBrandingShowcase from '../components/icons/IconBrandingShowcase';
import BrandedIcons from '../components/icons/BrandedIcons';

/**
 * App integration example showing how to use branded icons
 */
const App = () => {
  return (
    <Router>
      <div className="app">
        {/* Navigation with branded icons */}
        <nav className="app-nav">
          <div className="nav-brand">
            <BrandedIcons.Logo size={32} animated />
            <span>Devible Studio</span>
          </div>
          
          <div className="nav-links">
            <Link to="/" className="nav-link">
              <BrandedIcons.Mixer size={20} />
              IDE
            </Link>
            <Link to="/icons" className="nav-link">
              <BrandedIcons.ThemedIcon 
                icon={BrandedIcons.Play} 
                theme="secondary" 
                size={20} 
              />
              Icons
            </Link>
          </div>
        </nav>

        <main className="app-main">
          <Routes>
            <Route path="/" element={<MaxLiveIDE />} />
            <Route path="/icons" element={<IconBrandingShowcase />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;
