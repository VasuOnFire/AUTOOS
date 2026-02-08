"""
Predictive Intelligence Engine - Learns from past executions and predicts outcomes

The brain that makes AUTOOS truly intelligent and self-improving.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import json

from autoos.core.models import Workflow, WorkflowResult, FailureType, Lesson
from autoos.memory.session_memory import SessionMemory
from autoos.infrastructure.logging import get_logger

logger = get_logger(__name__)


class PredictiveEngine:
    """
    Predictive intelligence and learning system

    Features:
    - Predict workflow success probability
    - Estimate cost and time before execution
    - Learn from past failures
    - Identify patterns across workflows
    - Recommend optimal strategies
    - Detect anomalies in real-time
    """

    def __init__(self, session_memory: SessionMemory):
        """
        Initialize predictive engine

        Args:
            session_memory: Session memory for historical data
        """
        self.session_memory = session_memory
        self.pattern_cache: Dict[str, List[Dict]] = defaultdict(list)
        self.failure_patterns: Dict[str, int] = defaultdict(int)

        logger.info("Predictive engine initialized")

    def predict_success_probability(
        self, workflow: Workflow, context: Dict[str, Any]
    ) -> float:
        """
        Predict probability of workflow success

        Args:
            workflow: Workflow to predict
            context: Execution context

        Returns:
            Success probability (0-1)
        """
        # Analyze similar past workflows
        similar_workflows = self._find_similar_workflows(workflow, limit=10)

        if not similar_workflows:
            # No history, return neutral probability
            return 0.7

        # Calculate success rate from similar workflows
        successful = sum(1 for w in similar_workflows if w["status"] == "completed")
        total = len(similar_workflows)

        base_probability = successful / total if total > 0 else 0.5

        # Adjust based on complexity
        complexity_factor = self._calculate_complexity(workflow)
        adjusted_probability = base_probability * (1 - complexity_factor * 0.2)

        # Adjust based on recent failures
        recent_failures = self._get_recent_failures(workflow, hours=24)
        if recent_failures > 3:
            adjusted_probability *= 0.8

        logger.info(
            f"Predicted success probability",
            workflow_id=workflow.workflow_id,
            probability=adjusted_probability,
            similar_count=total,
        )

        return max(0.1, min(0.95, adjusted_probability))

    def estimate_cost_and_time(
        self, workflow: Workflow
    ) -> Tuple[float, float]:
        """
        Estimate cost and execution time

        Args:
            workflow: Workflow to estimate

        Returns:
            Tuple of (estimated_cost, estimated_time_seconds)
        """
        # Find similar workflows
        similar_workflows = self._find_similar_workflows(workflow, limit=20)

        if not similar_workflows:
            # Default estimates
            return (0.15, 45.0)

        # Calculate averages from similar workflows
        costs = [w.get("cost", 0.0) for w in similar_workflows if w.get("cost")]
        times = []

        for w in similar_workflows:
            if w.get("created_at") and w.get("completed_at"):
                created = datetime.fromisoformat(w["created_at"])
                completed = datetime.fromisoformat(w["completed_at"])
                duration = (completed - created).total_seconds()
                times.append(duration)

        avg_cost = sum(costs) / len(costs) if costs else 0.15
        avg_time = sum(times) / len(times) if times else 45.0

        # Adjust for complexity
        complexity = self._calculate_complexity(workflow)
        adjusted_cost = avg_cost * (1 + complexity * 0.5)
        adjusted_time = avg_time * (1 + complexity * 0.3)

        logger.info(
            f"Estimated cost and time",
            workflow_id=workflow.workflow_id,
            cost=adjusted_cost,
            time=adjusted_time,
        )

        return (adjusted_cost, adjusted_time)

    def learn_from_execution(
        self, workflow_result: WorkflowResult, workflow: Workflow
    ) -> None:
        """
        Learn from completed workflow execution

        Args:
            workflow_result: Execution result
            workflow: Executed workflow
        """
        logger.info(
            f"Learning from execution",
            workflow_id=workflow_result.workflow_id,
            success=workflow_result.success,
        )

        # Extract patterns
        pattern = {
            "workflow_id": workflow_result.workflow_id,
            "success": workflow_result.success,
            "cost": workflow_result.total_cost,
            "time": workflow_result.total_time,
            "confidence": workflow_result.avg_confidence,
            "steps_completed": workflow_result.steps_completed,
            "steps_failed": workflow_result.steps_failed,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Store in pattern cache
        workflow_type = self._classify_workflow(workflow)
        self.pattern_cache[workflow_type].append(pattern)

        # Update failure patterns if failed
        if not workflow_result.success:
            self.failure_patterns[workflow_type] += 1

        # Generate lessons learned
        lessons = self._generate_lessons(workflow_result, workflow)
        for lesson in lessons:
            logger.info(f"Lesson learned", lesson=lesson.pattern)

    def identify_anomalies(
        self, workflow: Workflow, current_metrics: Dict[str, Any]
    ) -> List[str]:
        """
        Detect anomalies in real-time execution

        Args:
            workflow: Current workflow
            current_metrics: Current execution metrics

        Returns:
            List of detected anomalies
        """
        anomalies = []

        # Get historical metrics for similar workflows
        similar = self._find_similar_workflows(workflow, limit=50)

        if len(similar) < 5:
            # Not enough data
            return anomalies

        # Check cost anomaly
        costs = [w.get("cost", 0.0) for w in similar if w.get("cost")]
        if costs:
            avg_cost = sum(costs) / len(costs)
            current_cost = current_metrics.get("cost", 0.0)

            if current_cost > avg_cost * 2:
                anomalies.append(
                    f"Cost anomaly: {current_cost:.2f} vs avg {avg_cost:.2f}"
                )

        # Check confidence anomaly
        confidences = [
            w.get("confidence", 0.0) for w in similar if w.get("confidence")
        ]
        if confidences:
            avg_confidence = sum(confidences) / len(confidences)
            current_confidence = current_metrics.get("confidence", 0.0)

            if current_confidence < avg_confidence * 0.7:
                anomalies.append(
                    f"Confidence anomaly: {current_confidence:.2f} vs avg {avg_confidence:.2f}"
                )

        if anomalies:
            logger.warning(
                f"Anomalies detected",
                workflow_id=workflow.workflow_id,
                anomalies=anomalies,
            )

        return anomalies

    def recommend_strategy(
        self, workflow: Workflow, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Recommend optimal execution strategy

        Args:
            workflow: Workflow to execute
            context: Execution context

        Returns:
            Strategy recommendation
        """
        # Predict success probability
        success_prob = self.predict_success_probability(workflow, context)

        # Get failure patterns
        workflow_type = self._classify_workflow(workflow)
        failure_count = self.failure_patterns.get(workflow_type, 0)

        # Recommend strategy based on predictions
        if success_prob < 0.5:
            strategy = "high_verification"
            recommendation = {
                "strategy": strategy,
                "reason": "Low success probability - use multiple verifiers",
                "llm_roles": ["planner", "executor", "verifier", "verifier"],
                "confidence_threshold": 0.9,
            }
        elif failure_count > 5:
            strategy = "conservative"
            recommendation = {
                "strategy": strategy,
                "reason": "High failure history - use conservative approach",
                "llm_roles": ["planner", "executor", "verifier"],
                "confidence_threshold": 0.85,
            }
        else:
            strategy = "standard"
            recommendation = {
                "strategy": strategy,
                "reason": "Normal execution expected",
                "llm_roles": ["planner", "executor"],
                "confidence_threshold": 0.75,
            }

        logger.info(
            f"Strategy recommended",
            workflow_id=workflow.workflow_id,
            strategy=strategy,
        )

        return recommendation

    def _find_similar_workflows(
        self, workflow: Workflow, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Find similar past workflows"""
        # Simplified similarity - would use embeddings in production
        workflow_type = self._classify_workflow(workflow)

        # Get from pattern cache
        patterns = self.pattern_cache.get(workflow_type, [])

        # Sort by recency
        patterns.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        return patterns[:limit]

    def _classify_workflow(self, workflow: Workflow) -> str:
        """Classify workflow type"""
        # Simple classification based on step count
        step_count = len(workflow.steps)

        if step_count <= 3:
            return "simple"
        elif step_count <= 7:
            return "medium"
        else:
            return "complex"

    def _calculate_complexity(self, workflow: Workflow) -> float:
        """Calculate workflow complexity (0-1)"""
        # Factors: step count, dependencies, parallel execution
        step_count = len(workflow.steps)
        parallel_groups = len(workflow.execution_order)

        # Normalize
        complexity = (step_count / 20.0) + (parallel_groups / 10.0)

        return min(1.0, complexity)

    def _get_recent_failures(self, workflow: Workflow, hours: int = 24) -> int:
        """Get count of recent failures for similar workflows"""
        workflow_type = self._classify_workflow(workflow)
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        patterns = self.pattern_cache.get(workflow_type, [])

        recent_failures = sum(
            1
            for p in patterns
            if not p.get("success")
            and datetime.fromisoformat(p.get("timestamp", "2000-01-01"))
            > cutoff
        )

        return recent_failures

    def _generate_lessons(
        self, result: WorkflowResult, workflow: Workflow
    ) -> List[Lesson]:
        """Generate lessons from execution"""
        lessons = []

        # Lesson from failure
        if not result.success:
            lesson = Lesson(
                pattern=f"Workflow type {self._classify_workflow(workflow)} failed",
                context={
                    "workflow_id": result.workflow_id,
                    "steps_completed": result.steps_completed,
                    "steps_failed": result.steps_failed,
                },
                outcome="failure",
                success=False,
                confidence=result.avg_confidence,
            )
            lessons.append(lesson)

        # Lesson from low confidence
        if result.avg_confidence < 0.6:
            lesson = Lesson(
                pattern="Low confidence execution",
                context={
                    "workflow_id": result.workflow_id,
                    "confidence": result.avg_confidence,
                },
                outcome="low_confidence",
                success=result.success,
                confidence=result.avg_confidence,
            )
            lessons.append(lesson)

        # Lesson from high cost
        if result.total_cost > 1.0:
            lesson = Lesson(
                pattern="High cost execution",
                context={
                    "workflow_id": result.workflow_id,
                    "cost": result.total_cost,
                },
                outcome="high_cost",
                success=result.success,
                confidence=1.0,
            )
            lessons.append(lesson)

        return lessons
