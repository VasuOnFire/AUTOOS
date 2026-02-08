'use client';

import { motion } from 'framer-motion';
import { Loader2, Brain, Zap, Shield } from 'lucide-react';

export function SpinnerLoader({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  return (
    <div className="flex items-center justify-center">
      <Loader2 className={`${sizes[size]} text-purple-500 animate-spin`} />
    </div>
  );
}

export function PulseLoader() {
  return (
    <div className="flex items-center justify-center space-x-2">
      {[0, 1, 2].map((i) => (
        <motion.div
          key={i}
          className="w-3 h-3 bg-purple-500 rounded-full"
          animate={{
            scale: [1, 1.5, 1],
            opacity: [1, 0.5, 1],
          }}
          transition={{
            duration: 1,
            repeat: Infinity,
            delay: i * 0.2,
          }}
        />
      ))}
    </div>
  );
}

export function SkeletonLoader({ className = '' }: { className?: string }) {
  return (
    <div
      className={`
        ${className}
        bg-gradient-to-r from-slate-800 via-slate-700 to-slate-800
        animate-shimmer bg-[length:200%_100%]
        rounded-lg
      `}
    />
  );
}

export function CardSkeleton() {
  return (
    <div className="glass-card rounded-xl p-6 space-y-4">
      <SkeletonLoader className="h-6 w-3/4" />
      <SkeletonLoader className="h-4 w-full" />
      <SkeletonLoader className="h-4 w-5/6" />
      <div className="flex space-x-2">
        <SkeletonLoader className="h-8 w-20" />
        <SkeletonLoader className="h-8 w-20" />
      </div>
    </div>
  );
}

export function WorkflowLoadingState() {
  return (
    <div className="glass-card rounded-xl p-8">
      <div className="flex flex-col items-center justify-center space-y-6">
        <motion.div
          animate={{
            rotate: 360,
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'linear',
          }}
          className="w-16 h-16 border-4 border-purple-500/30 border-t-purple-500 rounded-full"
        />
        
        <div className="text-center">
          <h3 className="text-xl font-bold text-white mb-2">
            Processing Workflow
          </h3>
          <p className="text-gray-400">
            Orchestrating agents and analyzing intent...
          </p>
        </div>

        <div className="space-y-3 w-full max-w-md">
          {[
            { icon: Brain, text: 'Analyzing intent with multi-LLM verification' },
            { icon: Zap, text: 'Spawning autonomous agents' },
            { icon: Shield, text: 'Applying security policies' },
          ].map((step, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.3 }}
              className="flex items-center space-x-3 text-sm text-gray-300"
            >
              <step.icon className="w-4 h-4 text-purple-400" />
              <span>{step.text}</span>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}

export function AgentLoadingState() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {[1, 2, 3].map((i) => (
        <div key={i} className="glass-card rounded-xl p-6">
          <div className="flex items-center space-x-3 mb-4">
            <SkeletonLoader className="w-12 h-12 rounded-full" />
            <div className="flex-1 space-y-2">
              <SkeletonLoader className="h-4 w-24" />
              <SkeletonLoader className="h-3 w-32" />
            </div>
          </div>
          <SkeletonLoader className="h-20 w-full" />
        </div>
      ))}
    </div>
  );
}

export function FullPageLoader({ message = 'Loading...' }: { message?: string }) {
  return (
    <div className="fixed inset-0 bg-slate-900/95 backdrop-blur-sm z-50 flex items-center justify-center">
      <div className="text-center">
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            rotate: [0, 180, 360],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          className="w-20 h-20 mx-auto mb-6"
        >
          <div className="w-full h-full bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl" />
        </motion.div>
        
        <h2 className="text-2xl font-bold text-white mb-2">AUTOOS</h2>
        <p className="text-gray-400">{message}</p>
      </div>
    </div>
  );
}

export function ProgressBar({ 
  progress, 
  label 
}: { 
  progress: number; 
  label?: string;
}) {
  return (
    <div className="space-y-2">
      {label && (
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-300">{label}</span>
          <span className="text-purple-400 font-semibold">{progress}%</span>
        </div>
      )}
      
      <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
          className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full"
        />
      </div>
    </div>
  );
}
