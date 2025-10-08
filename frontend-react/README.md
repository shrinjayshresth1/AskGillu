# CAG React Frontend

A modern React.js frontend for the CAG (Conversational AI Gateway) system with advanced AI chat capabilities and document processing.

## ✨ Features

- 🎨 **Modern UI**: Beautiful glass-morphism design with gradient backgrounds
- 📱 **Responsive Design**: Perfect on desktop, tablet, and mobile devices
- ⚡ **Real-time Status**: Backend connection monitoring and health checks
- 🎯 **AI Chat Interface**: Advanced conversational AI with multiple response styles
- 🔧 **Vector Database Toggle**: Switch between Qdrant and FAISS in chat interface
- 💫 **Smooth Animations**: Loading states and smooth transitions
- 🎭 **Professional UX**: Intuitive interface with modern components
- 🔍 **Hybrid Search**: Real-time search across document knowledge base
- 📊 **Status Dashboard**: System health and performance monitoring

## 🚀 Quick Start

### Prerequisites
- **Node.js 16+** and npm
- **Backend running** on http://localhost:8000

### Installation

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend-react
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

### Alternative: Automated Startup
```bash
# From the project root - this starts both backend and frontend
start-dev.ps1
```

The application will open at **http://localhost:3000**

## 🏗️ Architecture

### Component Structure
```
src/
├── components/
│   ├── ChatInterface.js      # Main chat component
│   ├── ResponseStyles.js     # AI personality modes
│   ├── StatusIndicator.js    # Backend health monitoring
│   ├── PromptEditor.js       # System prompt customization
│   └── VectorDBToggle.js     # Database switching
├── lib/
│   └── utils.js              # Utility functions
└── utils/
    └── api.js                # Backend API integration
```

### State Management
- **React Hooks**: useState, useEffect for local state
- **Real-time Updates**: Backend health monitoring with auto-reconnect
- **Error Handling**: Graceful fallbacks and user notifications

## 🎨 Design System

### Styling Framework
- **Tailwind CSS**: Utility-first CSS framework
- **Glass Morphism**: Modern translucent UI elements
- **Responsive Design**: Mobile-first approach
- **Dark Theme**: Professional appearance with gradient backgrounds

### Color Palette
- Primary: Blue gradients (#3B82F6 → #1E40AF)
- Success: Green (#10B981)
- Warning: Amber (#F59E0B)
- Error: Red (#EF4444)
- Background: Dark gradients with transparency

## 🔧 Configuration

### Environment Variables
```bash
# API Configuration
REACT_APP_BACKEND_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=30000

# Feature Flags
REACT_APP_ENABLE_VECTOR_TOGGLE=true
REACT_APP_ENABLE_PROMPT_EDITOR=true
```

### Backend Integration
The frontend communicates with the backend through:
- **REST API**: Standard HTTP requests for chat and configuration
- **Health Checks**: Real-time backend status monitoring
- **Error Handling**: Automatic retry and fallback mechanisms

## 📱 User Experience

### Chat Interface
- **Multi-modal Input**: Text input with formatting support
- **Response Streaming**: Real-time AI response display
- **Vector Database Toggle**: Switch between Qdrant and FAISS
- **Response Styles**: 6 different AI personality modes:
  - Professional
  - Casual
  - Technical
  - Creative
  - Analytical
  - Friendly

### Status Monitoring
- **Connection Status**: Visual indicator of backend health
- **Performance Metrics**: Response time monitoring
- **Error Recovery**: Automatic reconnection attempts

## 🚀 Deployment

### Development
```bash
npm start              # Development server
npm run build          # Production build
npm run test           # Run tests
npm run eject          # Eject from Create React App
```

### Production Build
```bash
npm run build
# Serves optimized build from build/ directory
```

### Integration with Backend
The frontend is designed to work seamlessly with the CAG backend system:
- **Automatic Discovery**: Detects backend availability
- **Graceful Degradation**: Handles backend downtime
- **Real-time Sync**: Updates when backend configuration changes

## 🔍 Features Detail

### AI Chat System
- **Hybrid Search**: Combines vector and keyword search
- **Context Awareness**: Maintains conversation history
- **Document Integration**: Access to uploaded document knowledge base
- **Response Customization**: Adjustable AI behavior and style

### Vector Database Integration
- **Dual Support**: Works with both Qdrant and FAISS
- **Runtime Switching**: Change database without restart
- **Performance Optimization**: Efficient query processing
- **Scalability**: Handles large document collections

## 📚 Documentation

- **[Main Project Docs](../docs/README.md)**: Complete project documentation
- **[Backend Documentation](../backend/docs/README.md)**: Backend API and architecture
- **[Features Guide](../docs/features/README.md)**: Detailed feature explanations
- **[Development Guide](../docs/guides/README.md)**: Development and contribution guidelines

## 🤝 Contributing

1. Follow the main project contribution guidelines
2. Maintain component modularity and reusability
3. Test on multiple screen sizes and browsers
4. Update documentation for new features
5. Follow the established design system

## 📊 Performance

- **Bundle Size**: Optimized with code splitting
- **Loading Time**: < 2s initial load
- **Runtime Performance**: 60fps animations
- **Memory Usage**: Efficient React hooks implementation

---

**Part of the CAG Project** - See [main documentation](../README.md) for complete system overview.

4. **Open your browser:**
   - The app will automatically open at `http://localhost:3000`
   - If it doesn't open automatically, manually navigate to the URL

## Prerequisites

- **Node.js** (version 14 or higher)
- **npm** (comes with Node.js)
- **Backend server** running on `http://127.0.0.1:8000`

## Backend Integration

The React frontend communicates with the FastAPI backend running on port 8000. Make sure your backend is running before using the frontend.

### Backend Endpoints Used:
- `GET /status` - Check system status
- `POST /ask` - Submit questions to ASK_GILLU

## Response Styles

Choose from 6 different AI response styles:

1. **Default** - Comprehensive SRMU assistant
2. **Professional** - Formal, consultative responses
3. **Casual** - Friendly, conversational tone
4. **Academic** - Scholarly, research-focused answers
5. **Bullet Points** - Organized, easy-to-scan format
6. **Expert** - Authoritative, technical expertise

## Project Structure

```
frontend-react/
├── public/
│   └── index.html          # Main HTML template
├── src/
│   ├── App.js             # Main React component
│   ├── index.js           # React entry point
│   └── index.css          # Global styles
├── package.json           # Dependencies and scripts
└── README.md             # This file
```

## Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App (not recommended)

## Customization

### Changing Colors
Edit the CSS variables in `src/index.css` to customize the color scheme:

```css
/* Update gradient colors */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Adding New Response Styles
Add new templates to the `PROMPT_TEMPLATES` object in `src/App.js`:

```javascript
const PROMPT_TEMPLATES = {
  // ...existing templates...
  "Custom Style": "Your custom prompt here..."
};
```

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge

## Development

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

For more information about Create React App, check out the [documentation](https://facebook.github.io/create-react-app/docs/getting-started).

## Troubleshooting

### Backend Connection Issues
- Ensure the FastAPI backend is running on `http://127.0.0.1:8000`
- Check that CORS is properly configured in the backend
- Verify no firewall is blocking the connection

### Installation Issues
- Make sure you have Node.js installed
- Try deleting `node_modules` and running `npm install` again
- Check that you're in the correct directory

### Port Conflicts
- If port 3000 is in use, React will offer to run on a different port
- You can also specify a different port: `PORT=3001 npm start`

## Production Build

To create a production build:

```bash
npm run build
```

This creates a `build` folder with optimized files ready for deployment.
