"""
Chroma vector database memory management for Council agents.

Replaces file-based JSON memory with semantic vector storage and retrieval.
Supports embedding-based context retrieval at each iteration.
"""

import os
from pathlib import Path
from typing import Optional, Dict, List
import chromadb
from chromadb.config import Settings


class ChromaMemoryManager:
    """Manages agent memory using Chroma vector database."""
    
    def __init__(self, agent_name: str, persist_dir: Optional[str] = None):
        """
        Initialize Chroma memory manager for an agent.
        
        Args:
            agent_name: Name of the agent (e.g., "rational", "ambitious")
            persist_dir: Directory to persist Chroma data (default: test/memory/chroma_db)
        """
        self.agent_name = agent_name
        
        # Setup persistence directory
        if persist_dir is None:
            persist_dir = str(
                (Path(__file__).resolve().parents[1] / "memory" / "chroma_db").resolve()
            )
        
        os.makedirs(persist_dir, exist_ok=True)
        self.persist_dir = persist_dir
        
        # Initialize Chroma client with persistence
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(
                allow_reset=True,
                anonymized_telemetry=False,
            )
        )
        
        # Create or get collection for this agent
        self.collection = self.client.get_or_create_collection(
            name=f"{agent_name}_memory",
            metadata={"agent": agent_name},
        )
    
    def reset_memory(self) -> None:
        """Clear all memory for this agent."""
        try:
            self.client.delete_collection(name=f"{self.agent_name}_memory")
            self.collection = self.client.get_or_create_collection(
                name=f"{self.agent_name}_memory",
                metadata={"agent": self.agent_name},
            )
        except Exception as e:
            print(f"[CHROMA RESET] Warning resetting {self.agent_name}: {e}")
    
    def add_response(
        self,
        exchange_num: int,
        response: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Store an agent's response with metadata.
        
        Args:
            exchange_num: Exchange/round number
            response: The agent's response text
            metadata: Optional metadata (peer responses, context, etc.)
        
        Returns:
            Document ID
        """
        doc_id = f"{self.agent_name}_exchange_{exchange_num}"
        
        if metadata is None:
            metadata = {}
        
        metadata.update({
            "agent": self.agent_name,
            "exchange": str(exchange_num),
            "type": "response",
        })
        
        self.collection.add(
            documents=[response],
            metadatas=[metadata],
            ids=[doc_id]
        )
        
        return doc_id
    
    def add_opinion(
        self,
        peer_name: str,
        score: int,
        opinion_text: str,
        exchange_num: int
    ) -> str:
        """
        Store an opinion about another peer.
        
        Args:
            peer_name: Name of the peer agent
            score: Opinion score (-100 to 100)
            opinion_text: Text describing the opinion
            exchange_num: Exchange number
        
        Returns:
            Document ID
        """
        doc_id = f"{self.agent_name}_opinion_{peer_name}_{exchange_num}"
        
        metadata = {
            "agent": self.agent_name,
            "type": "opinion",
            "peer": peer_name,
            "score": str(score),
            "exchange": str(exchange_num),
        }
        
        self.collection.add(
            documents=[opinion_text],
            metadatas=[metadata],
            ids=[doc_id]
        )
        
        return doc_id
    
    def retrieve_responses(
        self,
        query: str,
        num_results: int = 3,
        exchange_num: Optional[int] = None
    ) -> List[Dict]:
        """
        Retrieve relevant past responses using semantic search.
        
        Args:
            query: Query text to search for similar responses
            num_results: Number of results to return
            exchange_num: Optional filter by exchange number
        
        Returns:
            List of relevant responses with metadata
        """
        try:
            count = self.collection.count()
            if count == 0:
                return []
            
            where_filter = {"type": "response"}
            if exchange_num is not None:
                where_filter["exchange"] = str(exchange_num)
            
            results = self.collection.query(
                query_texts=[query],
                n_results=min(num_results, count),
                where=where_filter
            )
            
            # Format results
            formatted = []
            if results and results["documents"] and results["documents"][0]:
                for doc, meta, distance in zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0]
                ):
                    formatted.append({
                        "response": doc,
                        "exchange": int(meta.get("exchange", 0)),
                        "similarity": 1 - distance,
                        "metadata": meta
                    })
            
            return formatted
        except Exception as e:
            print(f"[CHROMA RETRIEVE] Error retrieving responses for {self.agent_name}: {e}")
            return []
    
    def retrieve_opinions(self, peer_name: str, num_results: int = 2) -> List[Dict]:
        """
        Retrieve stored opinions about a specific peer.
        
        Args:
            peer_name: Name of the peer
            num_results: Number of opinions to retrieve
        
        Returns:
            List of opinions with scores
        """
        try:
            where_filter = {
                "type": "opinion",
                "peer": peer_name
            }
            
            results = self.collection.query(
                query_texts=[f"opinion about {peer_name}"],
                n_results=num_results,
                where=where_filter
            )
            
            formatted = []
            if results and results["documents"] and results["documents"][0]:
                for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
                    formatted.append({
                        "opinion": doc,
                        "score": int(meta.get("score", 0)),
                        "exchange": int(meta.get("exchange", 0)),
                        "peer": meta.get("peer"),
                    })
            
            return formatted
        except Exception as e:
            print(f"[CHROMA OPINION] Error retrieving opinions for {self.agent_name}: {e}")
            return []
    
    def get_memory_summary(self) -> Dict:
        """Get a summary of stored memory."""
        try:
            response_count = self.collection.count()
        except:
            response_count = 0
        
        return {
            "agent": self.agent_name,
            "total_documents": response_count,
            "persist_dir": self.persist_dir,
        }
    
    def export_memory(self) -> Dict:
        """Export all memory as structured data."""
        try:
            all_data = self.collection.get()
            
            responses = []
            opinions = {}
            
            for doc, meta in zip(all_data["documents"], all_data["metadatas"]):
                if meta.get("type") == "response":
                    responses.append({
                        "exchange": int(meta.get("exchange", 0)),
                        "response": doc
                    })
                elif meta.get("type") == "opinion":
                    peer = meta.get("peer")
                    if peer not in opinions:
                        opinions[peer] = []
                    opinions[peer].append({
                        "score": int(meta.get("score", 0)),
                        "opinion": doc,
                        "exchange": int(meta.get("exchange", 0))
                    })
            
            return {
                "agent": self.agent_name,
                "responses": responses,
                "opinions": opinions,
            }
        except Exception as e:
            print(f"[CHROMA EXPORT] Error exporting {self.agent_name}: {e}")
            return {"agent": self.agent_name, "responses": [], "opinions": {}}
