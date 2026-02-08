"""
Context Synthesis Engine - Builds optimal context for LLM calls

Intelligently selects and compresses information to maximize LLM performance
while minimizing token usage. Goes beyond simple retrieval to synthesize
the most relevant context.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import math

from autoos.infrastructure.logging import get_logger

logger = get_logger(__name__)


class ContextElement:
    """Represents a piece of context"""

    def __init__(
        self,
        element_id: str,
        content: str,
        relevance: float,
        token_count: int,
        source: str,
    ):
        self.element_id = element_id
        self.content = content
        self.relevance = relevance
        self.token_count = token_count
        self.source = source


class ContextSynthesisEngine:
    """
    Context synthesis and optimization system

    Features:
    - Intelligently selects most relevant context
    - Compresses information without losing meaning
    - Optimizes token usage
    - Synthesizes information from multiple sources
    - Adapts context based on task requirements
    """

    def __init__(self):
        """Initialize context synthesis engine"""
        self.context_cache: Dict[str, List[ContextElement]] = {}
        self.compression_strategies: Dict[str, float] = {}

        logger.info("Context synthesis engine initialized")

    def synthesize_optimal_context(
        self,
        task: Dict[str, Any],
        available_context: List[Dict[str, Any]],
        token_budget: int,
    ) -> str:
        """
        Build optimal context for task within token budget

        Args:
            task: Task to build context for
            available_context: All available context elements
            token_budget: Maximum tokens to use

        Returns:
            Synthesized context string
        """
        logger.info(
            f"Synthesizing context",
            task_id=task.get("task_id"),
            budget=token_budget,
        )

        # Convert to ContextElements
        elements = []
        for ctx in available_context:
            relevance = self._calculate_relevance(task, ctx)
            token_count = self._estimate_tokens(ctx.get("content", ""))

            element = ContextElement(
                element_id=ctx.get("id", "unknown"),
                content=ctx.get("content", ""),
                relevance=relevance,
                token_count=token_count,
                source=ctx.get("source", "unknown"),
            )
            elements.append(element)

        # Select best elements within budget
        selected = self._select_elements(elements, token_budget)

        # Synthesize into coherent context
        synthesized = self._synthesize_elements(selected, task)

        logger.info(
            f"Context synthesized",
            elements_selected=len(selected),
            final_tokens=self._estimate_tokens(synthesized),
        )

        return synthesized

    def compress_context(
        self, context: str, target_compression: float
    ) -> str:
        """
        Compress context while preserving key information

        Args:
            context: Context to compress
            target_compression: Target compression ratio (0-1)

        Returns:
            Compressed context
        """
        if target_compression >= 1.0:
            return context

        # Split into sentences
        sentences = context.split(". ")

        # Calculate importance of each sentence
        sentence_scores = []
        for sentence in sentences:
            score = self._calculate_sentence_importance(sentence, context)
            sentence_scores.append((sentence, score))

        # Sort by importance
        sentence_scores.sort(key=lambda x: x[1], reverse=True)

        # Select top sentences to meet compression target
        target_count = int(len(sentences) * target_compression)
        selected_sentences = [s[0] for s in sentence_scores[:target_count]]

        # Reconstruct in original order
        compressed = ". ".join(
            s for s in sentences if s in selected_sentences
        )

        logger.info(
            f"Compressed context",
            original_tokens=self._estimate_tokens(context),
            compressed_tokens=self._estimate_tokens(compressed),
            ratio=target_compression,
        )

        return compressed

    def extract_key_information(
        self, context: str, information_type: str
    ) -> List[str]:
        """
        Extract specific type of information from context

        Args:
            context: Context to extract from
            information_type: Type of information (facts, actions, entities, etc.)

        Returns:
            List of extracted information
        """
        extracted = []

        if information_type == "facts":
            # Extract factual statements
            sentences = context.split(". ")
            for sentence in sentences:
                if self._is_factual(sentence):
                    extracted.append(sentence)

        elif information_type == "actions":
            # Extract action items
            sentences = context.split(". ")
            for sentence in sentences:
                if self._contains_action(sentence):
                    extracted.append(sentence)

        elif information_type == "entities":
            # Extract named entities (simplified)
            words = context.split()
            for word in words:
                if word[0].isupper() and len(word) > 1:
                    extracted.append(word)

        logger.info(
            f"Extracted {len(extracted)} {information_type} from context"
        )

        return extracted

    def merge_contexts(
        self, contexts: List[str], strategy: str = "union"
    ) -> str:
        """
        Merge multiple contexts intelligently

        Args:
            contexts: List of context strings
            strategy: Merge strategy (union, intersection, synthesis)

        Returns:
            Merged context
        """
        if not contexts:
            return ""

        if strategy == "union":
            # Combine all unique information
            all_sentences = []
            for context in contexts:
                all_sentences.extend(context.split(". "))

            # Remove duplicates while preserving order
            unique_sentences = []
            seen = set()
            for sentence in all_sentences:
                normalized = sentence.lower().strip()
                if normalized not in seen:
                    unique_sentences.append(sentence)
                    seen.add(normalized)

            merged = ". ".join(unique_sentences)

        elif strategy == "intersection":
            # Keep only common information
            sentence_sets = [set(ctx.split(". ")) for ctx in contexts]
            common = sentence_sets[0]
            for s in sentence_sets[1:]:
                common = common.intersection(s)

            merged = ". ".join(common)

        else:  # synthesis
            # Synthesize into coherent narrative
            merged = self._synthesize_narrative(contexts)

        logger.info(
            f"Merged {len(contexts)} contexts using {strategy} strategy"
        )

        return merged

    def adapt_context_for_model(
        self, context: str, model_name: str
    ) -> str:
        """
        Adapt context for specific model characteristics

        Args:
            context: Context to adapt
            model_name: Target model name

        Returns:
            Adapted context
        """
        # Model-specific adaptations
        if "gpt-4" in model_name:
            # GPT-4 handles complex context well
            return context

        elif "gpt-3.5" in model_name:
            # GPT-3.5 benefits from more structured context
            adapted = self._structure_context(context)
            return adapted

        elif "claude" in model_name:
            # Claude prefers detailed, explicit context
            adapted = self._expand_context(context)
            return adapted

        else:
            # Default: no adaptation
            return context

    def _calculate_relevance(
        self, task: Dict[str, Any], context: Dict[str, Any]
    ) -> float:
        """Calculate relevance score for context element"""
        # Simplified relevance calculation
        # In production, would use embeddings and semantic similarity

        task_keywords = set(task.get("description", "").lower().split())
        context_keywords = set(context.get("content", "").lower().split())

        # Jaccard similarity
        intersection = len(task_keywords.intersection(context_keywords))
        union = len(task_keywords.union(context_keywords))

        relevance = intersection / union if union > 0 else 0.0

        # Boost recent context
        if context.get("timestamp"):
            age_hours = (
                datetime.utcnow()
                - datetime.fromisoformat(context["timestamp"])
            ).total_seconds() / 3600
            recency_boost = math.exp(-age_hours / 24)  # Decay over 24 hours
            relevance *= (1 + recency_boost)

        return min(1.0, relevance)

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        # Rough estimation: ~4 characters per token
        return len(text) // 4

    def _select_elements(
        self, elements: List[ContextElement], budget: int
    ) -> List[ContextElement]:
        """Select best elements within token budget"""
        # Sort by relevance
        elements.sort(key=lambda e: e.relevance, reverse=True)

        selected = []
        total_tokens = 0

        for element in elements:
            if total_tokens + element.token_count <= budget:
                selected.append(element)
                total_tokens += element.token_count
            else:
                # Try compression
                compression_ratio = (budget - total_tokens) / element.token_count
                if compression_ratio > 0.3:  # Worth compressing
                    compressed_content = self.compress_context(
                        element.content, compression_ratio
                    )
                    compressed_element = ContextElement(
                        element_id=element.element_id,
                        content=compressed_content,
                        relevance=element.relevance * compression_ratio,
                        token_count=self._estimate_tokens(compressed_content),
                        source=element.source,
                    )
                    selected.append(compressed_element)
                    total_tokens += compressed_element.token_count

                break

        return selected

    def _synthesize_elements(
        self, elements: List[ContextElement], task: Dict[str, Any]
    ) -> str:
        """Synthesize elements into coherent context"""
        if not elements:
            return ""

        # Group by source
        by_source: Dict[str, List[ContextElement]] = {}
        for element in elements:
            if element.source not in by_source:
                by_source[element.source] = []
            by_source[element.source].append(element)

        # Build context sections
        sections = []

        # Add task description
        sections.append(f"Task: {task.get('description', 'Unknown task')}")

        # Add context from each source
        for source, source_elements in by_source.items():
            section_content = " ".join(e.content for e in source_elements)
            sections.append(f"\n{source.title()} Context:\n{section_content}")

        return "\n".join(sections)

    def _calculate_sentence_importance(
        self, sentence: str, full_context: str
    ) -> float:
        """Calculate importance of sentence in context"""
        # Factors: length, position, keyword density

        # Length factor (prefer medium-length sentences)
        words = sentence.split()
        length_score = min(len(words) / 20.0, 1.0)

        # Keyword density (simplified)
        important_words = ["must", "critical", "important", "key", "essential"]
        keyword_score = sum(1 for word in words if word.lower() in important_words)

        # Position factor (first and last sentences often important)
        sentences = full_context.split(". ")
        position = sentences.index(sentence) if sentence in sentences else len(sentences) // 2
        position_score = 1.0 if position < 3 or position > len(sentences) - 3 else 0.5

        # Combine scores
        importance = (length_score + keyword_score + position_score) / 3.0

        return importance

    def _is_factual(self, sentence: str) -> bool:
        """Check if sentence is factual"""
        # Simplified check
        factual_indicators = ["is", "are", "was", "were", "has", "have", "contains"]
        return any(indicator in sentence.lower() for indicator in factual_indicators)

    def _contains_action(self, sentence: str) -> bool:
        """Check if sentence contains action"""
        action_verbs = ["execute", "run", "perform", "create", "delete", "update"]
        return any(verb in sentence.lower() for verb in action_verbs)

    def _synthesize_narrative(self, contexts: List[str]) -> str:
        """Synthesize multiple contexts into coherent narrative"""
        # Extract key points from each context
        all_points = []
        for context in contexts:
            sentences = context.split(". ")
            # Take most important sentences
            for sentence in sentences[:3]:  # Top 3 from each
                all_points.append(sentence)

        # Remove duplicates
        unique_points = []
        seen = set()
        for point in all_points:
            normalized = point.lower().strip()
            if normalized not in seen:
                unique_points.append(point)
                seen.add(normalized)

        return ". ".join(unique_points)

    def _structure_context(self, context: str) -> str:
        """Add structure to context"""
        sentences = context.split(". ")

        structured = "Key Information:\n"
        for i, sentence in enumerate(sentences, 1):
            structured += f"{i}. {sentence}\n"

        return structured

    def _expand_context(self, context: str) -> str:
        """Expand context with more detail"""
        # Add explicit markers
        expanded = f"Context Details:\n\n{context}\n\nEnd of Context"
        return expanded
