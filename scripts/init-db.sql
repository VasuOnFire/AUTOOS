-- AUTOOS Database Initialization Script

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Workflows table
CREATE TABLE IF NOT EXISTS workflows (
    workflow_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    intent TEXT NOT NULL,
    goal_graph JSONB,
    workflow_definition JSONB,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    cost DECIMAL(10,4) DEFAULT 0.0,
    confidence DECIMAL(3,2),
    INDEX idx_workflows_user_id (user_id),
    INDEX idx_workflows_status (status),
    INDEX idx_workflows_created_at (created_at)
);

-- Agents table
CREATE TABLE IF NOT EXISTS agents (
    agent_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id UUID REFERENCES workflows(workflow_id) ON DELETE CASCADE,
    goal TEXT NOT NULL,
    capabilities JSONB NOT NULL,
    trust_level VARCHAR(50) NOT NULL,
    confidence_threshold DECIMAL(3,2) NOT NULL DEFAULT 0.75,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    retired_at TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'initializing',
    INDEX idx_agents_workflow_id (workflow_id),
    INDEX idx_agents_status (status)
);

-- LLM Providers table
CREATE TABLE IF NOT EXISTS llm_providers (
    provider_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider_name VARCHAR(100) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    cost_per_token DECIMAL(10,8) NOT NULL,
    avg_latency DECIMAL(8,2) DEFAULT 0.0,
    reliability_score DECIMAL(3,2) DEFAULT 1.0,
    capabilities JSONB,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(provider_name, model_name),
    INDEX idx_llm_providers_name (provider_name, model_name)
);

-- Audit Log table (append-only)
CREATE TABLE IF NOT EXISTS audit_log (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id UUID REFERENCES workflows(workflow_id) ON DELETE CASCADE,
    agent_id UUID REFERENCES agents(agent_id) ON DELETE SET NULL,
    event_type VARCHAR(100) NOT NULL,
    reasoning TEXT,
    decision JSONB,
    confidence DECIMAL(3,2),
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    signature VARCHAR(255),
    INDEX idx_audit_log_workflow_id (workflow_id),
    INDEX idx_audit_log_timestamp (timestamp),
    INDEX idx_audit_log_event_type (event_type)
);

-- Failures table
CREATE TABLE IF NOT EXISTS failures (
    failure_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id UUID REFERENCES workflows(workflow_id) ON DELETE CASCADE,
    agent_id UUID REFERENCES agents(agent_id) ON DELETE SET NULL,
    step_id VARCHAR(255),
    failure_type VARCHAR(100) NOT NULL,
    error_message TEXT,
    context JSONB,
    recovery_action VARCHAR(100),
    recovery_success BOOLEAN,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_failures_workflow_id (workflow_id),
    INDEX idx_failures_timestamp (timestamp),
    INDEX idx_failures_type (failure_type)
);

-- Policies table
CREATE TABLE IF NOT EXISTS policies (
    policy_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    policy_name VARCHAR(255) NOT NULL UNIQUE,
    policy_type VARCHAR(100) NOT NULL,
    rules JSONB NOT NULL,
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_policies_active (active),
    INDEX idx_policies_type (policy_type)
);

-- Insert default LLM providers
INSERT INTO llm_providers (provider_name, model_name, cost_per_token, capabilities) VALUES
    ('openai', 'gpt-4', 0.00003, '["reasoning", "planning", "analysis"]'::jsonb),
    ('openai', 'gpt-3.5-turbo', 0.000002, '["execution", "fast_tasks"]'::jsonb),
    ('anthropic', 'claude-3-opus-20240229', 0.000015, '["reasoning", "verification", "synthesis"]'::jsonb),
    ('anthropic', 'claude-3-sonnet-20240229', 0.000003, '["execution", "analysis"]'::jsonb),
    ('anthropic', 'claude-3-haiku-20240307', 0.00000025, '["fast_tasks", "execution"]'::jsonb)
ON CONFLICT (provider_name, model_name) DO NOTHING;

-- Insert default policies
INSERT INTO policies (policy_name, policy_type, rules) VALUES
    ('default_trust_levels', 'access_control', '{
        "restricted": ["read_file", "list_directory"],
        "standard": ["read_file", "list_directory", "write_file", "http_request"],
        "elevated": ["read_file", "list_directory", "write_file", "http_request", "execute_command"],
        "privileged": ["all"]
    }'::jsonb),
    ('high_risk_approval', 'approval', '{
        "requires_approval": ["delete_database", "modify_production", "financial_transaction"],
        "approval_level": "human"
    }'::jsonb),
    ('rate_limits', 'rate_limit', '{
        "llm_calls_per_minute": 100,
        "tool_executions_per_minute": 50,
        "cost_per_workflow_usd": 10.0
    }'::jsonb)
ON CONFLICT (policy_name) DO NOTHING;

-- ============================================================================
-- Authentication and Payment Tables
-- ============================================================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'student',
    subscription_tier VARCHAR(50) NOT NULL DEFAULT 'free_trial',
    is_email_verified BOOLEAN DEFAULT FALSE,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(255),
    biometric_enabled BOOLEAN DEFAULT FALSE,
    trial_start_date TIMESTAMP,
    trial_end_date TIMESTAMP,
    credits_remaining INTEGER DEFAULT 10,
    is_trial_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    INDEX idx_users_email (email),
    INDEX idx_users_username (username),
    INDEX idx_users_trial_active (is_trial_active)
);

-- Subscriptions table
CREATE TABLE IF NOT EXISTS subscriptions (
    subscription_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    tier VARCHAR(50) NOT NULL DEFAULT 'free_trial',
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    subscription_start_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    subscription_end_date TIMESTAMP,
    payment_method VARCHAR(100),
    billing_cycle VARCHAR(20) DEFAULT 'monthly',
    auto_renew BOOLEAN DEFAULT TRUE,
    stripe_subscription_id VARCHAR(255),
    workflows_limit INTEGER DEFAULT 10,
    agents_limit INTEGER DEFAULT 2,
    workflows_used INTEGER DEFAULT 0,
    INDEX idx_subscriptions_user (user_id),
    INDEX idx_subscriptions_status (status)
);

-- Payments table
CREATE TABLE IF NOT EXISTS payments (
    payment_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    subscription_id VARCHAR(36) REFERENCES subscriptions(subscription_id) ON DELETE SET NULL,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    payment_method VARCHAR(100) NOT NULL,
    payment_type VARCHAR(50) NOT NULL DEFAULT 'card',
    stripe_payment_id VARCHAR(255),
    qr_code_payment_id VARCHAR(255),
    qr_code_data TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    INDEX idx_payments_user (user_id),
    INDEX idx_payments_status (status),
    INDEX idx_payments_created (created_at)
);

-- OAuth Connections table
CREATE TABLE IF NOT EXISTS oauth_connections (
    connection_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL,
    provider_user_id VARCHAR(255) NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    token_expires_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_oauth_user (user_id),
    INDEX idx_oauth_provider (provider, provider_user_id)
);

-- Update workflows table to include user_id foreign key
ALTER TABLE workflows ADD COLUMN IF NOT EXISTS user_id_fk VARCHAR(36) REFERENCES users(user_id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS idx_workflows_user_id_fk ON workflows(user_id_fk);

-- Access Codes table
CREATE TABLE IF NOT EXISTS access_codes (
    code_id VARCHAR(36) PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    user_id VARCHAR(36) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    subscription_tier VARCHAR(50) NOT NULL,
    payment_id VARCHAR(36) NOT NULL REFERENCES payments(payment_id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP,
    revoked_at TIMESTAMP,
    revocation_reason TEXT,
    INDEX idx_access_codes_code (code),
    INDEX idx_access_codes_user (user_id),
    INDEX idx_access_codes_status (status),
    INDEX idx_access_codes_expires (expires_at)
);


