'use client';

import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';

export interface AnimatedButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  icon?: LucideIcon;
  iconPosition?: 'left' | 'right';
  disabled?: boolean;
  loading?: boolean;
  className?: string;
}

const variants = {
  primary: 'bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white shadow-lg shadow-purple-500/50',
  secondary: 'bg-white/10 hover:bg-white/20 text-white border border-white/20',
  ghost: 'bg-transparent hover:bg-white/10 text-white',
  danger: 'bg-red-500 hover:bg-red-600 text-white shadow-lg shadow-red-500/50',
};

const sizes = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-base',
  lg: 'px-6 py-3 text-lg',
};

export function AnimatedButton({
  children,
  onClick,
  variant = 'primary',
  size = 'md',
  icon: Icon,
  iconPosition = 'left',
  disabled = false,
  loading = false,
  className = '',
}: AnimatedButtonProps) {
  return (
    <motion.button
      onClick={onClick}
      disabled={disabled || loading}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      className={`
        ${variants[variant]}
        ${sizes[size]}
        ${className}
        rounded-lg font-semibold
        transition-all duration-200
        disabled:opacity-50 disabled:cursor-not-allowed
        flex items-center justify-center space-x-2
        relative overflow-hidden
      `}
    >
      {/* Shimmer effect */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
        initial={{ x: '-100%' }}
        whileHover={{ x: '100%' }}
        transition={{ duration: 0.6 }}
      />

      {/* Content */}
      <span className="relative flex items-center space-x-2">
        {Icon && iconPosition === 'left' && (
          <Icon className={loading ? 'animate-spin' : ''} size={18} />
        )}
        <span>{children}</span>
        {Icon && iconPosition === 'right' && (
          <Icon className={loading ? 'animate-spin' : ''} size={18} />
        )}
      </span>
    </motion.button>
  );
}

export function FloatingActionButton({
  icon: Icon,
  onClick,
  label,
}: {
  icon: LucideIcon;
  onClick: () => void;
  label: string;
}) {
  return (
    <motion.button
      onClick={onClick}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.9 }}
      className="fixed bottom-8 right-8 w-14 h-14 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full shadow-lg shadow-purple-500/50 flex items-center justify-center text-white z-40 group"
      aria-label={label}
    >
      <Icon size={24} />
      
      {/* Tooltip */}
      <motion.div
        initial={{ opacity: 0, x: 10 }}
        whileHover={{ opacity: 1, x: 0 }}
        className="absolute right-full mr-3 px-3 py-2 bg-slate-900 text-white text-sm rounded-lg whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity"
      >
        {label}
      </motion.div>
    </motion.button>
  );
}

export function IconButton({
  icon: Icon,
  onClick,
  variant = 'ghost',
  size = 'md',
  label,
}: {
  icon: LucideIcon;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  label?: string;
}) {
  const iconSizes = {
    sm: 16,
    md: 20,
    lg: 24,
  };

  const buttonSizes = {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-12 h-12',
  };

  return (
    <motion.button
      onClick={onClick}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.9 }}
      className={`
        ${variants[variant]}
        ${buttonSizes[size]}
        rounded-lg
        flex items-center justify-center
        transition-all
      `}
      aria-label={label}
    >
      <Icon size={iconSizes[size]} />
    </motion.button>
  );
}
