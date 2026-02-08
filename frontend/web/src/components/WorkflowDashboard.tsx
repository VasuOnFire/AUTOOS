'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Activity,
  CheckCircle2,
  Clock,
  AlertCircle,
  TrendingUp,
  Zap,
  Eye,
  Play,
  Pause,
  RotateCcw,
} from 'lucide-react';

interface Workflow {
  id: string;
  name: string;
  status: 'running' | 'completed' | 'failed' | 'paused';
  progress: number;
  startTime: string;
  estimatedTime: string;
  cost: number;
  confidence: number;
  steps: {
    name: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
  }[];
}

export function WorkflowDashboard() {
  const [workflows, setWorkflows] = useState<Workflow[]>([
    {
      id: 'wf-001',
      name: 'Analyze Q4 Sales Data',
      status: 'running',
      progress: 65,
      startTime: '2 min ago',
      estimatedTime: '1 min remaining',
      cost: 0.15,
      confidence: 0.89,
      steps: [
        { name: 'Data Collection', status: 'completed' },
        { name: 'Analysis', status: 'running' },
        { name: 'Report Generation', status: 'pending' },
      ],
    },
    {
      id: 'wf-002',
      name: 'Generate API Documentation',
      status: 'completed',
      progress: 100,
      startTime: '5 min ago',
      estimatedTime: 'Completed',
      cost: 0.08,
      confidence: 0.95,
      steps: [
        { name: 'Code Analysis', status: 'completed' },
        { name: 'Doc Generation', status: 'completed' },
        { name: 'Formatting', status: 'completed' },
      ],
    },
  ]);

  const [selectedWorkflow, setSelectedWorkflow] = useState<string | null>(null);

  return (
    <div className="space-y-6">
      {/* Active Workflows Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {workflows.map((workflow, index) => (
          <motion.div
            key={workflow.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            onClick={() => setSelectedWorkflow(workflow.id)}
            className="group relative cursor-pointer"
          >
            {/* Glassmorphism Card */}
            <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl border border-white/20 p-6 hover:border-primary-500/50 transition-all duration-300 hover:shadow-glow">
              {/* Animated Background Gradient */}
              <div className="absolute inset-0 bg-gradient-to-br from-primary-500/10 via-transparent to-accent-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

              {/* Status Indicator */}
              <div className="absolute top-4 right-4">
                <StatusBadge status={workflow.status} />
              </div>

              {/* Content */}
              <div className="relative z-10">
                <h3 className="text-xl font-bold text-white mb-2 group-hover:text-primary-300 transition-colors">
                  {workflow.name}
                </h3>

                <div className="flex items-center space-x-4 text-sm text-gray-400 mb-4">
                  <div className="flex items-center space-x-1">
                    <Clock className="w-4 h-4" />
                    <span>{workflow.startTime}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Zap className="w-4 h-4" />
                    <span>${workflow.cost.toFixed(2)}</span>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="mb-4">
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-gray-300">Progress</span>
                    <span className="text-primary-400 font-semibold">
                      {workflow.progress}%
                    </span>
                  </div>
                  <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${workflow.progress}%` }}
                      transition={{ duration: 1, ease: 'easeOut' }}
                      className="h-full bg-gradient-to-r from-primary-500 to-accent-500 rounded-full relative"
                    >
                      <div className="absolute inset-0 bg-white/30 animate-shimmer" />
                    </motion.div>
                  </div>
                </div>

                {/* Steps */}
                <div className="space-y-2">
                  {workflow.steps.map((step, i) => (
                    <div
                      key={i}
                      className="flex items-center space-x-2 text-sm"
                    >
                      <StepIcon status={step.status} />
                      <span
                        className={
                          step.status === 'completed'
                            ? 'text-green-400'
                            : step.status === 'running'
                            ? 'text-primary-400'
                            : 'text-gray-500'
                        }
                      >
                        {step.name}
                      </span>
                    </div>
                  ))}
                </div>

                {/* Confidence Score */}
                <div className="mt-4 pt-4 border-t border-white/10">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">Confidence</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-24 h-1.5 bg-white/10 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-green-500 to-emerald-400"
                          style={{ width: `${workflow.confidence * 100}%` }}
                        />
                      </div>
                      <span className="text-sm font-semibold text-green-400">
                        {(workflow.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="mt-4 flex space-x-2">
                  <ActionButton icon={Eye} label="View" />
                  {workflow.status === 'running' && (
                    <ActionButton icon={Pause} label="Pause" />
                  )}
                  {workflow.status === 'paused' && (
                    <ActionButton icon={Play} label="Resume" />
                  )}
                  {workflow.status === 'failed' && (
                    <ActionButton icon={RotateCcw} label="Retry" />
                  )}
                </div>
              </div>

              {/* Hover Glow Effect */}
              <div className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-primary-500/20 to-accent-500/20 blur-xl" />
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Workflow Details Modal */}
      <AnimatePresence>
        {selectedWorkflow && (
          <WorkflowDetailsModal
            workflow={workflows.find((w) => w.id === selectedWorkflow)!}
            onClose={() => setSelectedWorkflow(null)}
          />
        )}
      </AnimatePresence>
    </div>
  );
}

function StatusBadge({ status }: { status: Workflow['status'] }) {
  const config = {
    running: {
      icon: Activity,
      color: 'from-blue-500 to-cyan-500',
      text: 'Running',
      animate: 'animate-pulse',
    },
    completed: {
      icon: CheckCircle2,
      color: 'from-green-500 to-emerald-500',
      text: 'Completed',
      animate: '',
    },
    failed: {
      icon: AlertCircle,
      color: 'from-red-500 to-rose-500',
      text: 'Failed',
      animate: '',
    },
    paused: {
      icon: Clock,
      color: 'from-yellow-500 to-orange-500',
      text: 'Paused',
      animate: '',
    },
  };

  const { icon: Icon, color, text, animate } = config[status];

  return (
    <div
      className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-full bg-gradient-to-r ${color} ${animate}`}
    >
      <Icon className="w-3.5 h-3.5 text-white" />
      <span className="text-xs font-semibold text-white">{text}</span>
    </div>
  );
}

function StepIcon({ status }: { status: string }) {
  if (status === 'completed') {
    return <CheckCircle2 className="w-4 h-4 text-green-400" />;
  }
  if (status === 'running') {
    return (
      <div className="w-4 h-4 rounded-full border-2 border-primary-400 border-t-transparent animate-spin" />
    );
  }
  return <div className="w-4 h-4 rounded-full border-2 border-gray-600" />;
}

function ActionButton({ icon: Icon, label }: { icon: any; label: string }) {
  return (
    <button className="flex items-center space-x-1.5 px-3 py-1.5 bg-white/5 hover:bg-white/10 border border-white/10 hover:border-primary-500/50 rounded-lg text-sm text-gray-300 hover:text-white transition-all duration-200">
      <Icon className="w-3.5 h-3.5" />
      <span>{label}</span>
    </button>
  );
}

function WorkflowDetailsModal({
  workflow,
  onClose,
}: {
  workflow: Workflow;
  onClose: () => void;
}) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
      className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-6"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        onClick={(e) => e.stopPropagation()}
        className="bg-gradient-to-br from-slate-900 to-slate-800 border border-white/20 rounded-3xl p-8 max-w-2xl w-full max-h-[80vh] overflow-y-auto"
      >
        <h2 className="text-3xl font-bold text-white mb-6">{workflow.name}</h2>
        {/* Add more detailed workflow information here */}
        <button
          onClick={onClose}
          className="mt-6 px-6 py-3 bg-gradient-to-r from-primary-500 to-accent-500 text-white rounded-xl font-semibold hover:shadow-glow transition-all"
        >
          Close
        </button>
      </motion.div>
    </motion.div>
  );
}
