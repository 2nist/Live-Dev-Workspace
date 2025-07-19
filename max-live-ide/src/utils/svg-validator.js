/**
 * SVG Icon Validator and Optimizer
 * Use this tool to validate your custom SVG icons before integration
 */

class SVGIconValidator {
    constructor() {
        this.rules = {
            viewBox: '0 0 24 24',
            maxStrokeWidth: 3,
            minStrokeWidth: 1,
            recommendedStrokeWidth: 2,
            safeAreaMargin: 2
        };
    }

    validateSVG(svgString) {
        const parser = new DOMParser();
        const doc = parser.parseFromString(svgString, 'image/svg+xml');
        const svg = doc.querySelector('svg');
        
        if (!svg) {
            return { valid: false, errors: ['Invalid SVG format'] };
        }

        const errors = [];
        const warnings = [];
        const suggestions = [];

        // Check viewBox
        const viewBox = svg.getAttribute('viewBox');
        if (viewBox !== this.rules.viewBox) {
            errors.push(`ViewBox should be "${this.rules.viewBox}", found "${viewBox}"`);
        }

        // Check stroke width consistency
        const strokes = Array.from(svg.querySelectorAll('[stroke-width]'));
        const strokeWidths = strokes.map(el => parseFloat(el.getAttribute('stroke-width')));
        const uniqueStrokes = [...new Set(strokeWidths)];
        
        if (uniqueStrokes.length > 2) {
            warnings.push(`Multiple stroke widths found: ${uniqueStrokes.join(', ')}. Consider using max 2 different weights.`);
        }

        strokeWidths.forEach(width => {
            if (width < this.rules.minStrokeWidth || width > this.rules.maxStrokeWidth) {
                warnings.push(`Stroke width ${width} is outside recommended range (${this.rules.minStrokeWidth}-${this.rules.maxStrokeWidth})`);
            }
        });

        // Check for currentColor usage
        const colorElements = Array.from(svg.querySelectorAll('[stroke], [fill]'));
        const hasHardcodedColors = colorElements.some(el => {
            const stroke = el.getAttribute('stroke');
            const fill = el.getAttribute('fill');
            return (stroke && stroke !== 'currentColor' && stroke !== 'none') ||
                   (fill && fill !== 'currentColor' && fill !== 'none');
        });

        if (hasHardcodedColors) {
            warnings.push('Consider using "currentColor" instead of hardcoded colors for better theming flexibility');
        }

        // Check stroke caps and joins
        const paths = Array.from(svg.querySelectorAll('path, line, polyline'));
        paths.forEach(path => {
            if (!path.getAttribute('stroke-linecap')) {
                suggestions.push('Add stroke-linecap="round" for smoother line endings');
            }
            if (!path.getAttribute('stroke-linejoin')) {
                suggestions.push('Add stroke-linejoin="round" for smoother corners');
            }
        });

        // Check for unnecessary attributes
        const unnecessaryAttrs = ['style', 'class', 'id'];
        unnecessaryAttrs.forEach(attr => {
            if (svg.querySelector(`[${attr}]`)) {
                suggestions.push(`Remove ${attr} attributes - use props in React components instead`);
            }
        });

        return {
            valid: errors.length === 0,
            errors,
            warnings,
            suggestions,
            score: this.calculateScore(errors, warnings, suggestions)
        };
    }

    calculateScore(errors, warnings, suggestions) {
        let score = 100;
        score -= errors.length * 20;
        score -= warnings.length * 10;
        score -= suggestions.length * 5;
        return Math.max(0, score);
    }

    optimizeSVG(svgString) {
        let optimized = svgString;
        
        // Remove unnecessary whitespace
        optimized = optimized.replace(/\s+/g, ' ').trim();
        
        // Remove comments
        optimized = optimized.replace(/<!--[\s\S]*?-->/g, '');
        
        // Optimize path data (basic)
        optimized = optimized.replace(/\s*([,\s])\s*/g, '$1');
        
        // Add recommended attributes if missing
        if (!optimized.includes('stroke-linecap')) {
            optimized = optimized.replace(/stroke="[^"]*"/g, '$& stroke-linecap="round"');
        }
        
        if (!optimized.includes('stroke-linejoin')) {
            optimized = optimized.replace(/stroke="[^"]*"/g, '$& stroke-linejoin="round"');
        }

        return optimized;
    }

    generateReactComponent(svgString, iconName) {
        const parser = new DOMParser();
        const doc = parser.parseFromString(svgString, 'image/svg+xml');
        const svg = doc.querySelector('svg');
        
        if (!svg) return null;

        const paths = Array.from(svg.children).map(child => {
            const tagName = child.tagName;
            const attrs = Array.from(child.attributes).map(attr => {
                let name = attr.name;
                let value = attr.value;
                
                // Convert to React prop names
                if (name === 'stroke-width') name = 'strokeWidth';
                if (name === 'stroke-linecap') name = 'strokeLinecap';
                if (name === 'stroke-linejoin') name = 'strokeLinejoin';
                if (name === 'fill-rule') name = 'fillRule';
                
                // Use dynamic values for theming
                if (name === 'stroke' && value !== 'none') value = '{color}';
                if (name === 'fill' && value !== 'none') value = '{color}';
                
                return `${name}="${value}"`;
            }).join(' ');
            
            return `    <${tagName} ${attrs} />`;
        }).join('\n');

        return `export const ${iconName} = ({ 
  size = 24, 
  color = 'currentColor', 
  className = '' 
}) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    className={\`devible-icon \${className}\`}
    xmlns="http://www.w3.org/2000/svg"
  >
${paths}
  </svg>
);`;
    }
}

// Usage Examples and Testing Suite
const validator = new SVGIconValidator();

// Example SVG validation
const testSVG = `
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M9 18V5l12-2v13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="6" cy="18" r="3" stroke="currentColor" stroke-width="2"/>
  <circle cx="18" cy="16" r="3" stroke="currentColor" stroke-width="2"/>
</svg>
`;

console.log('Validation Result:', validator.validateSVG(testSVG));
console.log('Optimized SVG:', validator.optimizeSVG(testSVG));
console.log('React Component:', validator.generateReactComponent(testSVG, 'MusicIcon'));

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SVGIconValidator;
}

// Browser global
if (typeof window !== 'undefined') {
    window.SVGIconValidator = SVGIconValidator;
}

/**
 * QUICK VALIDATION CHECKLIST
 * 
 * ✅ ViewBox is "0 0 24 24"
 * ✅ Uses stroke="currentColor" 
 * ✅ stroke-width="2" (recommended)
 * ✅ stroke-linecap="round"
 * ✅ stroke-linejoin="round"
 * ✅ No hardcoded colors
 * ✅ Clean, minimal paths
 * ✅ File size under 2KB
 * ✅ Visually balanced
 * ✅ Works at 16px size
 */
