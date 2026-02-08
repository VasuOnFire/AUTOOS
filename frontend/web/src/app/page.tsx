'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Brain, 
  Zap, 
  Shield, 
  TrendingUp, 
  Users, 
  Activity,
  ArrowRight,
  CheckCircle2
} from 'lucide-react';
import { WorkflowDashboard } from '@/components/WorkflowDashboard';
import { AgentTeamView } from '@/components/AgentTeamView';
import { MetricsPanel } from '@/components/MetricsPanel';
import { IntentInput } from '@/components/IntentInput';
import { ThemeToggle } from '@/components/ThemeToggle';
import { FloatingOrbs } from '@/components/ParticleBackground';

export default function HomePage() {
  const [activeView, setActiveView] = useState<'dashboard' | 'agents' | 'metrics'>('dashboard');

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative">
      {/* Animated Background */}
      <FloatingOrbs />
      
      {/* Header */}
      <header className="border-b border-white/10 bg-black/20 backdrop-blur-xl relative z-10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">AUTOOS</h1>
                <p className="text-xs text-purple-300">Omega Edition</p>
              </div>
            </div>

            <nav className="flex items-center space-x-6">
              <button
                onClick={() => setActiveView('dashboard')}
                className={`px-4 py-2 rounded-lg transition-all ${
                  activeView === 'dashboard'
                    ? 'bg-purple-500 text-white'
                    : 'text-gray-300 hover:text-white'
                }`}
              >
                Dashboard
              </button>
              <button
                onClick={() => setActiveView('agents')}
                className={`px-4 py-2 rounded-lg transition-all ${
                  activeView === 'agents'
                    ? 'bg-purple-500 text-white'
                    : 'text-gray-300 hover:text-white'
                }`}
              >
                Agents
              </button>
              <button
                onClick={() => setActiveView('metrics')}
                className={`px-4 py-2 rounded-lg transition-all ${
                  activeView === 'metrics'
                    ? 'bg-purple-500 text-white'
                    : 'text-gray-300 hover:text-white'
                }`}
              >
                Metrics
              </button>
              
              <div className="ml-4">
                <ThemeToggle />
              </div>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-6 py-12 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h2 className="text-5xl font-bold text-white mb-4">
            The Automation Operating System
          </h2>
          <p className="text-xl text-purple-200 mb-8">
            Multi-LLM orchestration • Autonomous agents • Self-healing • Production-ready
          </p>

          {/* Feature Pills */}
          <div className="flex flex-wrap justify-center gap-3 mb-8">
            {[
              { icon: Brain, text: 'Multi-LLM Intelligence' },
              { icon: Zap, text: 'Autonomous Agents' },
              { icon: Shield, text: 'Self-Healing' },
              { icon: TrendingUp, text: 'Meta-Learning' },
              { icon: Users, text: 'Collaborative Teams' },
              { icon: Activity, text: 'Real-time Monitoring' },
            ].map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.1 }}
                className="flex items-center space-x-2 px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full border border-white/20"
              >
                <feature.icon className="w-4 h-4 text-purple-300" />
                <span className="text-sm text-white">{feature.text}</span>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Intent Input */}
        <IntentInput />

        {/* Main Content */}
        <div className="mt-12">
          {activeView === 'dashboard' && <WorkflowDashboard />}
          {activeView === 'agents' && <AgentTeamView />}
          {activeView === 'metrics' && <MetricsPanel />}
        </div>
      </section>

      {/* Stats Bar */}
      <section className="border-t border-white/10 bg-black/20 backdrop-blur-xl relative z-10">
        <div className="container mx-auto px-6 py-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <StatCard
              label="Success Rate"
              value="92%"
              change="+8%"
              positive
            />
            <StatCard
              label="Active Agents"
              value="24"
              change="+12"
              positive
            />
            <StatCard
              label="Cost Savings"
              value="49%"
              change="+5%"
              positive
            />
            <StatCard
              label="Avg Response"
              value="2.3s"
              change="-0.5s"
              positive
            />
          </div>
        </div>
      </section>
    </div>
  );
}

function StatCard({ 
  label, 
  value, 
  change, 
  positive 
}: { 
  label: string; 
  value: string; 
  change: string; 
  positive: boolean;
}) {
  return (
    <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
      <p className="text-sm text-gray-400 mb-2">{label}</p>
      <div className="flex items-end justify-between">
        <p className="text-3xl font-bold text-white">{value}</p>
        <span className={`text-sm ${positive ? 'text-green-400' : 'text-red-400'}`}>
          {change}
        </span>
      </div>
    </div>
  );
}
