"""
Retrieval evaluation metrics for Chroma memory.

Computes Hit@k, Recall@k, MRR (Mean Reciprocal Rank), and ndcg for evaluating
semantic search quality during agent decision-making.
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass
import math


@dataclass
class RetrievalMetrics:
    """Metrics for a single retrieval instance."""
    query: str
    agent: str
    exchange: int
    retrieved_ids: List[str]  # IDs of retrieved documents
    relevant_ids: List[str]   # IDs of truly relevant documents
    similarities: List[float] # Similarity scores of retrieved items
    
    def __post_init__(self):
        """Validate inputs."""
        if len(self.retrieved_ids) != len(self.similarities):
            raise ValueError("retrieved_ids and similarities must have same length")
    
    def hit_at_k(self, k: int) -> int:
        """
        Hit@k: Binary indicator if any relevant item is in top-k.
        
        Returns:
            1 if at least one relevant item in top-k, else 0
        """
        if not self.relevant_ids:
            return 0
        
        top_k = self.retrieved_ids[:k]
        return 1 if any(item_id in self.relevant_ids for item_id in top_k) else 0
    
    def recall_at_k(self, k: int) -> float:
        """
        Recall@k: Proportion of relevant items retrieved in top-k.
        
        Formula: |{relevant items in top-k}| / |total relevant items|
        
        Returns:
            Recall score (0.0 to 1.0)
        """
        if not self.relevant_ids:
            return 0.0
        
        top_k = self.retrieved_ids[:k]
        relevant_retrieved = sum(1 for item_id in top_k if item_id in self.relevant_ids)
        return relevant_retrieved / len(self.relevant_ids)
    
    def precision_at_k(self, k: int) -> float:
        """
        Precision@k: Proportion of retrieved items that are relevant in top-k.
        
        Formula: |{relevant items in top-k}| / k
        
        Returns:
            Precision score (0.0 to 1.0)
        """
        if k == 0 or not self.retrieved_ids:
            return 0.0
        
        top_k = self.retrieved_ids[:k]
        relevant_retrieved = sum(1 for item_id in top_k if item_id in self.relevant_ids)
        return relevant_retrieved / min(k, len(top_k))
    
    def mean_reciprocal_rank(self) -> float:
        """
        MRR: Reciprocal of the rank of the first relevant item.
        
        Returns:
            1/rank if relevant item found, else 0.0
        """
        if not self.relevant_ids:
            return 0.0
        
        for rank, item_id in enumerate(self.retrieved_ids, start=1):
            if item_id in self.relevant_ids:
                return 1.0 / rank
        return 0.0
    
    def ndcg_at_k(self, k: int) -> float:
        """
        NDCG@k: Normalized Discounted Cumulative Gain.
        
        Considers ranking quality and relevance scores.
        
        Returns:
            NDCG score (0.0 to 1.0)
        """
        if not self.relevant_ids or not self.similarities:
            return 0.0
        
        # Calculate DCG
        dcg = 0.0
        top_k_ids = self.retrieved_ids[:k]
        top_k_sims = self.similarities[:k]
        
        for rank, (item_id, sim) in enumerate(zip(top_k_ids, top_k_sims), start=1):
            relevance = 1.0 if item_id in self.relevant_ids else 0.0
            dcg += (relevance * sim) / math.log2(rank + 1)
        
        # Calculate IDCG (ideal ranking)
        idcg = 0.0
        # Best case: all relevant items first, sorted by similarity
        ideal_sims = sorted(self.similarities, reverse=True)[:min(k, len(self.relevant_ids))]
        for rank, sim in enumerate(ideal_sims, start=1):
            idcg += sim / math.log2(rank + 1)
        
        # Normalize
        if idcg == 0.0:
            return 0.0
        return dcg / idcg


@dataclass
class AggregatedMetrics:
    """Aggregated retrieval metrics across multiple queries."""
    metrics_list: List[RetrievalMetrics]
    k_values: List[int] = None
    
    def __post_init__(self):
        if self.k_values is None:
            self.k_values = [1, 3, 5, 10]
    
    def hit_at_k(self, k: int) -> float:
        """Average Hit@k across all queries."""
        if not self.metrics_list:
            return 0.0
        hits = [m.hit_at_k(k) for m in self.metrics_list]
        return sum(hits) / len(hits)
    
    def recall_at_k(self, k: int) -> float:
        """Average Recall@k across all queries."""
        if not self.metrics_list:
            return 0.0
        recalls = [m.recall_at_k(k) for m in self.metrics_list]
        return sum(recalls) / len(recalls)
    
    def precision_at_k(self, k: int) -> float:
        """Average Precision@k across all queries."""
        if not self.metrics_list:
            return 0.0
        precisions = [m.precision_at_k(k) for m in self.metrics_list]
        return sum(precisions) / len(precisions)
    
    def mrr(self) -> float:
        """Mean Reciprocal Rank across all queries."""
        if not self.metrics_list:
            return 0.0
        mrrs = [m.mean_reciprocal_rank() for m in self.metrics_list]
        return sum(mrrs) / len(mrrs)
    
    def ndcg_at_k(self, k: int) -> float:
        """Average NDCG@k across all queries."""
        if not self.metrics_list:
            return 0.0
        ndcgs = [m.ndcg_at_k(k) for m in self.metrics_list]
        return sum(ndcgs) / len(ndcgs)
    
    def summary_report(self) -> Dict[str, float]:
        """Generate comprehensive metrics report."""
        report = {
            "total_retrievals": len(self.metrics_list),
            "mrr": self.mrr(),
        }
        
        for k in self.k_values:
            report[f"hit@{k}"] = self.hit_at_k(k)
            report[f"recall@{k}"] = self.recall_at_k(k)
            report[f"precision@{k}"] = self.precision_at_k(k)
            report[f"ndcg@{k}"] = self.ndcg_at_k(k)
        
        return report
    
    def per_agent_report(self) -> Dict[str, Dict[str, float]]:
        """Generate metrics per agent."""
        agents = {}
        for metric in self.metrics_list:
            if metric.agent not in agents:
                agents[metric.agent] = []
            agents[metric.agent].append(metric)
        
        report = {}
        for agent_name, agent_metrics in agents.items():
            agg = AggregatedMetrics(agent_metrics, self.k_values)
            report[agent_name] = agg.summary_report()
        
        return report
    
    def per_exchange_report(self) -> Dict[int, Dict[str, float]]:
        """Generate metrics per exchange."""
        exchanges = {}
        for metric in self.metrics_list:
            if metric.exchange not in exchanges:
                exchanges[metric.exchange] = []
            exchanges[metric.exchange].append(metric)
        
        report = {}
        for exchange_num, exchange_metrics in exchanges.items():
            agg = AggregatedMetrics(exchange_metrics, self.k_values)
            report[exchange_num] = agg.summary_report()
        
        return report
    
    def print_summary(self):
        """Pretty-print summary report."""
        report = self.summary_report()
        print("\n" + "="*60)
        print("RETRIEVAL EVALUATION METRICS")
        print("="*60)
        print(f"Total Retrievals: {report['total_retrievals']}")
        print(f"MRR (Mean Reciprocal Rank): {report['mrr']:.4f}")
        print()
        
        for k in self.k_values:
            print(f"\n@k={k}:")
            print(f"  Hit@{k}      : {report.get(f'hit@{k}', 0):.4f}")
            print(f"  Recall@{k}   : {report.get(f'recall@{k}', 0):.4f}")
            print(f"  Precision@{k}: {report.get(f'precision@{k}', 0):.4f}")
            print(f"  NDCG@{k}     : {report.get(f'ndcg@{k}', 0):.4f}")
        
        print("\n" + "="*60)
    
    def print_per_agent(self):
        """Pretty-print per-agent report."""
        report = self.per_agent_report()
        print("\n" + "="*60)
        print("RETRIEVAL METRICS BY AGENT")
        print("="*60)
        
        for agent_name, metrics in report.items():
            print(f"\n{agent_name.upper()}:")
            print(f"  Retrievals: {metrics['total_retrievals']}")
            print(f"  MRR: {metrics['mrr']:.4f}")
            
            for k in self.k_values:
                recall = metrics.get(f'recall@{k}', 0)
                print(f"  Recall@{k}: {recall:.4f}")


class RetrievalEvaluator:
    """Manages retrieval evaluation throughout workflow."""
    
    def __init__(self):
        self.metrics: List[RetrievalMetrics] = []
    
    def add_retrieval(
        self,
        query: str,
        agent: str,
        exchange: int,
        retrieved_ids: List[str],
        relevant_ids: List[str],
        similarities: List[float]
    ):
        """Record a retrieval event for evaluation."""
        metric = RetrievalMetrics(
            query=query,
            agent=agent,
            exchange=exchange,
            retrieved_ids=retrieved_ids,
            relevant_ids=relevant_ids,
            similarities=similarities
        )
        self.metrics.append(metric)
    
    def get_aggregated_metrics(self, k_values: List[int] = None) -> AggregatedMetrics:
        """Get aggregated metrics."""
        return AggregatedMetrics(self.metrics, k_values)
    
    def report(self) -> Dict:
        """Generate full evaluation report."""
        agg = self.get_aggregated_metrics()
        return {
            "summary": agg.summary_report(),
            "per_agent": agg.per_agent_report(),
            "per_exchange": agg.per_exchange_report(),
        }
