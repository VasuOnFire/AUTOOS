"""
Meta-Learning Engine - Learns how to learn better

Advanced capability that analyzes learning patterns and optimizes
the learning process itself. Goes beyond simple pattern recognition
to understand HOW the system learns and improves that process.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import json
import math

from autoos.core.models import Workflow, WorkflowResult
from autoos.infrastructure.logging import get_logger

logger = get_logger(__name__)


class LearningPattern:
    """Represents a discovered learning pattern"""

    def __init__(
        self,
        pattern_id: str,
        pattern_type: str,
        effectiveness: float,
        context: Dict[str, Any],
    ):
        self.pattern_id = pattern_id
        self.pattern_type = pattern_type
        self.effectiveness = effectiveness
        self.context = context
        self.usage_count = 0
        self.success_rate = 0.0


class MetaLearningEngine:
    """
    Meta-learning system that learns how to learn

    Features:
    - Analyzes which learning strategies work best
    - Identifies optimal model combinations
    - Discovers emergent patterns across workflows
    - Optimizes the learning process itself
    - Predicts which strategies will work for new problems
    """

    def __init__(self):
        """Initialize meta-learning engine"""
        self.learning_patterns: Dict[str, LearningPattern] = {}
        self.strategy_effectiveness: Dict[str, List[float]] = defaultdict(list)
        self.model_synergies: Dict[Tuple[str, str], float] = {}
        self.adaptation_history: List[Dict[str, Any]] = []

        logger.info("Meta-learning engine initialized")

    def analyze_learning_effectiveness(
        self, workflow_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze how well the system is learning

        Args:
            workflow_history: Historical workflow data

        Returns:
            Learning effectiveness analysis
        """
        if len(workflow_history) < 10:
            return {
                "learning_rate": 0.0,
                "improvement_trend": "insufficient_data",
                "recommendations": ["Need more execution history"],
            }

        # Calculate success rate over time windows
        window_size = 10
        success_rates = []

        for i in range(0, len(workflow_history) - window_size, window_size):
            window = workflow_history[i : i + window_size]
            successes = sum(1 for w in window if w.get("success", False))
            success_rates.append(successes / window_size)

        # Calculate learning rate (improvement over time)
        if len(success_rates) >= 2:
            learning_rate = (success_rates[-1] - success_rates[0]) / len(success_rates)
        else:
            learning_rate = 0.0

        # Determine trend
        if learning_rate > 0.05:
            trend = "improving"
        elif learning_rate < -0.05:
            trend = "degrading"
        else:
            trend = "stable"

        # Generate recommendations
        recommendations = self._generate_learning_recommendations(
            learning_rate, success_rates, workflow_history
        )

        logger.info(
            f"Learning effectiveness analyzed",
            learning_rate=learning_rate,
            trend=trend,
        )

        return {
            "learning_rate": learning_rate,
            "improvement_trend": trend,
            "success_rates": success_rates,
            "recommendations": recommendations,
        }

    def discover_model_synergies(
        self, execution_history: List[Dict[str, Any]]
    ) -> Dict[Tuple[str, str], float]:
        """
        Discover which model combinations work best together

        Args:
            execution_history: Historical execution data

        Returns:
            Dictionary of model pairs to synergy scores
        """
        # Track model pair performance
        pair_performance: Dict[Tuple[str, str], List[float]] = defaultdict(list)

        for execution in execution_history:
            models_used = execution.get("models_used", [])
            success = execution.get("success", False)
            confidence = execution.get("confidence", 0.0)

            # Record all model pairs
            for i in range(len(models_used)):
                for j in range(i + 1, len(models_used)):
                    pair = tuple(sorted([models_used[i], models_used[j]]))
                    score = confidence if success else 0.0
                    pair_performance[pair].append(score)

        # Calculate synergy scores
        synergies = {}
        for pair, scores in pair_performance.items():
            if len(scores) >= 3:  # Need minimum data
                avg_score = sum(scores) / len(scores)
                synergies[pair] = avg_score

        # Update internal state
        self.model_synergies.update(synergies)

        logger.info(f"Discovered {len(synergies)} model synergies")

        return synergies

    def recommend_optimal_model_combination(
        self, task_type: str, complexity: float
    ) -> List[str]:
        """
        Recommend best model combination for task

        Args:
            task_type: Type of task
            complexity: Task complexity (0-1)

        Returns:
            List of recommended models
        """
        # Find best performing synergies
        sorted_synergies = sorted(
            self.model_synergies.items(), key=lambda x: x[1], reverse=True
        )

        if not sorted_synergies:
            # Default recommendation
            if complexity > 0.7:
                return ["gpt-4", "claude-3-opus-20240229"]
            else:
                return ["gpt-3.5-turbo", "claude-3-haiku-20240307"]

        # Select top synergy
        best_pair = sorted_synergies[0][0]

        logger.info(
            f"Recommended model combination",
            models=list(best_pair),
            synergy_score=sorted_synergies[0][1],
        )

        return list(best_pair)

    def identify_emergent_patterns(
        self, workflow_history: List[Dict[str, Any]]
    ) -> List[LearningPattern]:
        """
        Discover emergent patterns across workflows

        Args:
            workflow_history: Historical workflow data

        Returns:
            List of discovered patterns
        """
        patterns = []

        # Pattern 1: Time-of-day performance
        time_performance = self._analyze_time_patterns(workflow_history)
        if time_performance:
            patterns.append(
                LearningPattern(
                    pattern_id="time_of_day",
                    pattern_type="temporal",
                    effectiveness=time_performance["effectiveness"],
                    context=time_performance,
                )
            )

        # Pattern 2: Complexity thresholds
        complexity_patterns = self._analyze_complexity_patterns(workflow_history)
        if complexity_patterns:
            patterns.append(
                LearningPattern(
                    pattern_id="complexity_threshold",
                    pattern_type="structural",
                    effectiveness=complexity_patterns["effectiveness"],
                    context=complexity_patterns,
                )
            )

        # Pattern 3: Recovery success patterns
        recovery_patterns = self._analyze_recovery_patterns(workflow_history)
        if recovery_patterns:
            patterns.append(
                LearningPattern(
                    pattern_id="recovery_strategy",
                    pattern_type="operational",
                    effectiveness=recovery_patterns["effectiveness"],
                    context=recovery_patterns,
                )
            )

        # Store patterns
        for pattern in patterns:
            self.learning_patterns[pattern.pattern_id] = pattern

        logger.info(f"Identified {len(patterns)} emergent patterns")

        return patterns

    def optimize_learning_strategy(
        self, current_performance: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize how the system learns

        Args:
            current_performance: Current performance metrics

        Returns:
            Optimized learning strategy
        """
        # Analyze current learning effectiveness
        learning_rate = current_performance.get("learning_rate", 0.0)
        success_rate = current_performance.get("success_rate", 0.0)

        # Determine if learning strategy needs adjustment
        if learning_rate < 0.01 and success_rate < 0.8:
            # Learning is stagnant - increase exploration
            strategy = {
                "exploration_rate": 0.3,  # Try more alternatives
                "verification_threshold": 0.9,  # Be more careful
                "model_diversity": "high",  # Use more model variety
                "learning_rate_adjustment": 1.5,  # Learn faster
            }
        elif learning_rate > 0.1:
            # Learning too fast - might be overfitting
            strategy = {
                "exploration_rate": 0.1,  # Exploit known patterns
                "verification_threshold": 0.75,  # Standard verification
                "model_diversity": "medium",  # Balanced approach
                "learning_rate_adjustment": 0.8,  # Slow down learning
            }
        else:
            # Optimal learning - maintain
            strategy = {
                "exploration_rate": 0.15,
                "verification_threshold": 0.8,
                "model_diversity": "medium",
                "learning_rate_adjustment": 1.0,
            }

        logger.info(f"Optimized learning strategy", strategy=strategy)

        return strategy

    def predict_adaptation_success(
        self, proposed_change: Dict[str, Any], context: Dict[str, Any]
    ) -> float:
        """
        Predict if a proposed adaptation will succeed

        Args:
            proposed_change: Proposed system change
            context: Current context

        Returns:
            Success probability (0-1)
        """
        # Analyze similar past adaptations
        similar_adaptations = [
            a
            for a in self.adaptation_history
            if a.get("change_type") == proposed_change.get("type")
        ]

        if not similar_adaptations:
            # No history - neutral prediction
            return 0.5

        # Calculate success rate of similar adaptations
        successes = sum(1 for a in similar_adaptations if a.get("success", False))
        success_rate = successes / len(similar_adaptations)

        # Adjust based on context similarity
        context_similarity = self._calculate_context_similarity(
            context, similar_adaptations
        )

        adjusted_probability = success_rate * (0.5 + 0.5 * context_similarity)

        logger.info(
            f"Predicted adaptation success",
            probability=adjusted_probability,
            similar_count=len(similar_adaptations),
        )

        return adjusted_probability

    def record_adaptation(
        self, change: Dict[str, Any], success: bool, impact: Dict[str, Any]
    ) -> None:
        """
        Record an adaptation for meta-learning

        Args:
            change: Change that was made
            success: Whether it succeeded
            impact: Impact metrics
        """
        adaptation = {
            "change": change,
            "success": success,
            "impact": impact,
            "timestamp": datetime.utcnow().isoformat(),
        }

        self.adaptation_history.append(adaptation)

        logger.info(f"Recorded adaptation", success=success)

    def _generate_learning_recommendations(
        self,
        learning_rate: float,
        success_rates: List[float],
        history: List[Dict[str, Any]],
    ) -> List[str]:
        """Generate recommendations for improving learning"""
        recommendations = []

        if learning_rate < 0:
            recommendations.append(
                "System is degrading - review recent changes and consider rollback"
            )

        if learning_rate < 0.02:
            recommendations.append(
                "Learning is slow - increase exploration rate and try new strategies"
            )

        if len(success_rates) > 0 and success_rates[-1] < 0.7:
            recommendations.append(
                "Recent success rate low - increase verification and use more reliable models"
            )

        if not recommendations:
            recommendations.append("Learning is optimal - maintain current strategy")

        return recommendations

    def _analyze_time_patterns(
        self, history: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Analyze time-of-day performance patterns"""
        # Group by hour of day
        hour_performance: Dict[int, List[float]] = defaultdict(list)

        for workflow in history:
            timestamp = workflow.get("timestamp")
            if timestamp:
                hour = datetime.fromisoformat(timestamp).hour
                success = 1.0 if workflow.get("success") else 0.0
                hour_performance[hour].append(success)

        if not hour_performance:
            return None

        # Find best and worst hours
        hour_averages = {
            hour: sum(scores) / len(scores)
            for hour, scores in hour_performance.items()
        }

        best_hour = max(hour_averages.items(), key=lambda x: x[1])
        worst_hour = min(hour_averages.items(), key=lambda x: x[1])

        effectiveness = best_hour[1] - worst_hour[1]

        if effectiveness > 0.1:  # Significant pattern
            return {
                "effectiveness": effectiveness,
                "best_hour": best_hour[0],
                "worst_hour": worst_hour[0],
                "recommendation": f"Schedule critical tasks around hour {best_hour[0]}",
            }

        return None

    def _analyze_complexity_patterns(
        self, history: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Analyze complexity threshold patterns"""
        # Group by complexity ranges
        complexity_ranges = {
            "low": (0.0, 0.3),
            "medium": (0.3, 0.7),
            "high": (0.7, 1.0),
        }

        range_performance: Dict[str, List[float]] = defaultdict(list)

        for workflow in history:
            complexity = workflow.get("complexity", 0.5)
            success = 1.0 if workflow.get("success") else 0.0

            for range_name, (low, high) in complexity_ranges.items():
                if low <= complexity < high:
                    range_performance[range_name].append(success)
                    break

        if not range_performance:
            return None

        # Calculate success rates
        range_averages = {
            range_name: sum(scores) / len(scores)
            for range_name, scores in range_performance.items()
        }

        # Find threshold where success drops
        if range_averages.get("high", 1.0) < range_averages.get("medium", 1.0) * 0.8:
            return {
                "effectiveness": 0.7,
                "threshold": 0.7,
                "recommendation": "Use enhanced verification for high complexity tasks",
            }

        return None

    def _analyze_recovery_patterns(
        self, history: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Analyze recovery strategy effectiveness"""
        recovery_success: Dict[str, List[bool]] = defaultdict(list)

        for workflow in history:
            recovery_used = workflow.get("recovery_strategy")
            if recovery_used:
                success = workflow.get("success", False)
                recovery_success[recovery_used].append(success)

        if not recovery_success:
            return None

        # Find most effective recovery
        recovery_rates = {
            strategy: sum(successes) / len(successes)
            for strategy, successes in recovery_success.items()
        }

        best_strategy = max(recovery_rates.items(), key=lambda x: x[1])

        return {
            "effectiveness": best_strategy[1],
            "best_strategy": best_strategy[0],
            "recommendation": f"Prefer {best_strategy[0]} recovery strategy",
        }

    def _calculate_context_similarity(
        self, context: Dict[str, Any], adaptations: List[Dict[str, Any]]
    ) -> float:
        """Calculate similarity between contexts"""
        # Simplified similarity calculation
        # In production, would use embeddings or more sophisticated comparison

        if not adaptations:
            return 0.0

        # Compare key context features
        similarities = []
        for adaptation in adaptations:
            adapt_context = adaptation.get("context", {})

            # Compare numeric features
            numeric_sim = 0.0
            numeric_count = 0

            for key in ["complexity", "cost", "confidence"]:
                if key in context and key in adapt_context:
                    diff = abs(context[key] - adapt_context[key])
                    numeric_sim += 1.0 - min(diff, 1.0)
                    numeric_count += 1

            if numeric_count > 0:
                similarities.append(numeric_sim / numeric_count)

        return sum(similarities) / len(similarities) if similarities else 0.0
