# Memory & Sessions Example

This folder demonstrates how to use Strands agents with different session and memory management approaches.

## Files

### Session Management
- `Copilot_local.py`: Local file-based session manager using `FileSessionManager` with session state persisted locally.
- `Copilot_S3.py`: Amazon S3-based session storage for distributed session management.

### AgentCore Memory Integration
- `copilot_agentcore_stm.py`: Short-Term Memory (STM) example using `AgentCoreMemorySessionManager` with retrieval configs for user preferences.
- `copilot_agentcore_ltm.py`: Long-Term Memory (LTM) example using `AgentCoreMemorySessionManager` with multiple retrieval strategies (preferences, facts, summaries).

## Overview

These examples demonstrate:
- Creating a `BedrockModel` using `global.anthropic.claude-sonnet-4-6`
- Persisting agent sessions using different backends:
  - **Local**: `FileSessionManager` stores conversations locally under `./session/`
  - **S3**: Distributed session storage using Amazon S3
  - **AgentCore**: Integrated memory system with retrieval strategies
- Interacting with agents in a loop while preserving conversational state
- Configuring retrieval behaviors for semantic search and memory recall

## Requirements

- Python 3.10 or newer
- `strands-agents>=1.0.0` and `strands-agents-tools>=0.2.0`
- `bedrock-agentcore` (for AgentCore memory examples)
- AWS credentials configured for Bedrock

## Environment Configuration

Create a `.env` file with the following variables (for AgentCore examples):

```env
AGENTCORE_MEMORY_ID=your-memory-id-for-stm
AGENTCORE_LTM_MEMORY_ID=your-memory-id-for-ltm
```

Memory IDs can be created via AWS Console or setup scripts.

## Usage

### Local Session Example
```powershell
cd 2_memory_&_sessions
python Copilot_local.py
```

### S3 Session Example
```powershell
python Copilot_S3.py
```

### AgentCore STM Example
```powershell
python copilot_agentcore_stm.py
```

### AgentCore LTM Example
```powershell
python copilot_agentcore_ltm.py
```

Then enter a question when prompted.

## Memory Retrieval Strategies

The AgentCore examples use different retrieval configurations:

- **userPreferenceMemoryStrategy**: Retrieves user preferences (top_k=10, relevance_score=0.2)
- **semanticMemoryStrategy**: Semantic search over facts (top_k=10, relevance_score=0.3)
- **summaryMemoryStrategy**: Session-specific summaries (top_k=5, relevance_score=0.5)

Namespaces must start and end with a forward slash (e.g., `/preferences/{actorId}/`).

## Notes

- Ensure `callback_handler=None` is configured if you want to avoid duplicate console output from streaming events.
- Use context managers (`with` blocks) to safely handle sessions and prevent data loss.
- The `batch_size` parameter in AgentCoreMemoryConfig controls how many items are stored before automatic flushing.
- Session folders store conversation state and can be inspected for debugging.
