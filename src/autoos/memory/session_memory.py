"""
Session Memory - PostgreSQL-based persistent storage

Stores workflow definitions, agent configurations, audit logs, and policies.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy import create_engine, Column, String, DateTime, JSON, Boolean, Float, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID
import uuid

from autoos.infrastructure.logging import get_logger
from autoos.infrastructure.metrics import get_metrics_collector

logger = get_logger(__name__)
metrics = get_metrics_collector()

Base = declarative_base()


# ============================================================================
# ORM Models
# ============================================================================


class WorkflowModel(Base):
    """Workflow ORM model"""

    __tablename__ = "workflows"

    workflow_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False, index=True)
    intent = Column(String, nullable=False)
    goal_graph = Column(JSON)
    workflow_definition = Column(JSON)
    status = Column(String(50), nullable=False, default="pending", index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime)
    cost = Column(Float, default=0.0)
    confidence = Column(Float)


class AgentModel(Base):
    """Agent ORM model"""

    __tablename__ = "agents"

    agent_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), index=True)
    goal = Column(String, nullable=False)
    capabilities = Column(JSON, nullable=False)
    trust_level = Column(String(50), nullable=False)
    confidence_threshold = Column(Float, nullable=False, default=0.75)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    retired_at = Column(DateTime)
    status = Column(String(50), nullable=False, default="initializing", index=True)


class LLMProviderModel(Base):
    """LLM Provider ORM model"""

    __tablename__ = "llm_providers"

    provider_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_name = Column(String(100), nullable=False, index=True)
    model_name = Column(String(100), nullable=False, index=True)
    cost_per_token = Column(Float, nullable=False)
    avg_latency = Column(Float, default=0.0)
    reliability_score = Column(Float, default=1.0)
    capabilities = Column(JSON)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class AuditLogModel(Base):
    """Audit Log ORM model (append-only)"""

    __tablename__ = "audit_log"

    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), index=True)
    agent_id = Column(UUID(as_uuid=True))
    event_type = Column(String(100), nullable=False, index=True)
    reasoning = Column(String)
    decision = Column(JSON)
    confidence = Column(Float)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    signature = Column(String(255))


class FailureModel(Base):
    """Failure ORM model"""

    __tablename__ = "failures"

    failure_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), index=True)
    agent_id = Column(UUID(as_uuid=True))
    step_id = Column(String(255))
    failure_type = Column(String(100), nullable=False, index=True)
    error_message = Column(String)
    context = Column(JSON)
    recovery_action = Column(String(100))
    recovery_success = Column(Boolean)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)


class PolicyModel(Base):
    """Policy ORM model"""

    __tablename__ = "policies"

    policy_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_name = Column(String(255), nullable=False, unique=True)
    policy_type = Column(String(100), nullable=False, index=True)
    rules = Column(JSON, nullable=False)
    active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class UserModel(Base):
    """User ORM model"""

    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, unique=True, index=True)
    username = Column(String(255), nullable=False, unique=True, index=True)
    full_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="student")
    subscription_tier = Column(String(50), nullable=False, default="free_trial")
    is_email_verified = Column(Boolean, nullable=False, default=False)
    mfa_enabled = Column(Boolean, nullable=False, default=False)
    mfa_secret = Column(String(255))
    biometric_enabled = Column(Boolean, nullable=False, default=False)
    trial_start_date = Column(DateTime)
    trial_end_date = Column(DateTime)
    credits_remaining = Column(Integer, default=10)
    is_trial_active = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    last_login = Column(DateTime)


class SubscriptionModel(Base):
    """Subscription ORM model"""

    __tablename__ = "subscriptions"

    subscription_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    tier = Column(String(50), nullable=False, default="free_trial")
    status = Column(String(50), nullable=False, default="active", index=True)
    subscription_start_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    subscription_end_date = Column(DateTime)
    payment_method = Column(String(50))
    billing_cycle = Column(String(20), default="monthly")
    auto_renew = Column(Boolean, default=True)
    stripe_subscription_id = Column(String(255), index=True)
    workflows_limit = Column(Integer, default=10)
    agents_limit = Column(Integer, default=2)
    workflows_used = Column(Integer, default=0)


class PaymentModel(Base):
    """Payment ORM model"""

    __tablename__ = "payments"

    payment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    subscription_id = Column(UUID(as_uuid=True), index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False, default="USD")
    status = Column(String(50), nullable=False, default="pending", index=True)
    payment_method = Column(String(50), nullable=False)
    payment_type = Column(String(50), nullable=False, default="card")
    stripe_payment_id = Column(String(255), index=True)
    qr_code_payment_id = Column(String(255), index=True)
    qr_code_data = Column(String)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime)


class InvoiceModel(Base):
    """Invoice ORM model"""

    __tablename__ = "invoices"

    invoice_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    subscription_id = Column(UUID(as_uuid=True), index=True)
    payment_id = Column(UUID(as_uuid=True), index=True)
    invoice_number = Column(String(100), nullable=False, unique=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False, default="USD")
    status = Column(String(50), nullable=False, default="pending", index=True)
    invoice_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=False)
    paid_date = Column(DateTime)
    stripe_invoice_id = Column(String(255), index=True)
    pdf_url = Column(String)


class OAuthConnectionModel(Base):
    """OAuth Connection ORM model"""

    __tablename__ = "oauth_connections"

    connection_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    provider = Column(String(50), nullable=False, index=True)
    provider_user_id = Column(String(255), nullable=False)
    access_token = Column(String)  # Should be encrypted
    refresh_token = Column(String)
    token_expires_at = Column(DateTime)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


# ============================================================================
# Session Memory Class
# ============================================================================


class SessionMemory:
    """
    PostgreSQL-based session memory

    Features:
    - Persistent workflow and agent storage
    - Immutable audit logs
    - Policy management
    - Failure tracking
    """

    def __init__(self, database_url: str):
        """
        Initialize session memory

        Args:
            database_url: PostgreSQL connection URL
        """
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(bind=self.engine)

        logger.info(f"Connected to PostgreSQL session memory")

    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()

    # ========================================================================
    # Workflow Operations
    # ========================================================================

    def create_workflow(
        self, user_id: str, intent: str, goal_graph: Dict[str, Any]
    ) -> str:
        """
        Create new workflow

        Args:
            user_id: User ID
            intent: Natural language intent
            goal_graph: Goal graph dictionary

        Returns:
            Workflow ID
        """
        session = self.get_session()
        try:
            workflow = WorkflowModel(
                user_id=user_id, intent=intent, goal_graph=goal_graph
            )
            session.add(workflow)
            session.commit()

            workflow_id = str(workflow.workflow_id)
            metrics.record_memory_operation("session", "write")
            logger.info(f"Created workflow", workflow_id=workflow_id)

            return workflow_id

        finally:
            session.close()

    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get workflow by ID

        Args:
            workflow_id: Workflow ID

        Returns:
            Workflow dictionary or None
        """
        session = self.get_session()
        try:
            workflow = (
                session.query(WorkflowModel)
                .filter(WorkflowModel.workflow_id == uuid.UUID(workflow_id))
                .first()
            )

            metrics.record_memory_operation("session", "read")

            if workflow:
                return {
                    "workflow_id": str(workflow.workflow_id),
                    "user_id": workflow.user_id,
                    "intent": workflow.intent,
                    "goal_graph": workflow.goal_graph,
                    "workflow_definition": workflow.workflow_definition,
                    "status": workflow.status,
                    "created_at": workflow.created_at.isoformat(),
                    "completed_at": (
                        workflow.completed_at.isoformat() if workflow.completed_at else None
                    ),
                    "cost": workflow.cost,
                    "confidence": workflow.confidence,
                }
            return None

        finally:
            session.close()

    def update_workflow_status(
        self, workflow_id: str, status: str, **kwargs: Any
    ) -> None:
        """
        Update workflow status and optional fields

        Args:
            workflow_id: Workflow ID
            status: New status
            **kwargs: Additional fields to update
        """
        session = self.get_session()
        try:
            workflow = (
                session.query(WorkflowModel)
                .filter(WorkflowModel.workflow_id == uuid.UUID(workflow_id))
                .first()
            )

            if workflow:
                workflow.status = status
                for key, value in kwargs.items():
                    if hasattr(workflow, key):
                        setattr(workflow, key, value)

                session.commit()
                metrics.record_memory_operation("session", "write")
                logger.debug(f"Updated workflow status", workflow_id=workflow_id, status=status)

        finally:
            session.close()

    # ========================================================================
    # Audit Log Operations (Append-Only)
    # ========================================================================

    def append_audit_log(
        self,
        workflow_id: str,
        event_type: str,
        reasoning: str,
        decision: Dict[str, Any],
        confidence: float,
        agent_id: Optional[str] = None,
    ) -> str:
        """
        Append to audit log (immutable)

        Args:
            workflow_id: Workflow ID
            event_type: Type of event
            reasoning: Decision reasoning
            decision: Decision data
            confidence: Confidence score
            agent_id: Agent ID (optional)

        Returns:
            Log ID
        """
        session = self.get_session()
        try:
            log_entry = AuditLogModel(
                workflow_id=uuid.UUID(workflow_id),
                agent_id=uuid.UUID(agent_id) if agent_id else None,
                event_type=event_type,
                reasoning=reasoning,
                decision=decision,
                confidence=confidence,
            )
            session.add(log_entry)
            session.commit()

            log_id = str(log_entry.log_id)
            metrics.record_memory_operation("audit", "write")

            return log_id

        finally:
            session.close()

    def get_audit_trail(self, workflow_id: str) -> List[Dict[str, Any]]:
        """
        Get complete audit trail for workflow

        Args:
            workflow_id: Workflow ID

        Returns:
            List of audit log entries
        """
        session = self.get_session()
        try:
            logs = (
                session.query(AuditLogModel)
                .filter(AuditLogModel.workflow_id == uuid.UUID(workflow_id))
                .order_by(AuditLogModel.timestamp)
                .all()
            )

            metrics.record_memory_operation("audit", "read")

            return [
                {
                    "log_id": str(log.log_id),
                    "event_type": log.event_type,
                    "reasoning": log.reasoning,
                    "decision": log.decision,
                    "confidence": log.confidence,
                    "timestamp": log.timestamp.isoformat(),
                    "agent_id": str(log.agent_id) if log.agent_id else None,
                }
                for log in logs
            ]

        finally:
            session.close()

    # ========================================================================
    # Policy Operations
    # ========================================================================

    def get_policy(self, policy_name: str) -> Optional[Dict[str, Any]]:
        """
        Get policy by name

        Args:
            policy_name: Policy name

        Returns:
            Policy dictionary or None
        """
        session = self.get_session()
        try:
            policy = (
                session.query(PolicyModel)
                .filter(PolicyModel.policy_name == policy_name, PolicyModel.active == True)
                .first()
            )

            metrics.record_memory_operation("session", "read")

            if policy:
                return {
                    "policy_id": str(policy.policy_id),
                    "policy_name": policy.policy_name,
                    "policy_type": policy.policy_type,
                    "rules": policy.rules,
                    "active": policy.active,
                }
            return None

        finally:
            session.close()

    # ========================================================================
    # Payment Operations
    # ========================================================================

    def create_payment(
        self,
        user_id: str,
        amount: float,
        currency: str,
        payment_method: str,
        payment_type: str,
        subscription_id: Optional[str] = None,
        stripe_payment_id: Optional[str] = None,
        qr_code_payment_id: Optional[str] = None,
    ) -> str:
        """
        Create new payment record

        Args:
            user_id: User ID
            amount: Payment amount
            currency: Currency code
            payment_method: Payment method
            payment_type: Payment type (card, upi, qr_code)
            subscription_id: Subscription ID (optional)
            stripe_payment_id: Stripe payment ID (optional)
            qr_code_payment_id: QR code payment ID (optional)

        Returns:
            Payment ID
        """
        session = self.get_session()
        try:
            payment = PaymentModel(
                user_id=uuid.UUID(user_id),
                subscription_id=uuid.UUID(subscription_id) if subscription_id else None,
                amount=amount,
                currency=currency,
                payment_method=payment_method,
                payment_type=payment_type,
                stripe_payment_id=stripe_payment_id,
                qr_code_payment_id=qr_code_payment_id,
            )
            session.add(payment)
            session.commit()

            payment_id = str(payment.payment_id)
            metrics.record_memory_operation("session", "write")
            logger.info(f"Created payment", payment_id=payment_id)

            return payment_id

        finally:
            session.close()

    def get_payment_history(
        self, user_id: str, limit: int = 10, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get payment history for user

        Args:
            user_id: User ID
            limit: Number of records to return
            offset: Offset for pagination

        Returns:
            List of payment records
        """
        session = self.get_session()
        try:
            payments = (
                session.query(PaymentModel)
                .filter(PaymentModel.user_id == uuid.UUID(user_id))
                .order_by(PaymentModel.created_at.desc())
                .limit(limit)
                .offset(offset)
                .all()
            )

            metrics.record_memory_operation("session", "read")

            return [
                {
                    "payment_id": str(payment.payment_id),
                    "amount": payment.amount,
                    "currency": payment.currency,
                    "status": payment.status,
                    "payment_method": payment.payment_method,
                    "payment_type": payment.payment_type,
                    "created_at": payment.created_at.isoformat(),
                    "completed_at": (
                        payment.completed_at.isoformat() if payment.completed_at else None
                    ),
                }
                for payment in payments
            ]

        finally:
            session.close()

    def update_payment_status(
        self, payment_id: str, status: str, completed_at: Optional[datetime] = None
    ) -> None:
        """
        Update payment status

        Args:
            payment_id: Payment ID
            status: New status
            completed_at: Completion timestamp (optional)
        """
        session = self.get_session()
        try:
            payment = (
                session.query(PaymentModel)
                .filter(PaymentModel.payment_id == uuid.UUID(payment_id))
                .first()
            )

            if payment:
                payment.status = status
                if completed_at:
                    payment.completed_at = completed_at

                session.commit()
                metrics.record_memory_operation("session", "write")
                logger.debug(f"Updated payment status", payment_id=payment_id, status=status)

        finally:
            session.close()

    # ========================================================================
    # Subscription Operations
    # ========================================================================

    def create_subscription(
        self,
        user_id: str,
        tier: str,
        billing_cycle: str = "monthly",
        stripe_subscription_id: Optional[str] = None,
    ) -> str:
        """
        Create new subscription

        Args:
            user_id: User ID
            tier: Subscription tier
            billing_cycle: Billing cycle (monthly or annual)
            stripe_subscription_id: Stripe subscription ID (optional)

        Returns:
            Subscription ID
        """
        session = self.get_session()
        try:
            subscription = SubscriptionModel(
                user_id=uuid.UUID(user_id),
                tier=tier,
                billing_cycle=billing_cycle,
                stripe_subscription_id=stripe_subscription_id,
            )
            session.add(subscription)
            session.commit()

            subscription_id = str(subscription.subscription_id)
            metrics.record_memory_operation("session", "write")
            logger.info(f"Created subscription", subscription_id=subscription_id)

            return subscription_id

        finally:
            session.close()

    def get_user_subscription(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get active subscription for user

        Args:
            user_id: User ID

        Returns:
            Subscription dictionary or None
        """
        session = self.get_session()
        try:
            subscription = (
                session.query(SubscriptionModel)
                .filter(
                    SubscriptionModel.user_id == uuid.UUID(user_id),
                    SubscriptionModel.status == "active",
                )
                .first()
            )

            metrics.record_memory_operation("session", "read")

            if subscription:
                return {
                    "subscription_id": str(subscription.subscription_id),
                    "tier": subscription.tier,
                    "status": subscription.status,
                    "billing_cycle": subscription.billing_cycle,
                    "workflows_limit": subscription.workflows_limit,
                    "agents_limit": subscription.agents_limit,
                    "workflows_used": subscription.workflows_used,
                    "subscription_start_date": subscription.subscription_start_date.isoformat(),
                    "subscription_end_date": (
                        subscription.subscription_end_date.isoformat()
                        if subscription.subscription_end_date
                        else None
                    ),
                }
            return None

        finally:
            session.close()

    def update_subscription_usage(self, user_id: str, workflows_increment: int = 1) -> None:
        """
        Update subscription usage

        Args:
            user_id: User ID
            workflows_increment: Number of workflows to add to usage
        """
        session = self.get_session()
        try:
            subscription = (
                session.query(SubscriptionModel)
                .filter(
                    SubscriptionModel.user_id == uuid.UUID(user_id),
                    SubscriptionModel.status == "active",
                )
                .first()
            )

            if subscription:
                subscription.workflows_used += workflows_increment
                session.commit()
                metrics.record_memory_operation("session", "write")
                logger.debug(
                    f"Updated subscription usage",
                    user_id=user_id,
                    workflows_used=subscription.workflows_used,
                )

        finally:
            session.close()

    # ========================================================================
    # Invoice Operations
    # ========================================================================

    def create_invoice(
        self,
        user_id: str,
        amount: float,
        currency: str,
        due_date: datetime,
        subscription_id: Optional[str] = None,
        payment_id: Optional[str] = None,
        stripe_invoice_id: Optional[str] = None,
    ) -> str:
        """
        Create new invoice

        Args:
            user_id: User ID
            amount: Invoice amount
            currency: Currency code
            due_date: Due date
            subscription_id: Subscription ID (optional)
            payment_id: Payment ID (optional)
            stripe_invoice_id: Stripe invoice ID (optional)

        Returns:
            Invoice ID
        """
        session = self.get_session()
        try:
            # Generate invoice number
            invoice_number = f"INV-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

            invoice = InvoiceModel(
                user_id=uuid.UUID(user_id),
                subscription_id=uuid.UUID(subscription_id) if subscription_id else None,
                payment_id=uuid.UUID(payment_id) if payment_id else None,
                invoice_number=invoice_number,
                amount=amount,
                currency=currency,
                due_date=due_date,
                stripe_invoice_id=stripe_invoice_id,
            )
            session.add(invoice)
            session.commit()

            invoice_id = str(invoice.invoice_id)
            metrics.record_memory_operation("session", "write")
            logger.info(f"Created invoice", invoice_id=invoice_id)

            return invoice_id

        finally:
            session.close()

    def get_user_invoices(
        self, user_id: str, limit: int = 10, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get invoices for user

        Args:
            user_id: User ID
            limit: Number of records to return
            offset: Offset for pagination

        Returns:
            List of invoice records
        """
        session = self.get_session()
        try:
            invoices = (
                session.query(InvoiceModel)
                .filter(InvoiceModel.user_id == uuid.UUID(user_id))
                .order_by(InvoiceModel.invoice_date.desc())
                .limit(limit)
                .offset(offset)
                .all()
            )

            metrics.record_memory_operation("session", "read")

            return [
                {
                    "invoice_id": str(invoice.invoice_id),
                    "invoice_number": invoice.invoice_number,
                    "amount": invoice.amount,
                    "currency": invoice.currency,
                    "status": invoice.status,
                    "invoice_date": invoice.invoice_date.isoformat(),
                    "due_date": invoice.due_date.isoformat(),
                    "paid_date": invoice.paid_date.isoformat() if invoice.paid_date else None,
                    "pdf_url": invoice.pdf_url,
                }
                for invoice in invoices
            ]

        finally:
            session.close()

    def close(self) -> None:
        """Close database connection"""
        self.engine.dispose()
        logger.info("Session memory connection closed")
