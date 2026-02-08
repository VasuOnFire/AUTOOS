# AUTOOS Web Application

Beautiful, modern web interface for the AUTOOS Automation Operating System with advanced UI features, animations, and real-time monitoring.

## Features

### 🎨 Advanced UI Components

- **Glassmorphism Design**: Beautiful glass-effect cards with backdrop blur
- **Smooth Animations**: Framer Motion powered animations throughout
- **Particle Background**: Dynamic floating orbs and particle effects
- **Neon Effects**: Glowing borders and text effects
- **Micro-interactions**: Hover effects, button animations, and transitions

### 🎯 Core Components

#### Layout Components
- `WorkflowDashboard` - Main dashboard with workflow cards and real-time updates
- `AgentTeamView` - Agent team visualization with role-based colors
- `MetricsPanel` - Charts and metrics with Recharts integration
- `IntentInput` - Natural language input with example suggestions

#### UI Components
- `Modal` - Customizable modal with multiple sizes and animations
- `Notification` - Toast notifications with auto-dismiss and progress bar
- `AnimatedButton` - Buttons with shimmer effects and loading states
- `AnimatedCard` - Cards with hover effects and gradient borders
- `StatusBadge` - Status indicators with icons and animations
- `ConfidenceBadge` - Circular progress indicators for confidence scores
- `Tooltip` - Contextual tooltips with multiple positions
- `ThemeToggle` - Dark/light theme switcher with smooth transitions

#### Loading States
- `SpinnerLoader` - Simple spinning loader
- `PulseLoader` - Pulsing dots animation
- `SkeletonLoader` - Shimmer skeleton screens
- `WorkflowLoadingState` - Full workflow loading animation
- `AgentLoadingState` - Agent cards skeleton
- `FullPageLoader` - Full-screen loading overlay
- `ProgressBar` - Animated progress bars

#### Background Effects
- `ParticleBackground` - Canvas-based particle system with connections
- `FloatingOrbs` - Animated gradient orbs
- `GridBackground` - Grid pattern overlay
- `MeshGradientBackground` - Mesh gradient effect

### 🎭 Animations

All animations are powered by Framer Motion and include:

- **Float**: Smooth up/down floating motion
- **Shimmer**: Horizontal shimmer effect
- **Glow**: Pulsing glow animation
- **Pulse**: Opacity pulsing
- **Scale**: Scale in/out transitions
- **Slide**: Slide up/down/left/right
- **Rotate**: Continuous rotation

### 🎨 Styling

#### Tailwind Configuration
- Custom color palette (purple/pink gradients)
- Extended animations and keyframes
- Custom shadows (glow, neon)
- Backdrop blur utilities
- Gradient utilities

#### Global Styles
- Glass morphism effects
- Neon glow effects
- Custom scrollbars
- Gradient text
- Mesh backgrounds

### 📊 State Management

Using Zustand for global state:

```typescript
// Store structure
{
  workflows: Workflow[],
  agents: Agent[],
  metrics: Metric[],
  isLoading: boolean,
  error: string | null,
  
  // Actions
  submitIntent(),
  fetchWorkflows(),
  fetchAgents(),
  fetchMetrics(),
  cancelWorkflow(),
  pauseWorkflow(),
  resumeWorkflow()
}
```

### 🔌 API Integration

All API calls go through the workflow store with automatic error handling:

- `POST /intents` - Submit new intent
- `GET /workflows` - Fetch all workflows
- `GET /agents` - Fetch active agents
- `GET /metrics` - Fetch system metrics
- `DELETE /workflows/:id` - Cancel workflow
- `POST /workflows/:id/pause` - Pause workflow
- `POST /workflows/:id/resume` - Resume workflow

## Getting Started

### Prerequisites

- Node.js 18+
- npm 9+

### Installation

```bash
cd frontend/web
npm install
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### Build

```bash
npm run build
npm start
```

### Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Project Structure

```
src/
├── app/
│   ├── layout.tsx          # Root layout with providers
│   ├── page.tsx            # Home page
│   └── globals.css         # Global styles
├── components/
│   ├── WorkflowDashboard.tsx
│   ├── AgentTeamView.tsx
│   ├── MetricsPanel.tsx
│   ├── IntentInput.tsx
│   ├── Modal.tsx
│   ├── Notification.tsx
│   ├── AnimatedButton.tsx
│   ├── AnimatedCard.tsx
│   ├── LoadingStates.tsx
│   ├── StatusBadge.tsx
│   ├── Tooltip.tsx
│   ├── ThemeToggle.tsx
│   ├── ParticleBackground.tsx
│   └── WorkflowDetailModal.tsx
└── store/
    └── workflowStore.ts    # Zustand store
```

## Component Usage Examples

### Modal

```tsx
import { Modal, ModalFooter, ModalButton } from '@/components/Modal';

<Modal isOpen={isOpen} onClose={onClose} title="My Modal" size="lg">
  <p>Modal content here</p>
  <ModalFooter>
    <ModalButton onClick={onSave} variant="primary">Save</ModalButton>
    <ModalButton onClick={onClose} variant="secondary">Cancel</ModalButton>
  </ModalFooter>
</Modal>
```

### Animated Button

```tsx
import { AnimatedButton } from '@/components/AnimatedButton';
import { Send } from 'lucide-react';

<AnimatedButton
  onClick={handleClick}
  variant="primary"
  size="md"
  icon={Send}
  iconPosition="right"
  loading={isLoading}
>
  Submit
</AnimatedButton>
```

### Status Badge

```tsx
import { StatusBadge, ConfidenceBadge } from '@/components/StatusBadge';

<StatusBadge status="running" size="md" />
<ConfidenceBadge confidence={0.92} size="md" />
```

### Notification

```tsx
import { NotificationContainer } from '@/components/Notification';

<NotificationContainer
  notifications={notifications}
  onClose={handleClose}
/>
```

### Loading States

```tsx
import { 
  SpinnerLoader, 
  WorkflowLoadingState,
  ProgressBar 
} from '@/components/LoadingStates';

<SpinnerLoader size="lg" />
<WorkflowLoadingState />
<ProgressBar progress={75} label="Processing" />
```

## Customization

### Colors

Edit `tailwind.config.js` to customize the color palette:

```js
colors: {
  primary: { /* purple shades */ },
  accent: { /* pink shades */ },
}
```

### Animations

Add custom animations in `tailwind.config.js`:

```js
animation: {
  'my-animation': 'myAnimation 2s ease-in-out infinite',
},
keyframes: {
  myAnimation: {
    '0%, 100%': { /* start/end state */ },
    '50%': { /* middle state */ },
  },
}
```

### Theme

Toggle between dark and light themes using the `ThemeToggle` component. Theme preference is saved to localStorage.

## Performance

- **Code Splitting**: Automatic with Next.js
- **Image Optimization**: Next.js Image component
- **Lazy Loading**: Components loaded on demand
- **Memoization**: React.memo for expensive components
- **Debouncing**: Input debouncing for API calls

## Accessibility

- Semantic HTML elements
- ARIA labels on interactive elements
- Keyboard navigation support
- Focus indicators
- Screen reader friendly

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Contributing

1. Follow the existing component structure
2. Use TypeScript for type safety
3. Add proper prop types and documentation
4. Test on multiple screen sizes
5. Ensure accessibility compliance

## License

Part of the AUTOOS project - see main README for license information.
