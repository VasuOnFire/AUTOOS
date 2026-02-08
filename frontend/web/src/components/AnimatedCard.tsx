'use client';

import { motion } from 'framer-motion';
import { ReactNode } from 'react';

export interface AnimatedCardProps {
  children: ReactNode;
  className?: string;
  hover?: boolean;
  glow?: boolean;
  gradient?: boolean;
}

export function AnimatedCard({
  children,
  className = '',
  hover = true,
  glow = false,
  gradient = false,
}: AnimatedCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={hover ? { y: -4, scale: 1.02 } : {}}
      transition={{ duration: 0.3 }}
      className={`
        ${className}
        ${gradient ? 'gradient-border' : 'border border-white/10'}
        ${glow ? 'shadow-glow' : 'shadow-lg'}
        bg-white/5 backdrop-blur-xl rounded-xl
        transition-all duration-300
      `}
    >
      {children}
    </motion.div>
  );
}

export function GlassCard({
  children,
  className = '',
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.02 }}
      className={`
        ${className}
        glass-card rounded-xl p-6
        hover-lift
      `}
    >
      {children}
    </motion.div>
  );
}

export function NeonCard({
  children,
  className = '',
  color = 'purple',
}: {
  children: ReactNode;
  className?: string;
  color?: 'purple' | 'pink' | 'blue' | 'green';
}) {
  const colors = {
    purple: 'shadow-purple-500/50 border-purple-500/30',
    pink: 'shadow-pink-500/50 border-pink-500/30',
    blue: 'shadow-blue-500/50 border-blue-500/30',
    green: 'shadow-green-500/50 border-green-500/30',
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      whileHover={{ boxShadow: '0 0 30px rgba(168, 85, 247, 0.6)' }}
      className={`
        ${className}
        ${colors[color]}
        bg-slate-900/50 backdrop-blur-xl
        border rounded-xl p-6
        shadow-lg
        transition-all duration-300
      `}
    >
      {children}
    </motion.div>
  );
}

export function ExpandableCard({
  title,
  children,
  defaultExpanded = false,
}: {
  title: string;
  children: ReactNode;
  defaultExpanded?: boolean;
}) {
  const [isExpanded, setIsExpanded] = React.useState(defaultExpanded);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="glass-card rounded-xl overflow-hidden"
    >
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-white/5 transition-colors"
      >
        <h3 className="text-lg font-semibold text-white">{title}</h3>
        <motion.div
          animate={{ rotate: isExpanded ? 180 : 0 }}
          transition={{ duration: 0.3 }}
        >
          <svg
            className="w-5 h-5 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 9l-7 7-7-7"
            />
          </svg>
        </motion.div>
      </button>

      <motion.div
        initial={false}
        animate={{
          height: isExpanded ? 'auto' : 0,
          opacity: isExpanded ? 1 : 0,
        }}
        transition={{ duration: 0.3 }}
        className="overflow-hidden"
      >
        <div className="px-6 pb-4 border-t border-white/10">
          {children}
        </div>
      </motion.div>
    </motion.div>
  );
}

import React from 'react';

export function HoverCard({
  children,
  hoverContent,
}: {
  children: ReactNode;
  hoverContent: ReactNode;
}) {
  const [isHovered, setIsHovered] = React.useState(false);

  return (
    <div
      className="relative"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {children}

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{
          opacity: isHovered ? 1 : 0,
          y: isHovered ? 0 : 10,
        }}
        transition={{ duration: 0.2 }}
        className="absolute z-10 top-full left-0 mt-2 p-4 bg-slate-900 border border-white/20 rounded-xl shadow-xl min-w-[200px]"
        style={{ pointerEvents: isHovered ? 'auto' : 'none' }}
      >
        {hoverContent}
      </motion.div>
    </div>
  );
}
