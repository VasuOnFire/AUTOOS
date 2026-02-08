'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Clock,
  Zap,
  Activity,
  BarChart3,
  PieChart,
} from 'lucide-react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart as RePieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

const performanceData = [
  { time: '00:00', success: 85, cost: 0.12, latency: 2.1 },
  { time: '04:00', success: 88, cost: 0.10, latency: 1.9 },
  { time: '08:00', success: 92, cost: 0.09, latency: 1.7 },
  { time: '12:00', success: 94, cost: 0.08, latency: 1.5 },
  { time: '16:00', success: 91, cost: 0.11, latency: 1.8 },
  { time: '20:00', success: 89, cost: 0.13, latency: 2.0 },
];

const modelUsageData = [
  { name: 'GPT-4', value: 35, color: '#a855f7' },
  { name: 'Claude-Opus', value: 25, color: '#ec4899' },
  { name: 'GPT-3.5', value: 30, color: '#3b82f6' },
  { name: 'Claude-Haiku', value: 10, color: '#10b981' },
];

const agentActivityData = [
  { agent: 'Alpha', tasks: 45 },
  { agent: 'Beta', tasks: 38 },
  { agent: 'Gamma', tasks: 42 },
  { agent: 'Delta', tasks: 35 },
  { agent: 'Epsilon', tasks: 40 },
];

export function MetricsPanel() {
  const [timeRange, setTimeRange] = useState<'24h' | '7d' | '30d'>('24h');

  return (
    <div className="space-y-6">
      {/* Time Range Selector */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">System Metrics</h2>
        <div className="flex space-x-2">
          {(['24h', '7d', '30d'] as const).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                timeRange === range
                  ? 'bg-gradient-to-r from-primary-500 to-accent-500 text-white shadow-glow'
                  : 'bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white'
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          icon={TrendingUp}
          label="Success Rate"
          value="94.2%"
          change="+2.3%"
          trend="up"
          color="from-green-500 to-emerald-500"
        />
        <MetricCard
          icon={DollarSign}
          label="Total Cost"
          value="$127.45"
          change="-18%"
          trend="down"
          color="from-blue-500 to-cyan-500"
        />
        <MetricCard
          icon={Clock}
          label="Avg Latency"
          value="1.8s"
          change="-0.4s"
          trend="down"
          color="from-purple-500 to-pink-500"
        />
        <MetricCard
          icon={Zap}
          label="Workflows"
          value="1,247"
          change="+156"
          trend="up"
          color="from-yellow-500 to-orange-500"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Performance Over Time */}
        <ChartCard title="Performance Over Time" icon={Activity}>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={performanceData}>
              <defs>
                <linearGradient id="successGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#a855f7" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#a855f7" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
              <XAxis dataKey="time" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1e293b',
                  border: '1px solid #ffffff20',
                  borderRadius: '12px',
                }}
              />
              <Area
                type="monotone"
                dataKey="success"
                stroke="#a855f7"
                fillOpacity={1}
                fill="url(#successGradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Model Usage Distribution */}
        <ChartCard title="Model Usage Distribution" icon={PieChart}>
          <ResponsiveContainer width="100%" height={300}>
            <RePieChart>
              <Pie
                data={modelUsageData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) =>
                  `${name} ${(percent * 100).toFixed(0)}%`
                }
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {modelUsageData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1e293b',
                  border: '1px solid #ffffff20',
                  borderRadius: '12px',
                }}
              />
            </RePieChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Cost Trends */}
        <ChartCard title="Cost Trends" icon={DollarSign}>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
              <XAxis dataKey="time" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1e293b',
                  border: '1px solid #ffffff20',
                  borderRadius: '12px',
                }}
              />
              <Line
                type="monotone"
                dataKey="cost"
                stroke="#3b82f6"
                strokeWidth={3}
                dot={{ fill: '#3b82f6', r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Agent Activity */}
        <ChartCard title="Agent Activity" icon={BarChart3}>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={agentActivityData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
              <XAxis dataKey="agent" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1e293b',
                  border: '1px solid #ffffff20',
                  borderRadius: '12px',
                }}
              />
              <Bar dataKey="tasks" fill="#a855f7" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* Real-time Activity Feed */}
      <ActivityFeed />
    </div>
  );
}

function MetricCard({
  icon: Icon,
  label,
  value,
  change,
  trend,
  color,
}: {
  icon: any;
  label: string;
  value: string;
  change: string;
  trend: 'up' | 'down';
  color: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.02 }}
      className="relative group"
    >
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl border border-white/20 p-6 hover:border-primary-500/50 transition-all duration-300">
        {/* Icon */}
        <div
          className={`w-12 h-12 rounded-xl bg-gradient-to-br ${color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}
        >
          <Icon className="w-6 h-6 text-white" />
        </div>

        {/* Content */}
        <p className="text-sm text-gray-400 mb-2">{label}</p>
        <div className="flex items-end justify-between">
          <p className="text-3xl font-bold text-white">{value}</p>
          <div className="flex items-center space-x-1">
            {trend === 'up' ? (
              <TrendingUp className="w-4 h-4 text-green-400" />
            ) : (
              <TrendingDown className="w-4 h-4 text-green-400" />
            )}
            <span className="text-sm font-semibold text-green-400">{change}</span>
          </div>
        </div>

        {/* Animated Background */}
        <div className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
          <div
            className={`absolute inset-0 rounded-2xl bg-gradient-to-r ${color} opacity-10 blur-xl`}
          />
        </div>
      </div>
    </motion.div>
  );
}

function ChartCard({
  title,
  icon: Icon,
  children,
}: {
  title: string;
  icon: any;
  children: React.ReactNode;
}) {
  return (
    <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl border border-white/20 p-6">
      <div className="flex items-center space-x-3 mb-6">
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center">
          <Icon className="w-5 h-5 text-white" />
        </div>
        <h3 className="text-lg font-bold text-white">{title}</h3>
      </div>
      {children}
    </div>
  );
}

function ActivityFeed() {
  const activities = [
    {
      type: 'success',
      message: 'Workflow "Sales Analysis" completed successfully',
      time: '2m ago',
    },
    {
      type: 'info',
      message: 'Agent Beta started data collection task',
      time: '5m ago',
    },
    {
      type: 'warning',
      message: 'High cost detected in workflow "Market Research"',
      time: '8m ago',
    },
    {
      type: 'success',
      message: 'Meta-learning discovered new optimization pattern',
      time: '12m ago',
    },
  ];

  return (
    <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl border border-white/20 p-6">
      <div className="flex items-center space-x-3 mb-6">
        <Activity className="w-6 h-6 text-primary-400" />
        <h3 className="text-xl font-bold text-white">Real-time Activity</h3>
        <div className="flex-1" />
        <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
        <span className="text-sm text-gray-400">Live</span>
      </div>

      <div className="space-y-3">
        {activities.map((activity, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.1 }}
            className="flex items-start space-x-3 p-4 bg-white/5 rounded-xl border border-white/10"
          >
            <div
              className={`w-2 h-2 rounded-full mt-2 ${
                activity.type === 'success'
                  ? 'bg-green-400'
                  : activity.type === 'warning'
                  ? 'bg-yellow-400'
                  : 'bg-blue-400'
              }`}
            />
            <div className="flex-1">
              <p className="text-sm text-white">{activity.message}</p>
              <p className="text-xs text-gray-500 mt-1">{activity.time}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
