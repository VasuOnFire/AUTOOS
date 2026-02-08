"""
Core data models and enums for AUTOOS

Defines all domain models used across the system.
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime
import json
import uuid


# ============================================================================
# Enums
# ============================================================================


class RiskLevel(str, Enum):
    """Risk classification for intents"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TrustLevel(str, Enum):
    """Security classification for agents"""

    RESTRICTED = "restricted"
    STANDARD = "standard"
    ELEVATED = "elevated"
    PRIVILEGED = "privileged"


class WorkflowState(str, Enum):
    """Workflow execution states"""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentStatus(str, Enum):
    """Agent lifecycle states"""

    INITIALIZING = "initializing"
    READY = "ready"
    WORKING = "working"
    WAITING = "waiting"
    FAILED = "failed"
    RETIRED = "retired"


class LLMRole(str, Enum):
    """Specialized LLM roles"""

    PLANNER = "planner"  # Deep reasoning for planning
    EXECUTOR = "executor"  # Fast, cheap execution
    VERIFIER = "verifier"  # Cross-check and critique
    AUDITOR = "auditor"  # Post-hoc analysis
    SYNTHESIZER = "synthesizer"  # Final output generation


class FailureType(str, Enum):
    """Types of failures"""

    TRANSIENT = "transient"
    MODEL_ERROR = "model_error"
    TOOL_ERROR = "tool_error"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    POLICY_VIOLATION = "policy_violation"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


class UserRole(str, Enum):
    """User roles"""

    STUDENT = "student"
    EMPLOYEE = "employee"
    PROFESSIONAL = "professional"
    ADMIN = "admin"


class SubscriptionTier(str, Enum):
    """Subscription tiers"""

    FREE_TRIAL = "free_trial"
    STUDENT = "student"
    EMPLOYEE = "employee"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    """Subscription status"""

    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PAST_DUE = "past_due"


class PaymentStatus(str, Enum):
    """Payment status"""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentType(str, Enum):
    """Payment type"""

    CARD = "card"
    UPI = "upi"
    QR_CODE = "qr_code"


# ============================================================================
# Intent Plane Models
# ============================================================================


@dataclass
class ParsedIntent:
    """Parsed and validated intent"""

    intent_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    raw_text: str = ""
    entities: Dict[str, Any] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    risk_level: RiskLevel = RiskLevel.LOW
    ambiguities: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["risk_level"] = self.risk_level.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ParsedIntent":
        """Create from dictionary"""
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        data["risk_level"] = RiskLevel(data["risk_level"])
        return cls(**data)


@dataclass
class GoalNode:
    """Single goal in goal graph"""

    goal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    required_capabilities: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    success_criteria: Dict[str, Any] = field(default_factory=dict)
    estimated_cost: float = 0.0
    estimated_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GoalNode":
        """Create from dictionary"""
        return cls(**data)


@dataclass
class GoalGraph:
    """Directed acyclic graph of goals"""

    graph_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    root_goal: str = ""
    nodes: Dict[str, GoalNode] = field(default_factory=dict)
    edges: List[tuple[str, str]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "graph_id": self.graph_id,
            "root_goal": self.root_goal,
            "nodes": {k: v.to_dict() for k, v in self.nodes.items()},
            "edges": self.edges,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        """Serialize to JSON"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GoalGraph":
        """Create from dictionary"""
        nodes = {k: GoalNode.from_dict(v) for k, v in data["nodes"].items()}
        return cls(
            graph_id=data["graph_id"],
            root_goal=data["root_goal"],
            nodes=nodes,
            edges=[tuple(e) for e in data["edges"]],
            metadata=data["metadata"],
        )

    @classmethod
    def from_json(cls, json_str: str) -> "GoalGraph":
        """Deserialize from JSON"""
        return cls.from_dict(json.loads(json_str))


# ============================================================================
# Orchestration Plane Models
# ============================================================================


@dataclass
class RetryConfig:
    """Retry configuration"""

    max_attempts: int = 3
    backoff_multiplier: float = 2.0
    initial_delay_seconds: float = 1.0
    max_delay_seconds: float = 60.0


@dataclass
class FallbackStrategy:
    """Fallback strategy for failures"""

    strategy_type: str = "agent_swap"  # agent_swap, llm_swap, workflow_mutation
    trigger_condition: str = ""
    alternative_approach: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowStep:
    """Single step in workflow"""

    step_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    goal_id: str = ""
    required_capabilities: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    retry_config: RetryConfig = field(default_factory=RetryConfig)
    fallback_strategy: FallbackStrategy = field(default_factory=FallbackStrategy)
    checkpoint: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class Workflow:
    """Executable workflow"""

    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    steps: Dict[str, WorkflowStep] = field(default_factory=dict)
    execution_order: List[List[str]] = field(default_factory=list)
    state: WorkflowState = WorkflowState.PENDING
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "workflow_id": self.workflow_id,
            "steps": {k: v.to_dict() for k, v in self.steps.items()},
            "execution_order": self.execution_order,
            "state": self.state.value,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        """Serialize to JSON"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> "Workflow":
        """Deserialize from JSON"""
        data = json.loads(json_str)
        steps = {k: WorkflowStep(**v) for k, v in data["steps"].items()}
        return cls(
            workflow_id=data["workflow_id"],
            steps=steps,
            execution_order=data["execution_order"],
            state=WorkflowState(data["state"]),
            metadata=data["metadata"],
        )


@dataclass
class FailureRecord:
    """Record of a failure"""

    failure_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    failure_type: FailureType = FailureType.UNKNOWN
    error_message: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    recovery_action: str = ""
    recovery_success: bool = False


@dataclass
class Agent:
    """Autonomous agent"""

    agent_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    goal: str = ""
    capabilities: List[str] = field(default_factory=list)
    allowed_tools: List[str] = field(default_factory=list)
    preferred_llm_roles: Dict[str, str] = field(default_factory=dict)
    trust_level: TrustLevel = TrustLevel.STANDARD
    memory_scope: str = "workflow"
    confidence_threshold: float = 0.75
    failure_history: List[FailureRecord] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: AgentStatus = AgentStatus.INITIALIZING

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["trust_level"] = self.trust_level.value
        data["status"] = self.status.value
        data["created_at"] = self.created_at.isoformat()
        return data

    def to_json(self) -> str:
        """Serialize to JSON"""
        return json.dumps(self.to_dict())


# ============================================================================
# Execution Plane Models
# ============================================================================


@dataclass
class LLMProvider:
    """LLM provider configuration"""

    provider_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    provider_name: str = ""  # openai, anthropic, google
    model_name: str = ""
    api_endpoint: str = ""
    cost_per_token: float = 0.0
    avg_latency: float = 0.0
    reliability_score: float = 1.0
    capabilities: List[str] = field(default_factory=list)


@dataclass
class LLMResponse:
    """Response from LLM"""

    provider: LLMProvider
    role: LLMRole
    prompt: str
    response: str
    confidence: float
    tokens_used: int
    latency: float
    cost: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Tool:
    """Tool definition"""

    tool_name: str
    description: str
    parameters_schema: Dict[str, Any]
    required_trust_level: TrustLevel
    timeout_seconds: int = 60
    rate_limit: int = 100


@dataclass
class ToolResult:
    """Result of tool execution"""

    success: bool
    output: Any
    error: Optional[str] = None
    execution_time: float = 0.0
    cost: float = 0.0


@dataclass
class TaskResult:
    """Result of agent task execution"""

    success: bool
    output: Any
    confidence: float
    reasoning: str
    cost: float
    latency: float
    errors: List[str] = field(default_factory=list)


@dataclass
class WorkflowResult:
    """Final workflow execution result"""

    workflow_id: str
    success: bool
    final_output: Any
    total_cost: float
    total_time: float
    avg_confidence: float
    steps_completed: int
    steps_failed: int
    audit_trail_id: str


# ============================================================================
# Memory Plane Models
# ============================================================================


@dataclass
class Lesson:
    """Learned lesson from execution"""

    lesson_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    pattern: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    outcome: str = ""
    success: bool = True
    confidence: float = 1.0
    learned_at: datetime = field(default_factory=datetime.utcnow)


# ============================================================================
# Governance Plane Models
# ============================================================================


@dataclass
class Policy:
    """Policy definition"""

    policy_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    policy_name: str = ""
    policy_type: str = ""  # access_control, approval, rate_limit
    rules: Dict[str, Any] = field(default_factory=dict)
    active: bool = True


@dataclass
class PolicyDecision:
    """Policy evaluation result"""

    allowed: bool
    reason: str
    requires_approval: bool = False
    approval_level: Optional[str] = None


# ============================================================================
# Verification Models
# ============================================================================


@dataclass
class VerificationResult:
    """Result of cross-verification"""

    consensus: bool
    selected_response: Optional[LLMResponse]
    discrepancies: List[str] = field(default_factory=list)
    confidence: float = 0.0


# ============================================================================
# Authentication and Payment Models
# ============================================================================


@dataclass
class User:
    """User account"""

    user_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    email: str = ""
    username: str = ""
    full_name: str = ""
    password_hash: str = ""
    role: UserRole = UserRole.STUDENT
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE_TRIAL
    is_email_verified: bool = False
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    biometric_enabled: bool = False
    trial_start_date: Optional[datetime] = None
    trial_end_date: Optional[datetime] = None
    credits_remaining: int = 10
    is_trial_active: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["role"] = self.role.value
        data["subscription_tier"] = self.subscription_tier.value
        data["created_at"] = self.created_at.isoformat()
        if self.last_login:
            data["last_login"] = self.last_login.isoformat()
        if self.trial_start_date:
            data["trial_start_date"] = self.trial_start_date.isoformat()
        if self.trial_end_date:
            data["trial_end_date"] = self.trial_end_date.isoformat()
        return data


@dataclass
class Subscription:
    """User subscription"""

    subscription_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    tier: SubscriptionTier = SubscriptionTier.FREE_TRIAL
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    subscription_start_date: datetime = field(default_factory=datetime.utcnow)
    subscription_end_date: Optional[datetime] = None
    payment_method: Optional[str] = None
    billing_cycle: str = "monthly"  # monthly, annual
    auto_renew: bool = True
    stripe_subscription_id: Optional[str] = None
    workflows_limit: int = 10
    agents_limit: int = 2
    workflows_used: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["tier"] = self.tier.value
        data["status"] = self.status.value
        data["subscription_start_date"] = self.subscription_start_date.isoformat()
        if self.subscription_end_date:
            data["subscription_end_date"] = self.subscription_end_date.isoformat()
        return data


@dataclass
class Payment:
    """Payment transaction"""

    payment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    subscription_id: Optional[str] = None
    amount: float = 0.0
    currency: str = "USD"
    status: PaymentStatus = PaymentStatus.PENDING
    payment_method: str = ""
    payment_type: PaymentType = PaymentType.CARD
    stripe_payment_id: Optional[str] = None
    qr_code_payment_id: Optional[str] = None
    qr_code_data: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["status"] = self.status.value
        data["payment_type"] = self.payment_type.value
        data["created_at"] = self.created_at.isoformat()
        if self.completed_at:
            data["completed_at"] = self.completed_at.isoformat()
        return data


@dataclass
class OAuthConnection:
    """OAuth provider connection"""

    connection_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    provider: str = ""  # google, github, microsoft, apple, linkedin
    provider_user_id: str = ""
    access_token: str = ""  # Should be encrypted
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        if self.token_expires_at:
            data["token_expires_at"] = self.token_expires_at.isoformat()
        return data


@dataclass
class PricingTier:
    """Pricing tier configuration"""

    tier: SubscriptionTier
    name: str
    price_monthly: float
    price_annual: float
    workflows_limit: int
    agents_limit: int
    features: List[str] = field(default_factory=list)
    is_trial: bool = False
    trial_days: int = 0
    trial_credits: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["tier"] = self.tier.value
        return data
