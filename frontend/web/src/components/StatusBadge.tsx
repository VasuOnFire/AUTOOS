'use client';

import { motion } from 'framer-motion';
import { 
  CheckCircle2, 
  XCircle, 
  Clock, 
  Loader2, 
  Pause, 
  AlertCircle 
} from 'lucide-react';

export type Status = 
  | 'pending' 
  | 'running' 
  | 'paused' 
  | 'completed' 
  | 'failed' 
  | 'cancelled';

const statusConfig = {
  pending: {
    icon: Clock,
    color: 'text-yellow-400',
    bg: 'bg-yellow-500/10',
    border: 'border-yellow-500/30',
    label: 'Pending',
    animate: false,
  },
  running: {
    icon: Loader2,
    color: 'text-blue-400',
    bg: 'bg-blue-500/10',
    border: 'border-blue-500/30',
    label: 'Running',
    animate: true,
  },
  paused: {
    icon: Pause,
    color: 'text-gray-400',
    bg: 'bg-gray-500/10',
    border: 'border-gray-500/30',
    label: 'Paused',
    animate: false,
  },
  completed: {
    icon: CheckCircle2,
    color: 'text-green-400',
    bg: 'bg-green-500/10',
    border: 'border-green-500/30',
    label: 'Completed',
    animate: false,
  },
  failed: {
    icon: XCircle,
    color: 'text-red-400',
    bg: 'bg-red-500/10',
    border: 'border-red-500/30',
    label: 'Failed',
    animate: false,
  },
  cancelled: {
    icon: AlertCircle,
    color: 'text-orange-400',
    bg: 'bg-orange-500/10',
    border: 'border-orange-500/30',
    label: 'Cancelled',
    animate: false,
  },
};

export function StatusBadge({ 
  status, 
  size = 'md',
  showLabel = true,
}: { 
  status: Status;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}) {
  const config = statusConfig[status];
  const Icon = config.icon;

  const sizes = {
    sm: {
      container: 'px-2 py-1 text-xs',
      icon: 'w-3 h-3',
    },
    md: {
      container: 'px-3 py-1.5 text-sm',
      icon: 'w-4 h-4',
    },
    lg: {
      container: 'px-4 py-2 text-base',
      icon: 'w-5 h-5',
    },
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`
        ${config.bg} ${config.border} ${sizes[size].container}
        inline-flex items-center space-x-2
        border rounded-full backdrop-blur-sm
      `}
    >
      <Icon 
        className={`${config.color} ${sizes[size].icon} ${config.animate ? 'animate-spin' : ''}`}
      />
      {showLabel && (
        <span className={`${config.color} font-medium`}>
          {config.label}
        </span>
      )}
    </motion.div>
  );
}

export function PulseDot({ 
  color = 'green',
  size = 'md',
}: { 
  color?: 'green' | 'red' | 'yellow' | 'blue';
  size?: 'sm' | 'md' | 'lg';
}) {
  const colors = {
    green: 'bg-green-400',
    red: 'bg-red-400',
    yellow: 'bg-yellow-400',
    blue: 'bg-blue-400',
  };

  const sizes = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
    lg: 'w-4 h-4',
  };

  return (
    <div className="relative flex items-center justify-center">
      <motion.div
        className={`${colors[color]} ${sizes[size]} rounded-full`}
        animate={{
          scale: [1, 1.2, 1],
          opacity: [1, 0.8, 1],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />
      <motion.div
        className={`absolute ${colors[color]} ${sizes[size]} rounded-full opacity-50`}
        animate={{
          scale: [1, 2, 1],
          opacity: [0.5, 0, 0.5],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />
    </div>
  );
}

export function ConfidenceBadge({ 
  confidence,
  size = 'md',
}: { 
  confidence: number;
  size?: 'sm' | 'md' | 'lg';
}) {
  const getColor = (conf: number) => {
    if (conf >= 0.8) return { text: 'text-green-400', bg: 'bg-green-500/10', border: 'border-green-500/30' };
    if (conf >= 0.6) return { text: 'text-yellow-400', bg: 'bg-yellow-500/10', border: 'border-yellow-500/30' };
    return { text: 'text-red-400', bg: 'bg-red-500/10', border: 'border-red-500/30' };
  };

  const colors = getColor(confidence);
  const percentage = Math.round(confidence * 100);

  const sizes = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm',
    lg: 'px-4 py-2 text-base',
  };

  return (
    <div
      className={`
        ${colors.bg} ${colors.border} ${sizes[size]}
        inline-flex items-center space-x-2
        border rounded-full backdrop-blur-sm
      `}
    >
      <div className="relative w-4 h-4">
        <svg className="transform -rotate-90" viewBox="0 0 16 16">
          <circle
            cx="8"
            cy="8"
            r="6"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            className="text-gray-600"
          />
          <circle
            cx="8"
            cy="8"
            r="6"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeDasharray={`${2 * Math.PI * 6}`}
            strokeDashoffset={`${2 * Math.PI * 6 * (1 - confidence)}`}
            className={colors.text}
          />
        </svg>
      </div>
      <span className={`${colors.text} font-semibold`}>
        {percentage}%
      </span>
    </div>
  );
}
