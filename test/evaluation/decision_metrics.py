"""
Final decision evaluation metrics for Council agent system.

Evaluates the quality and characteristics of final decisions generated
by the council, including coherence, diversity, uniqueness, and confidence.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import math


@dataclass
class DecisionMetrics:
    """Metrics for a single decision."""
    decision_text: str
    agent_responses: Dict[str, str]  # agent_name -> their response
    mode: str  # "personal" or "whatif"
    query: str
    exchange_count: int
    agent_count: int
    
    def length(self) -> int:
        """Decision text length in characters."""
        return len(self.decision_text)
    
    def word_count(self) -> int:
        """Decision text word count."""
        return len(self.decision_text.split())
    
    def sentence_count(self) -> int:
        """Decision text sentence count."""
        import re
        sentences = re.split(r'[.!?]+', self.decision_text.strip())
        return len([s for s in sentences if s.strip()])
    
    def avg_sentence_length(self) -> float:
        """Average words per sentence."""
        sentence_count = self.sentence_count()
        if sentence_count == 0:
            return 0.0
        return self.word_count() / sentence_count
    
    def coverage_ratio(self) -> float:
        """
        Coverage: How many agent perspectives are mentioned in decision?
        
        Returns:
            Ratio of agents mentioned to total agents (0.0 to 1.0)
        """
        decision_lower = self.decision_text.lower()
        mentioned = 0
        
        for agent_name in self.agent_responses.keys():
            agent_lower = agent_name.lower()
            if agent_lower in decision_lower:
                mentioned += 1
        
        total = len(self.agent_responses)
        return mentioned / total if total > 0 else 0.0
    
    def terminology_alignment(self) -> float:
        """
        Alignment: How much of the decision uses terminology from agent responses?
        
        Measures semantic alignment by checking for key terms.
        
        Returns:
            Alignment score (0.0 to 1.0)
        """
        decision_words = set(self.decision_text.lower().split())
        agent_words = set()
        
        for response in self.agent_responses.values():
            agent_words.update(response.lower().split())
        
        # Remove common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'to', 'of'}
        decision_words -= common_words
        agent_words -= common_words
        
        shared = decision_words & agent_words
        if not decision_words:
            return 0.0
        
        return len(shared) / len(decision_words)
    
    def distinctiveness(self) -> float:
        """
        Distinctiveness: How unique is this decision from individual responses?
        
        Measured by vocabulary not present in agent responses.
        
        Returns:
            Score (0.0 to 1.0) - higher = more unique
        """
        decision_words = set(self.decision_text.lower().split())
        agent_words = set()
        
        for response in self.agent_responses.values():
            agent_words.update(response.lower().split())
        
        unique_in_decision = decision_words - agent_words
        if not decision_words:
            return 0.0
        
        return len(unique_in_decision) / len(decision_words)
    
    def decisiveness_score(self) -> float:
        """
        Decisiveness: How actionable/directive is the decision?
        
        Counts action verbs and instructions.
        
        Returns:
            Score (0.0 to 1.0)
        """
        action_verbs = {
            'should', 'must', 'recommend', 'suggest', 'consider', 'try', 'focus',
            'prioritize', 'avoid', 'invest', 'develop', 'build', 'start', 'stop',
            'continue', 'improve', 'learn', 'practice', 'plan', 'execute'
        }
        
        words = self.decision_text.lower().split()
        action_count = sum(1 for word in words if word.rstrip('.,!?') in action_verbs)
        
        if len(words) == 0:
            return 0.0
        
        return min(1.0, action_count / len(words) * 10)  # Scale to 0-1
    
    def confidence_level(self) -> float:
        """
        Confidence: How certain/confident does the decision sound?
        
        Based on confidence indicators vs uncertainty indicators.
        
        Returns:
            Score (-1.0 to 1.0) - positive = confident, negative = uncertain
        """
        text_lower = self.decision_text.lower()
        
        confidence_words = {
            'clearly', 'definitely', 'certainly', 'absolutely', 'should', 'will',
            'must', 'strong', 'proven', 'evidence', 'fact', 'obvious'
        }
        
        uncertainty_words = {
            'might', 'could', 'perhaps', 'may', 'possibly', 'uncertainty',
            'unclear', 'risky', 'question', 'uncertain', 'probably', 'seems'
        }
        
        conf_count = sum(1 for word in confidence_words if word in text_lower)
        unc_count = sum(1 for word in uncertainty_words if word in text_lower)
        
        total = conf_count + unc_count
        if total == 0:
            return 0.0
        
        return (conf_count - unc_count) / total


@dataclass
class AggregatedDecisionMetrics:
    """Aggregated decision metrics across multiple decisions."""
    decisions: List[DecisionMetrics]
    
    def avg_length(self) -> float:
        """Average decision length."""
        if not self.decisions:
            return 0.0
        return sum(d.length() for d in self.decisions) / len(self.decisions)
    
    def avg_word_count(self) -> float:
        """Average word count."""
        if not self.decisions:
            return 0.0
        return sum(d.word_count() for d in self.decisions) / len(self.decisions)
    
    def avg_coverage(self) -> float:
        """Average coverage ratio."""
        if not self.decisions:
            return 0.0
        return sum(d.coverage_ratio() for d in self.decisions) / len(self.decisions)
    
    def avg_alignment(self) -> float:
        """Average terminology alignment."""
        if not self.decisions:
            return 0.0
        return sum(d.terminology_alignment() for d in self.decisions) / len(self.decisions)
    
    def avg_distinctiveness(self) -> float:
        """Average distinctiveness."""
        if not self.decisions:
            return 0.0
        return sum(d.distinctiveness() for d in self.decisions) / len(self.decisions)
    
    def avg_decisiveness(self) -> float:
        """Average decisiveness."""
        if not self.decisions:
            return 0.0
        return sum(d.decisiveness_score() for d in self.decisions) / len(self.decisions)
    
    def avg_confidence(self) -> float:
        """Average confidence level."""
        if not self.decisions:
            return 0.0
        return sum(d.confidence_level() for d in self.decisions) / len(self.decisions)
    
    def quality_score(self) -> float:
        """
        Composite quality score (0.0 to 1.0).
        
        Weighted combination of all metrics.
        """
        if not self.decisions:
            return 0.0
        
        # Normalize metrics to 0-1 range
        coverage = self.avg_coverage()  # Already 0-1
        alignment = self.avg_alignment()  # Already 0-1
        distinctiveness = self.avg_distinctiveness()  # Already 0-1
        decisiveness = self.avg_decisiveness()  # Already 0-1
        confidence = max(0.0, self.avg_confidence())  # Scale -1 to 1 to 0-1
        
        # Weighted average
        weights = {
            'coverage': 0.25,
            'alignment': 0.20,
            'distinctiveness': 0.15,
            'decisiveness': 0.25,
            'confidence': 0.15,
        }
        
        score = (
            coverage * weights['coverage'] +
            alignment * weights['alignment'] +
            distinctiveness * weights['distinctiveness'] +
            decisiveness * weights['decisiveness'] +
            confidence * weights['confidence']
        )
        
        return score
    
    def summary_report(self) -> Dict[str, float]:
        """Generate comprehensive report."""
        return {
            "total_decisions": len(self.decisions),
            "avg_length_chars": self.avg_length(),
            "avg_word_count": self.avg_word_count(),
            "coverage_ratio": self.avg_coverage(),
            "terminology_alignment": self.avg_alignment(),
            "distinctiveness": self.avg_distinctiveness(),
            "decisiveness_score": self.avg_decisiveness(),
            "confidence_level": self.avg_confidence(),
            "quality_score": self.quality_score(),
        }
    
    def print_summary(self):
        """Pretty-print summary report."""
        report = self.summary_report()
        print("\n" + "="*60)
        print("FINAL DECISION EVALUATION METRICS")
        print("="*60)
        print(f"Total Decisions Evaluated: {report['total_decisions']}")
        print()
        print("TEXT CHARACTERISTICS:")
        print(f"  Avg Length (chars)      : {report['avg_length_chars']:.1f}")
        print(f"  Avg Word Count          : {report['avg_word_count']:.1f}")
        print()
        print("QUALITY METRICS:")
        print(f"  Coverage Ratio          : {report['coverage_ratio']:.4f} (agents mentioned)")
        print(f"  Terminology Alignment   : {report['terminology_alignment']:.4f} (with responses)")
        print(f"  Distinctiveness         : {report['distinctiveness']:.4f} (unique content)")
        print(f"  Decisiveness Score      : {report['decisiveness_score']:.4f} (actionability)")
        print(f"  Confidence Level        : {report['confidence_level']:.4f} (certainty)")
        print()
        print(f"OVERALL QUALITY SCORE     : {report['quality_score']:.4f} ⭐")
        print("="*60)


class DecisionEvaluator:
    """Manages decision evaluation."""
    
    def __init__(self):
        self.decisions: List[DecisionMetrics] = []
    
    def add_decision(
        self,
        decision_text: str,
        agent_responses: Dict[str, str],
        mode: str,
        query: str,
        exchange_count: int,
        agent_count: int
    ):
        """Record a decision for evaluation."""
        metric = DecisionMetrics(
            decision_text=decision_text,
            agent_responses=agent_responses,
            mode=mode,
            query=query,
            exchange_count=exchange_count,
            agent_count=agent_count
        )
        self.decisions.append(metric)
    
    def get_aggregated_metrics(self) -> AggregatedDecisionMetrics:
        """Get aggregated metrics."""
        return AggregatedDecisionMetrics(self.decisions)
    
    def report(self) -> Dict:
        """Generate full report."""
        agg = self.get_aggregated_metrics()
        return agg.summary_report()
