'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Users,
  Brain,
  Zap,
  Shield,
  Search,
  FileText,
  Code,
  BarChart3,
  MessageSquare,
  Activity,
  CheckCircle2,
  Clock,
} from 'lucide-react';

interface Agent {
  id: string;
  name: string;
  role: string;
  status: 'active' | 'idle' | 'busy';
  avatar: string;
  tasksCompleted: number;
  successRate: number;
  currentTask?: string;
  capabilities: string[];
}

const roleIcons = {
  leader: Users,
  researcher: Search,
  analyst: BarChart3,
  executor: Zap,
  reviewer: Shield,
  coder: Code,
  writer: FileText,
};

const roleColors = {
  leader: 'from-purple-500 to-pink-500',
  researcher: 'from-blue-500 to-cyan-500',
  analyst: 'from-green-500 to-emerald-500',
  executor: 'from-yellow-500 to-orange-500',
  reviewer: 'from-red-500 to-rose-500',
  coder: 'from-indigo-500 to-purple-500',
  writer: 'from-teal-500 to-green-500',
};

export function AgentTeamView() {
  const [agents] = useState<Agent[]>([
    {
      id: 'agent-001',
      name: 'Alpha',
      role: 'leader',
      status: 'active',
      avatar: '🎯',
      tasksCompleted: 156,
      successRate: 0.94,
      currentTask: 'Coordinating team workflow',
      capabilities: ['Planning', 'Coordination', 'Decision Making'],
    },
    {
      id: 'agent-002',
      name: 'Beta',
      role: 'researcher',
      status: 'busy',
      avatar: '🔍',
      tasksCompleted: 203,
      successRate: 0.91,
      currentTask: 'Gathering market data',
      capabilities: ['Web Search', 'Data Collection', 'Analysis'],
    },
    {
      id: 'agent-003',
      name: 'Gamma',
      role: 'analyst',
      status: 'active',
      avatar: '📊',
      tasksCompleted: 178,
      successRate: 0.96,
      capabilities: ['Statistical Analysis', 'Pattern Recognition', 'Insights'],
    },
    {
      id: 'agent-004',
      name: 'Delta',
      role: 'coder',
      status: 'idle',
      avatar: '💻',
      tasksCompleted: 142,
      successRate: 0.89,
      capabilities: ['Code Generation', 'Debugging', 'Optimization'],
    },
  ]);

  return (
    <div className="space-y-8">
      {/* Team Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <TeamStatCard
          label="Active Agents"
          value="24"
          change="+3"
          icon={Users}
          color="from-purple-500 to-pink-500"
        />
        <TeamStatCard
          label="Tasks Completed"
          value="1,247"
          change="+156"
          icon={CheckCircle2}
          color="from-green-500 to-emerald-500"
        />
        <TeamStatCard
          label="Success Rate"
          value="94%"
          change="+2%"
          icon={Activity}
          color="from-blue-500 to-cyan-500"
        />
        <TeamStatCard
          label="Avg Response"
          value="1.8s"
          change="-0.3s"
          icon={Zap}
          color="from-yellow-500 to-orange-500"
        />
      </div>

      {/* Agent Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {agents.map((agent, index) => (
          <AgentCard key={agent.id} agent={agent} index={index} />
        ))}
      </div>

      {/* Team Communication */}
      <TeamCommunication />
    </div>
  );
}

function TeamStatCard({
  label,
  value,
  change,
  icon: Icon,
  color,
}: {
  label: string;
  value: string;
  change: string;
  icon: any;
  color: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="relative group"
    >
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl border border-white/20 p-6 hover:border-primary-500/50 transition-all duration-300">
        {/* Icon Background */}
        <div
          className={`absolute top-4 right-4 w-12 h-12 rounded-xl bg-gradient-to-br ${color} opacity-20 group-hover:opacity-30 transition-opacity`}
        />

        {/* Icon */}
        <div
          className={`w-10 h-10 rounded-lg bg-gradient-to-br ${color} flex items-center justify-center mb-4`}
        >
          <Icon className="w-5 h-5 text-white" />
        </div>

        {/* Content */}
        <p className="text-sm text-gray-400 mb-1">{label}</p>
        <div className="flex items-end justify-between">
          <p className="text-3xl font-bold text-white">{value}</p>
          <span className="text-sm text-green-400 font-semibold">{change}</span>
        </div>
      </div>
    </motion.div>
  );
}

function AgentCard({ agent, index }: { agent: Agent; index: number }) {
  const RoleIcon = roleIcons[agent.role as keyof typeof roleIcons];
  const roleColor = roleColors[agent.role as keyof typeof roleColors];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className="group relative"
    >
      {/* Card */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl border border-white/20 p-6 hover:border-primary-500/50 transition-all duration-300 hover:shadow-glow">
        {/* Status Indicator */}
        <div className="absolute top-4 right-4">
          <div
            className={`w-3 h-3 rounded-full ${
              agent.status === 'active'
                ? 'bg-green-400 animate-pulse'
                : agent.status === 'busy'
                ? 'bg-yellow-400 animate-pulse'
                : 'bg-gray-500'
            }`}
          />
        </div>

        {/* Avatar */}
        <div className="relative mb-4">
          <div
            className={`w-20 h-20 rounded-2xl bg-gradient-to-br ${roleColor} flex items-center justify-center text-4xl mb-3 group-hover:scale-110 transition-transform duration-300`}
          >
            {agent.avatar}
          </div>
          <div
            className={`absolute -bottom-2 -right-2 w-10 h-10 rounded-xl bg-gradient-to-br ${roleColor} flex items-center justify-center`}
          >
            <RoleIcon className="w-5 h-5 text-white" />
          </div>
        </div>

        {/* Info */}
        <h3 className="text-xl font-bold text-white mb-1">{agent.name}</h3>
        <p className="text-sm text-gray-400 capitalize mb-4">{agent.role}</p>

        {/* Current Task */}
        {agent.currentTask && (
          <div className="mb-4 p-3 bg-white/5 rounded-lg border border-white/10">
            <p className="text-xs text-gray-400 mb-1">Current Task</p>
            <p className="text-sm text-white">{agent.currentTask}</p>
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="p-3 bg-white/5 rounded-lg">
            <p className="text-xs text-gray-400 mb-1">Tasks</p>
            <p className="text-lg font-bold text-white">{agent.tasksCompleted}</p>
          </div>
          <div className="p-3 bg-white/5 rounded-lg">
            <p className="text-xs text-gray-400 mb-1">Success</p>
            <p className="text-lg font-bold text-green-400">
              {(agent.successRate * 100).toFixed(0)}%
            </p>
          </div>
        </div>

        {/* Capabilities */}
        <div className="space-y-2">
          <p className="text-xs text-gray-400">Capabilities</p>
          <div className="flex flex-wrap gap-1.5">
            {agent.capabilities.map((cap, i) => (
              <span
                key={i}
                className="px-2 py-1 bg-white/10 rounded-md text-xs text-gray-300"
              >
                {cap}
              </span>
            ))}
          </div>
        </div>

        {/* Hover Glow */}
        <div className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
          <div
            className={`absolute inset-0 rounded-2xl bg-gradient-to-r ${roleColor} opacity-20 blur-xl`}
          />
        </div>
      </div>
    </motion.div>
  );
}

function TeamCommunication() {
  const messages = [
    {
      from: 'Alpha',
      to: 'Beta',
      message: 'Please gather competitor pricing data',
      time: '2m ago',
      avatar: '🎯',
    },
    {
      from: 'Beta',
      to: 'Gamma',
      message: 'Data collected, ready for analysis',
      time: '1m ago',
      avatar: '🔍',
    },
    {
      from: 'Gamma',
      to: 'Alpha',
      message: 'Analysis complete, insights ready',
      time: '30s ago',
      avatar: '📊',
    },
  ];

  return (
    <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl border border-white/20 p-6">
      <div className="flex items-center space-x-3 mb-6">
        <MessageSquare className="w-6 h-6 text-primary-400" />
        <h3 className="text-xl font-bold text-white">Team Communication</h3>
        <div className="flex-1" />
        <div className="px-3 py-1 bg-green-500/20 rounded-full">
          <span className="text-xs text-green-400 font-semibold">
            {messages.length} messages
          </span>
        </div>
      </div>

      <div className="space-y-3">
        {messages.map((msg, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.1 }}
            className="flex items-start space-x-3 p-4 bg-white/5 rounded-xl border border-white/10 hover:border-primary-500/30 transition-all"
          >
            <div className="text-2xl">{msg.avatar}</div>
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-1">
                <span className="text-sm font-semibold text-white">{msg.from}</span>
                <span className="text-xs text-gray-500">→</span>
                <span className="text-sm text-gray-400">{msg.to}</span>
                <span className="text-xs text-gray-500">{msg.time}</span>
              </div>
              <p className="text-sm text-gray-300">{msg.message}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
