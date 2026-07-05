# Streaming Response Example

This folder demonstrates how to stream responses from a Strands agent in real time.

## Files

- `agent.py`: example script showing how to create an agent and iterate over streamed response events.

## Overview

- Uses a `BedrockModel` with the `global.anthropic.claude-sonnet-4-6` model.
- Streams agent output with `stream_async(...)`.
- Prints received response chunks to the console as they arrive.

## Requirements

- Python 3.10 or newer
- `strands-agents` and `strands-agents-tools`
- AWS credentials for Amazon Bedrock

## Usage

1. Open a terminal and navigate to the repository root.
2. Activate your Python environment if needed.
3. Change into the streaming folder:

```powershell
cd 3_streaming
```

4. Start the agent:

```powershell
python agent.py
```

5. When the script prompts for input, type your question or prompt and press Enter.
6. Watch the streamed response arrive in the console.

## Notes

- Streaming is useful for long responses and interactive applications.
- Make sure the console can display text as chunks arrive.
