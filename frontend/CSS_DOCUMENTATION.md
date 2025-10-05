# DocuSage CSS Documentation

## Overview
DocuSage uses a comprehensive CSS system built on top of Tailwind CSS with custom components, animations, and medical-themed styling.

## CSS Files Structure

### 1. `index.css` - Core Tailwind & Component Styles
Main stylesheet that includes:
- Tailwind base, components, and utilities
- Custom button styles (primary, secondary, danger, success)
- Card components with hover effects
- Badge and status indicators
- Input fields and form elements
- Upload zone styling
- Progress bars
- Alert components
- Loading spinners
- Utility classes for gradients, scrollbars, and more

### 2. `custom-styles.css` - Medical-Themed Enhancements
Specialized styling for medical documentation:
- Health status indicators with color variables
- Medical document card effects
- Risk level indicators with pulse animations
- Document type icons
- Test result displays
- Interactive expandable sections
- Chart tooltips
- Trend indicators
- Loading states
- Notification toasts
- Accessibility enhancements
- Print styles

### 3. `animations.css` - Animation Library
Comprehensive animation system:
- Health status animations (heartbeat pulse, critical glow)
- Document processing animations (DNA helix, scan lines)
- Test result reveal animations
- Chart drawing animations
- Badge effects (shimmer)
- Question card animations
- Upload zone effects
- Trend indicators
- Success animations (checkmark drawing, confetti)
- Loading states (skeleton, dots)
- Notification animations
- Micro-interactions

## Key CSS Classes

### Buttons
```css
.btn-primary         /* Primary action button (blue) */
.btn-secondary       /* Secondary button (gray) */
.btn-danger          /* Danger/delete button (red) */
.btn-success         /* Success button (green) */
.btn-press           /* Add press effect on click */
```

### Cards
```css
.card                /* Basic white card with shadow */
.card-interactive    /* Clickable card with hover effects */
.card-lift           /* Card that lifts on hover */
.medical-card        /* Medical-themed card with shine effect */
```

### Badges & Status
```css
.status-badge        /* Base badge style */
.badge-success       /* Green badge for normal results */
.badge-warning       /* Yellow badge for monitoring */
.badge-danger        /* Red badge for urgent items */
.badge-info          /* Blue badge for information */
.badge-shimmer       /* Animated shimmer effect */
```

### Health Indicators
```css
.health-indicator    /* Pulsing health status icon */
.critical-alert      /* Glowing animation for critical items */
.risk-indicator      /* Risk level with pulse ring */
```

### Animations
```css
.fade-in             /* Fade in from bottom */
.slide-in            /* Slide in from left */
.scale-in            /* Scale in animation */
.result-reveal       /* Animated result appearance */
.question-card-enter /* Bouncy question card entrance */
.upload-icon-float   /* Floating upload icon */
.trend-arrow-up      /* Animated up arrow */
.trend-arrow-down    /* Animated down arrow */
```

### Loading States
```css
.skeleton            /* Skeleton loading block */
.skeleton-shimmer    /* Skeleton with shimmer effect */
.processing-animation /* Spinning loader */
.dot-pulse           /* Pulsing dot loader */
```

### Charts & Visualizations
```css
.custom-tooltip      /* Chart tooltip styling */
.chart-line          /* Animated line drawing */
.chart-bar           /* Growing bar animation */
.health-meter        /* Gradient health score meter */
```

### Upload Features
```css
.upload-zone         /* File upload dropzone */
.upload-zone-active  /* Active drag state */
.drag-over           /* Dragging file over zone */
.file-preview-enter  /* File preview animation */
```

### Progress
```css
.progress-bar        /* Progress bar container */
.progress-bar-fill   /* Animated fill */
.circular-progress   /* Circular progress indicator */
.step-indicator      /* Multi-step progress */
```

### Utilities
```css
.gradient-text       /* Gradient text effect */
.glass               /* Glassmorphism effect */
.scrollbar-thin      /* Thin custom scrollbar */
.scrollbar-hide      /* Hide scrollbar */
.text-shadow         /* Text shadow */
.text-shadow-lg      /* Large text shadow */
```

## Color Variables

### Health Status Colors
```css
--color-health-excellent: #10b981  /* Green */
--color-health-good: #22c55e       /* Light green */
--color-health-fair: #f59e0b       /* Yellow/Orange */
--color-health-poor: #ef4444       /* Red */
--color-health-critical: #dc2626   /* Dark red */
```

### Primary Theme Colors (Tailwind Config)
```javascript
primary: {
  50: '#f0f9ff',
  100: '#e0f2fe',
  500: '#0ea5e9',
  600: '#0284c7',
  700: '#0369a1',
}
```

## Animations List

### Medical-Themed
- `heartbeat-pulse` - Heartbeat rhythm for health indicators
- `critical-glow` - Pulsing glow for critical alerts
- `dna-helix` - DNA-inspired rotation
- `scan-line` - Medical scan line effect

### UI Interactions
- `pulse-ring` - Expanding ring effect
- `shimmer` - Shine/shimmer effect
- `float` - Gentle floating motion
- `ripple` - Click ripple effect
- `bounce-subtle` - Subtle bounce
- `shake` - Error shake animation

### Content Reveal
- `fadeIn` - Fade in with slide
- `slideIn` - Slide from left
- `scaleIn` - Scale up entrance
- `result-reveal` - Staggered result display
- `bounce-in-question` - Bouncy entrance

### Data Visualization
- `draw-line` - SVG line drawing
- `bar-grow` - Bar chart growth
- `health-meter-gradient` - Gradient shift

### Loading
- `rotate` - Spinning loader
- `loading` - Skeleton shimmer
- `skeleton-shimmer` - Gradient sweep
- `dot-pulse` - Pulsing dots
- `processing-stage` - Stage indicator

## Responsive Breakpoints

Following Tailwind's default breakpoints:
- `sm`: 640px
- `md`: 768px
- `lg`: 1024px
- `xl`: 1280px
- `2xl`: 1536px

## Accessibility Features

### Focus States
- Custom focus-visible outline (3px solid #0ea5e9)
- High contrast mode support
- Reduced motion support (all animations disabled)

### Screen Reader Support
- `.skip-link` - Skip to main content
- Proper heading hierarchy
- ARIA-friendly components

### Keyboard Navigation
- Clear focus indicators
- Tab-friendly interactive elements
- Escape key support for modals

## Print Styles

Optimized for printing medical documents:
- Hides navigation and interactive elements
- Removes background colors
- Enhances borders for clarity
- Prevents page breaks inside cards
- Black and white friendly

## Performance Optimizations

- Hardware-accelerated animations using `transform` and `opacity`
- Will-change hints for frequently animated elements
- Debounced scroll and resize events
- Lazy-loaded animations
- Reduced motion preference respected

## Usage Examples

### Creating a Status Card
```jsx
<div className="card medical-card">
  <div className="health-indicator">
    <span className="badge-success">Normal</span>
  </div>
  <div className="result-reveal">
    <h3>Cholesterol</h3>
    <p className="test-result">195 mg/dL</p>
  </div>
</div>
```

### Animated Upload Zone
```jsx
<div className="upload-zone upload-icon-float">
  <Upload className="h-16 w-16" />
  <p>Drop your files here</p>
</div>
```

### Critical Alert with Animation
```jsx
<div className="alert alert-danger critical-alert">
  <AlertCircle className="h-5 w-5" />
  <p>Urgent: Vitamin D level is critically low</p>
</div>
```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

All modern browsers with CSS Grid, Flexbox, and CSS Variables support.

## Future Enhancements

- Dark mode theme
- Customizable color schemes per user preference
- More chart animation variations
- Additional loading state options
- Enhanced print layouts for different document types
