import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

export interface Workflow {
  workflow_id: string;
  user_id: string;
  intent: string;
  status: 'pending' | 'running' | 'paused' | 'completed' | 'failed' | 'cancelled';
  created_at: string;
  completed_at?: string;
  cost: number;
  confidence: number;
  progress: number;
  current_step?: string;
  steps_completed: number;
  steps_total: number;
}

export interface Agent {
  agent_id: string;
  workflow_id: string;
  goal: string;
  capabilities: string[];
  trust_level: 'restricted' | 'standard' | 'elevated' | 'privileged';
  status: 'initializing' | 'ready' | 'working' | 'waiting' | 'failed' | 'retired';
  confidence_threshold: number;
  created_at: string;
  role: 'PLANNER' | 'EXECUTOR' | 'VERIFIER' | 'AUDITOR' | 'SYNTHESIZER';
}

export interface Metric {
  timestamp: string;
  workflow_success_rate: number;
  agent_utilization: number;
  llm_latency: number;
  cost_per_workflow: number;
  active_agents: number;
  total_workflows: number;
}

interface WorkflowStore {
  workflows: Workflow[];
  agents: Agent[];
  metrics: Metric[];
  isLoading: boolean;
  error: string | null;
  
  // Actions
  submitIntent: (intent: string) => Promise<{ workflow_id: string }>;
  fetchWorkflows: () => Promise<void>;
  fetchAgents: () => Promise<void>;
  fetchMetrics: () => Promise<void>;
  cancelWorkflow: (workflowId: string) => Promise<void>;
  pauseWorkflow: (workflowId: string) => Promise<void>;
  resumeWorkflow: (workflowId: string) => Promise<void>;
  clearError: () => void;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const useWorkflowStore = create<WorkflowStore>()(
  devtools(
    persist(
      (set, get) => ({
        workflows: [],
        agents: [],
        metrics: [],
        isLoading: false,
        error: null,

        submitIntent: async (intent: string) => {
          set({ isLoading: true, error: null });
          
          try {
            const response = await fetch(`${API_BASE_URL}/intents`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ intent, user_id: 'demo-user' }),
            });

            if (!response.ok) {
              throw new Error('Failed to submit intent');
            }

            const data = await response.json();
            
            // Add new workflow to state
            const newWorkflow: Workflow = {
              workflow_id: data.workflow_id,
              user_id: 'demo-user',
              intent,
              status: 'pending',
              created_at: new Date().toISOString(),
              cost: 0,
              confidence: 0,
              progress: 0,
              steps_completed: 0,
              steps_total: 0,
            };

            set((state: WorkflowStore) => ({
              workflows: [newWorkflow, ...state.workflows],
              isLoading: false,
            }));

            // Start polling for updates
            setTimeout(() => get().fetchWorkflows(), 1000);

            return { workflow_id: data.workflow_id };
          } catch (error) {
            set({ 
              error: error instanceof Error ? error.message : 'Unknown error',
              isLoading: false 
            });
            throw error;
          }
        },

        fetchWorkflows: async () => {
          try {
            const response = await fetch(`${API_BASE_URL}/workflows`);
            
            if (!response.ok) {
              throw new Error('Failed to fetch workflows');
            }

            const data = await response.json();
            set({ workflows: data.workflows || [] });
          } catch (error) {
            console.error('Error fetching workflows:', error);
            // Don't set error state for background fetches
          }
        },

        fetchAgents: async () => {
          try {
            const response = await fetch(`${API_BASE_URL}/agents`);
            
            if (!response.ok) {
              throw new Error('Failed to fetch agents');
            }

            const data = await response.json();
            set({ agents: data.agents || [] });
          } catch (error) {
            console.error('Error fetching agents:', error);
          }
        },

        fetchMetrics: async () => {
          try {
            const response = await fetch(`${API_BASE_URL}/metrics`);
            
            if (!response.ok) {
              throw new Error('Failed to fetch metrics');
            }

            const data = await response.json();
            set({ metrics: data.metrics || [] });
          } catch (error) {
            console.error('Error fetching metrics:', error);
          }
        },

        cancelWorkflow: async (workflowId: string) => {
          set({ isLoading: true, error: null });
          
          try {
            const response = await fetch(`${API_BASE_URL}/workflows/${workflowId}`, {
              method: 'DELETE',
            });

            if (!response.ok) {
              throw new Error('Failed to cancel workflow');
            }

            set((state: WorkflowStore) => ({
              workflows: state.workflows.map((w: Workflow) =>
                w.workflow_id === workflowId ? { ...w, status: 'cancelled' as const } : w
              ),
              isLoading: false,
            }));
          } catch (error) {
            set({ 
              error: error instanceof Error ? error.message : 'Unknown error',
              isLoading: false 
            });
            throw error;
          }
        },

        pauseWorkflow: async (workflowId: string) => {
          set({ isLoading: true, error: null });
          
          try {
            const response = await fetch(`${API_BASE_URL}/workflows/${workflowId}/pause`, {
              method: 'POST',
            });

            if (!response.ok) {
              throw new Error('Failed to pause workflow');
            }

            set((state: WorkflowStore) => ({
              workflows: state.workflows.map((w: Workflow) =>
                w.workflow_id === workflowId ? { ...w, status: 'paused' as const } : w
              ),
              isLoading: false,
            }));
          } catch (error) {
            set({ 
              error: error instanceof Error ? error.message : 'Unknown error',
              isLoading: false 
            });
            throw error;
          }
        },

        resumeWorkflow: async (workflowId: string) => {
          set({ isLoading: true, error: null });
          
          try {
            const response = await fetch(`${API_BASE_URL}/workflows/${workflowId}/resume`, {
              method: 'POST',
            });

            if (!response.ok) {
              throw new Error('Failed to resume workflow');
            }

            set((state: WorkflowStore) => ({
              workflows: state.workflows.map((w: Workflow) =>
                w.workflow_id === workflowId ? { ...w, status: 'running' as const } : w
              ),
              isLoading: false,
            }));
          } catch (error) {
            set({ 
              error: error instanceof Error ? error.message : 'Unknown error',
              isLoading: false 
            });
            throw error;
          }
        },

        clearError: () => set({ error: null }),
      }),
      {
        name: 'autoos-workflow-store',
        partialize: (state: WorkflowStore) => ({ workflows: state.workflows }),
      }
    )
  )
);

