# Chroma Vector Memory Integration Summary

## What Was Done

### 1. **New: `memory/chroma_memory.py`**
   - Created `ChromaMemoryManager` class with:
     - **`reset_memory()`**: Clear all agent memory
     - **`add_response()`**: Store agent responses with metadata in Chroma
     - **`add_opinion()`**: Store opinions about peers with scoring
     - **`retrieve_responses()`**: Semantic search for relevant past responses
     - **`retrieve_opinions()`**: Lookup peer opinions with scores
     - **`export_memory()`**: Export all memory as structured data

### 2. **Updated: `requirements.txt`**
   - Added `chromadb>=0.4.0`
   - Added `sentence-transformers>=2.2.0` (for embeddings)

### 3. **Updated: `langgraph_workflow.py`**
   - **Import**: Added `from memory.chroma_memory import ChromaMemoryManager`
   - **`create_agent_node()`**: Now accepts optional `chroma_manager` parameter
     - Retrieves past responses using semantic search before agent responds
     - Stores new responses to Chroma vector DB after generation
     - Adds `past_context` to council_context for agent awareness
   - **`create_council_graph()`**: Now accepts `chroma_managers` dict
   - **`run_council_workflow()`**: Now initializes Chroma managers instead of file-based memory
   - **Removed**: Old `_reset_agent_memories()` function (Chroma handles it)

## How It Works Now

```
START WORKFLOW
├── Initialize ChromaMemoryManager for each agent
├── Reset Chroma memory if RESET_MEMORY_ON_START=1
├── FOR EACH EXCHANGE (1-4):
│   └── FOR EACH AGENT:
│       ├── Query Chroma: "Retrieve 2 most relevant past responses"
│       ├── Build council_context with retrieved context
│       ├── Agent generates response (informed by past context)
│       ├── Store response in Chroma with metadata
│       ├── Update transcript and state
│       └── NEXT AGENT
├── Generate final decision
└── END WORKFLOW
```

## Vector Memory Benefits

| Feature | File-Based | Chroma |
|---------|-----------|--------|
| Storage | JSON files | Vector DB |
| Lookup | Exact match | **Semantic search** |
| At iteration | Manual parsing | **Auto-retrieve top-k** |
| Opinions | Static key-value | **Scored, timestamped** |
| Scale | Limited | **Optimized for ML** |
| Persistence | Local files | **Vector persistence** |

## Installation

```bash
cd test
pip install -r requirements.txt
```

This installs:
- `chromadb` - Vector database
- `sentence-transformers` - Default embeddings (All-MiniLM-L6-v2)

## Usage (No changes to existing code flow)

```python
from langgraph_workflow import run_council_workflow

result = run_council_workflow(
    mode="personal",
    query="I want to transition into MLOps",
    additional_info=[...],
    total_exchanges=4,
    reset_memory=True  # Clears Chroma memory
)
```

## Memory Persistence

- **Location**: `test/memory/chroma_db/`
- **Format**: Chroma vector database
- **Per-Agent**: Separate collection for each agent (e.g., `rational_memory`, `ambitious_memory`)
- **Auto-persistence**: Changes saved immediately

## Chroma Collections Structure

Each agent has a collection with documents:
```json
{
  "id": "rational_exchange_1",
  "document": "I believe we should focus on...",
  "metadata": {
    "agent": "rational",
    "exchange": "1",
    "type": "response",
    "query": "I want to transition...",
    "mode": "personal"
  }
}
```

## Query & Retrieval Example

```python
# Semantic search for relevant past context
past_responses = chroma_manager.retrieve_responses(
    query="career transition goals",
    num_results=2
)
# Returns: [{response, exchange, similarity, metadata}, ...]
```

## Testing

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run CLI
```bash
python main.py
```

### 3. Check Chroma DB created
```bash
ls -la memory/chroma_db/
```

### 4. Export memory after run
```python
from memory.chroma_memory import ChromaMemoryManager
manager = ChromaMemoryManager("rational")
memory = manager.export_memory()
print(memory)
```

## API Compatibility

✅ **Frontend unchanged** - Same HTTP endpoints  
✅ **Response format same** - API contract preserved  
✅ **Memory transparent** - Chroma is internal to workflow  
✅ **CLI works** - main.py still works identically  

## Key Differences from File Memory

1. **Not JSON** - Chroma uses SQLite + vector embeddings
2. **Semantic not literal** - Finds relevant past context by meaning
3. **Automatic indexing** - No manual JSON parsing
4. **Scale efficient** - Handles thousands of memories
5. **Per-iteration context** - Each agent gets most relevant history

## Future Enhancements

- **Opinion tracking**: Use `add_opinion()` to track peer relationships
- **Query analytics**: See what context agents retrieve most
- **Custom embeddings**: Use `chromadb.get_embedding_function()`
- **Filtering**: Add where-filters for exchange number, mode, etc.

---

**Status**: ✅ Complete and ready to test
**Memory Type**: Semantic vector persistence with auto-retrieval
**Database**: Chroma (SQLite + embeddings)
