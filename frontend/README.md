# BuildMyRig Frontend

A modern, responsive web frontend for the BuildMyRig PC build recommendation system.

## Features

- **Beautiful UI**: Modern gradient design with smooth animations
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Interactive Form**: Easy-to-use form for budget, use case, and brand preferences
- **Real-time Results**: Dynamic loading and display of build recommendations
- **Parts Explorer**: Browse all available PC parts by category
- **Smooth Navigation**: Smooth scrolling between sections

## Technology Stack

- **HTML5**: Semantic markup
- **CSS3**: Modern styling with gradients, animations, and flexbox/grid
- **JavaScript (ES6+)**: Modern JavaScript with async/await, fetch API
- **Font Awesome**: Icons for better UX
- **Google Fonts**: Inter font family for clean typography

## Setup Instructions

1. **Start the Backend**: First, make sure your FastAPI backend is running:
   ```bash
   python main.py
   ```

2. **Access the Frontend**: Open your browser and go to:
   ```
   http://localhost:8000
   ```

3. **Use the Application**: 
   - Fill in your budget (minimum $500)
   - Select your use case (Gaming, Workstation, or General Use)
   - Optionally select brand preferences
   - Click "Find My Build" to get recommendations

## File Structure

```
frontend/
├── index.html          # Main HTML file
├── styles.css          # CSS styles and animations
├── script.js           # JavaScript functionality
└── README.md          # This file
```

## Features Breakdown

### 1. Hero Section
- Eye-catching gradient background
- Animated PC component icons
- Call-to-action button

### 2. Configuration Form
- Budget input with validation
- Use case selection
- Brand preference dropdowns
- Responsive design

### 3. Loading Animation
- Smooth loading spinner
- Loading text feedback

### 4. Results Display
- Cards showing build recommendations
- Bang-for-buck scores
- Detailed part lists with prices
- Hover effects and animations

### 5. Parts Explorer
- Tabbed interface for different categories
- Part cards with performance scores
- Real-time loading from API

### 6. About Section
- Feature highlights
- Clean card layout
- Hover animations

## API Integration

The frontend communicates with the backend API at `http://localhost:8000`:

- `POST /recommend` - Get build recommendations
- `GET /parts/{category}` - Get parts by category
- `GET /health` - Health check

## Responsive Design

The frontend is fully responsive and adapts to different screen sizes:

- **Desktop**: Full grid layout with side-by-side sections
- **Tablet**: Adjusted grid with proper spacing
- **Mobile**: Stacked layout with optimized touch targets

## Browser Support

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Customization

The design can be easily customized by modifying:

- **Colors**: Update CSS custom properties in `styles.css`
- **Typography**: Change font families and sizes
- **Layout**: Modify grid and flexbox properties
- **Animations**: Adjust keyframe animations and transitions

## Development

To make changes:

1. Edit the HTML, CSS, or JavaScript files
2. Refresh the browser to see changes
3. No build process required - pure vanilla web technologies

## Performance

- Optimized CSS with efficient selectors
- Minimal JavaScript bundle
- Lazy loading for better performance
- Smooth 60fps animations

## Accessibility

- Semantic HTML structure
- Proper ARIA labels
- Keyboard navigation support
- Color contrast compliance

## Future Enhancements

- Dark mode toggle
- Build comparison feature
- Save/export build functionality
- Enhanced mobile experience
- Progressive Web App (PWA) features
