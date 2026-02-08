'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Send, Sparkles, Loader2 } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { useWorkflowStore } from '@/store/workflowStore';

export function IntentInput() {
  const [intent, setIntent] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { submitIntent } = useWorkflowStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!intent.trim()) {
      toast.error('Please enter an intent');
      return;
    }

    setIsSubmitting(true);

    try {
      const result = await submitIntent(intent);
      
      toast.success(
        <div>
          <p className="font-semibold">Workflow Created!</p>
          <p className="text-sm">ID: {result.workflow_id}</p>
        </div>
      );

      setIntent('');
    } catch (error) {
      toast.error('Failed to submit intent');
      console.error(error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const exampleIntents = [
    'Analyze last quarter sales data and create report',
    'Research competitor products and identify gaps',
    'Generate API documentation for user module',
    'Optimize database queries for better performance',
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-4xl mx-auto"
    >
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative">
          <div className="absolute left-4 top-1/2 -translate-y-1/2">
            <Sparkles className="w-5 h-5 text-purple-400" />
          </div>
          
          <input
            type="text"
            value={intent}
            onChange={(e) => setIntent(e.target.value)}
            placeholder="What would you like AUTOOS to do? (e.g., 'Analyze sales data and create quarterly report')"
            className="w-full pl-12 pr-32 py-6 bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-lg"
            disabled={isSubmitting}
          />

          <button
            type="submit"
            disabled={isSubmitting || !intent.trim()}
            className="absolute right-2 top-1/2 -translate-y-1/2 px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl font-semibold hover:from-purple-600 hover:to-pink-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <span>Execute</span>
                <Send className="w-5 h-5" />
              </>
            )}
          </button>
        </div>
      </form>

      {/* Example Intents */}
      <div className="mt-6">
        <p className="text-sm text-gray-400 mb-3">Try these examples:</p>
        <div className="flex flex-wrap gap-2">
          {exampleIntents.map((example, i) => (
            <button
              key={i}
              onClick={() => setIntent(example)}
              className="px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm text-gray-300 hover:text-white transition-all"
            >
              {example}
            </button>
          ))}
        </div>
      </div>

      {/* Real-time Status */}
      {isSubmitting && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="mt-6 p-6 bg-purple-500/10 border border-purple-500/20 rounded-xl"
        >
          <div className="flex items-center space-x-3 mb-4">
            <Loader2 className="w-5 h-5 text-purple-400 animate-spin" />
            <span className="text-white font-semibold">Processing Intent...</span>
          </div>
          
          <div className="space-y-2 text-sm text-gray-300">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              <span>Parsing natural language intent</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse" />
              <span>Selecting optimal LLM models</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" />
              <span>Creating execution workflow</span>
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}
