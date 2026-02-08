'use client';

import { motion } from 'framer-motion';
import { 
  X, 
  Clock, 
  DollarSign, 
  TrendingUp, 
  CheckCircle2,
  AlertCircle,
  Zap,
  Brain,
  Shield
} from 'lucide-react';
import { Modal, ModalFooter, ModalButton } from './Modal';
import { StatusBadge, ConfidenceBadge } from './StatusBadge';
import { ProgressBar } from './LoadingStates';
import { Workflow } from '@/store/workflowStore';

export interface WorkflowDetailModalProps {
  workflow: Workflow | null;
  isOpen: boolean;
  onClose: () => void;
  onPause?: () => void;
  onResume?: () => void;
  onCancel?: () => void;
}

export function WorkflowDetailModal({
  workflow,
  isOpen,
  onClose,
  onPause,
  onResume,
  onCancel,
}: WorkflowDetailModalProps) {
  if (!workflow) return null;

  const steps = [
    { id: 1, name: 'Intent Parsing', status: 'completed', confidence: 0.95 },
    { id: 2, name: 'Goal Decomposition', status: 'completed', confidence: 0.92 },
    { id: 3, name: 'Agent Spawning', status: 'running', confidence: 0.88 },
    { id: 4, name: 'Tool Execution', status: 'pending', confidence: 0 },
    { id: 5, name: 'Verification', status: 'pending', confidence: 0 },
  ];

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Workflow Details" size="xl">
      <div className="space-y-6">
        {/* Header Info */}
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-white mb-2">
              {workflow.intent}
            </h3>
            <div className="flex items-center space-x-3">
              <StatusBadge status={workflow.status} />
              <ConfidenceBadge confidence={workflow.confidence} />
            </div>
          </div>
        </div>

        {/* Progress */}
        <div>
          <ProgressBar 
            progress={workflow.progress} 
            label="Overall Progress"
          />
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-3 gap-4">
          <MetricCard
            icon={Clock}
            label="Duration"
            value="2m 34s"
            color="blue"
          />
          <MetricCard
            icon={DollarSign}
            label="Cost"
            value={`$${workflow.cost.toFixed(4)}`}
            color="green"
          />
          <MetricCard
            icon={TrendingUp}
            label="Steps"
            value={`${workflow.steps_completed}/${workflow.steps_total}`}
            color="purple"
          />
        </div>

        {/* Execution Steps */}
        <div>
          <h4 className="text-sm font-semibold text-gray-400 mb-3">
            Execution Steps
          </h4>
          <div className="space-y-2">
            {steps.map((step, i) => (
              <motion.div
                key={step.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1 }}
                className="flex items-center justify-between p-3 bg-white/5 rounded-lg border border-white/10"
              >
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center text-purple-400 text-sm font-semibold">
                    {step.id}
                  </div>
                  <span className="text-white">{step.name}</span>
                </div>
                
                <div className="flex items-center space-x-3">
                  {step.confidence > 0 && (
                    <ConfidenceBadge confidence={step.confidence} size="sm" />
                  )}
                  <StatusBadge 
                    status={step.status as any} 
                    size="sm" 
                    showLabel={false}
                  />
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Agent Activity */}
        <div>
          <h4 className="text-sm font-semibold text-gray-400 mb-3">
            Active Agents
          </h4>
          <div className="grid grid-cols-2 gap-3">
            {[
              { name: 'Planner Agent', role: 'PLANNER', status: 'working' },
              { name: 'Executor Agent', role: 'EXECUTOR', status: 'working' },
              { name: 'Verifier Agent', role: 'VERIFIER', status: 'waiting' },
            ].map((agent, i) => (
              <div
                key={i}
                className="p-3 bg-white/5 rounded-lg border border-white/10"
              >
                <div className="flex items-center space-x-2 mb-2">
                  <Brain className="w-4 h-4 text-purple-400" />
                  <span className="text-sm font-medium text-white">
                    {agent.name}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-400">{agent.role}</span>
                  <span className={`text-xs ${
                    agent.status === 'working' ? 'text-green-400' : 'text-gray-400'
                  }`}>
                    {agent.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Audit Trail Preview */}
        <div>
          <h4 className="text-sm font-semibold text-gray-400 mb-3">
            Recent Activity
          </h4>
          <div className="space-y-2 max-h-40 overflow-y-auto scrollbar-thin">
            {[
              { time: '10:23:45', event: 'Intent parsed successfully', type: 'success' },
              { time: '10:23:47', event: 'Goal graph generated', type: 'success' },
              { time: '10:23:49', event: 'Spawned 3 agents', type: 'info' },
              { time: '10:23:52', event: 'Agent verification in progress', type: 'info' },
            ].map((log, i) => (
              <div
                key={i}
                className="flex items-start space-x-3 text-sm p-2 rounded hover:bg-white/5"
              >
                <span className="text-gray-500 font-mono">{log.time}</span>
                <span className="text-gray-300 flex-1">{log.event}</span>
                {log.type === 'success' && (
                  <CheckCircle2 className="w-4 h-4 text-green-400" />
                )}
                {log.type === 'info' && (
                  <AlertCircle className="w-4 h-4 text-blue-400" />
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      <ModalFooter>
        {workflow.status === 'running' && onPause && (
          <ModalButton onClick={onPause} variant="secondary">
            Pause
          </ModalButton>
        )}
        {workflow.status === 'paused' && onResume && (
          <ModalButton onClick={onResume} variant="primary">
            Resume
          </ModalButton>
        )}
        {(workflow.status === 'running' || workflow.status === 'paused') && onCancel && (
          <ModalButton onClick={onCancel} variant="danger">
            Cancel
          </ModalButton>
        )}
        <ModalButton onClick={onClose} variant="secondary">
          Close
        </ModalButton>
      </ModalFooter>
    </Modal>
  );
}

function MetricCard({
  icon: Icon,
  label,
  value,
  color,
}: {
  icon: any;
  label: string;
  value: string;
  color: 'blue' | 'green' | 'purple';
}) {
  const colors = {
    blue: 'text-blue-400 bg-blue-500/10 border-blue-500/30',
    green: 'text-green-400 bg-green-500/10 border-green-500/30',
    purple: 'text-purple-400 bg-purple-500/10 border-purple-500/30',
  };

  return (
    <div className={`${colors[color]} p-4 rounded-lg border backdrop-blur-sm`}>
      <div className="flex items-center space-x-2 mb-2">
        <Icon className="w-4 h-4" />
        <span className="text-xs text-gray-400">{label}</span>
      </div>
      <p className="text-xl font-bold">{value}</p>
    </div>
  );
}
