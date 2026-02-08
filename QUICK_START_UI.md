# AUTOOS UI Quick Start Guide

Get the beautiful AUTOOS web interface up and running in minutes!

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
cd frontend/web
npm install
```

### 2. Configure Environment

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Start Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) 🎉

## 🎨 Using the UI Components

### Submit an Intent

The main feature - submit natural language intents:

```tsx
import { IntentInput } from '@/components/IntentInput';

<IntentInput />
```

Try these example intents:
- "Analyze last quarter sales data and create report"
- "Research competitor products and identify gaps"
- "Generate API documentation for user module"

### Display Workflows

Show active workflows with real-time updates:

```tsx
import { WorkflowDashboard } from '@/components/WorkflowDashboard';

<WorkflowDashboard />
```

### Monitor Agents

View active agents and their status:

```tsx
import { AgentTeamView } from '@/components/AgentTeamView';

<AgentTeamView />
```

### View Metrics

Display system metrics and charts:

```tsx
import { MetricsPanel } from '@/components/MetricsPanel';

<MetricsPanel />
```

## 🎭 Adding Animations

### Animate Any Element

```tsx
import { motion } from 'framer-motion';

<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.5 }}
>
  Content
</motion.div>
```

### Use Pre-built Animated Components

```tsx
import { AnimatedCard } from '@/components/AnimatedCard';

<AnimatedCard hover glow gradient>
  Card content
</AnimatedCard>
```

## 🔔 Show Notifications

```tsx
import { toast } from 'react-hot-toast';

// Success
toast.success('Workflow completed!');

// Error
toast.error('Failed to submit intent');

// Info
toast('Processing your request...');

// Custom
toast.custom(
  <div>Custom notification</div>
);
```

## 📦 Access Global State

```tsx
import { useWorkflowStore } from '@/store/workflowStore';

function MyComponent() {
  const { 
    workflows, 
    agents, 
    submitIntent,
    fetchWorkflows 
  } = useWorkflowStore();

  // Submit intent
  const handleSubmit = async () => {
    await submitIntent("My intent");
  };

  // Access workflows
  console.log(workflows);
}
```

## 🎨 Apply Styling

### Use Tailwind Classes

```tsx
<div className="glass rounded-xl p-6 hover-lift">
  Glassmorphism card
</div>
```

### Pre-built Utility Classes

- `glass` - Glassmorphism effect
- `glass-dark` - Dark glass effect
- `gradient-text` - Gradient text
- `gradient-border` - Gradient border
- `neon-text` - Neon glow text
- `neon-border` - Neon glow border
- `hover-lift` - Lift on hover
- `scrollbar-thin` - Thin scrollbar
- `scrollbar-hide` - Hide scrollbar

## 🎯 Common Patterns

### Loading State

```tsx
import { SpinnerLoader } from '@/components/LoadingStates';

{isLoading ? (
  <SpinnerLoader size="lg" />
) : (
  <Content />
)}
```

### Modal Dialog

```tsx
import { Modal, ModalFooter, ModalButton } from '@/components/Modal';

const [isOpen, setIsOpen] = useState(false);

<Modal 
  isOpen={isOpen} 
  onClose={() => setIsOpen(false)}
  title="Confirm Action"
>
  <p>Are you sure?</p>
  <ModalFooter>
    <ModalButton onClick={handleConfirm} variant="primary">
      Confirm
    </ModalButton>
    <ModalButton onClick={() => setIsOpen(false)} variant="secondary">
      Cancel
    </ModalButton>
  </ModalFooter>
</Modal>
```

### Status Display

```tsx
import { StatusBadge, ConfidenceBadge } from '@/components/StatusBadge';

<StatusBadge status="running" />
<ConfidenceBadge confidence={0.92} />
```

### Tooltip

```tsx
import { Tooltip } from '@/components/Tooltip';

<Tooltip content="This is a tooltip" position="top">
  <button>Hover me</button>
</Tooltip>
```

### Progress Bar

```tsx
import { ProgressBar } from '@/components/LoadingStates';

<ProgressBar progress={75} label="Processing" />
```

## 🎨 Customizing Colors

Edit `tailwind.config.js`:

```js
theme: {
  extend: {
    colors: {
      primary: {
        500: '#your-color',
      },
    },
  },
}
```

## 🌈 Adding Background Effects

```tsx
import { 
  FloatingOrbs, 
  ParticleBackground,
  GridBackground 
} from '@/components/ParticleBackground';

// Choose one:
<FloatingOrbs />
<ParticleBackground />
<GridBackground />
```

## 🎭 Creating Custom Animations

In `tailwind.config.js`:

```js
animation: {
  'my-animation': 'myAnimation 2s ease-in-out infinite',
},
keyframes: {
  myAnimation: {
    '0%, 100%': { transform: 'scale(1)' },
    '50%': { transform: 'scale(1.1)' },
  },
}
```

Use it:

```tsx
<div className="animate-my-animation">
  Animated content
</div>
```

## 🔧 Debugging

### Check State

```tsx
import { useWorkflowStore } from '@/store/workflowStore';

const state = useWorkflowStore.getState();
console.log(state);
```

### Enable Zustand DevTools

Already enabled! Open Redux DevTools in browser.

### Check API Calls

Open Network tab in browser DevTools to see API requests.

## 📱 Mobile Testing

```bash
# Get your local IP
ipconfig getifaddr en0  # macOS
ip addr show           # Linux

# Access from mobile
http://YOUR_IP:3000
```

## 🎨 Component Cheat Sheet

| Component | Use Case |
|-----------|----------|
| `AnimatedButton` | Interactive buttons |
| `AnimatedCard` | Content cards |
| `Modal` | Dialogs and overlays |
| `Notification` | Toast messages |
| `StatusBadge` | Status indicators |
| `ConfidenceBadge` | Confidence scores |
| `Tooltip` | Contextual help |
| `ProgressBar` | Progress tracking |
| `SpinnerLoader` | Loading states |
| `ThemeToggle` | Theme switching |

## 🚀 Production Build

```bash
# Build
npm run build

# Start production server
npm start

# Or deploy to Vercel
vercel deploy
```

## 🎯 Best Practices

1. **Always use TypeScript** - Type safety prevents bugs
2. **Memoize expensive components** - Use React.memo
3. **Debounce API calls** - Prevent excessive requests
4. **Handle loading states** - Show spinners/skeletons
5. **Handle error states** - Show error messages
6. **Use semantic HTML** - Better accessibility
7. **Add ARIA labels** - Screen reader support
8. **Test on mobile** - Ensure responsive design
9. **Optimize images** - Use Next.js Image component
10. **Monitor performance** - Use React DevTools Profiler

## 🐛 Common Issues

### Port Already in Use
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### Module Not Found
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Styles Not Updating
```bash
# Restart dev server
# Clear browser cache
# Check tailwind.config.js paths
```

## 📚 Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [Framer Motion](https://www.framer.com/motion/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Zustand](https://github.com/pmndrs/zustand)
- [Recharts](https://recharts.org/)

## 🎉 You're Ready!

Start building beautiful UIs with AUTOOS. All components are documented, typed, and ready to use.

**Happy coding!** 🚀
