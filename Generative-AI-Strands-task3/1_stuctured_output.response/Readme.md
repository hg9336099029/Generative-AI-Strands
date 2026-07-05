# Structured Output Agent

This folder contains `agent.py`, an example Strands agent that extracts structured person information from text using a Pydantic model and an Amazon Bedrock-backed LLM.

## Overview

- Defines a `PersonInfo` schema with fields: `name`, `age`, `email`, `occupation`, and `address`
- Configures a `BedrockModel` for `global.anthropic.claude-sonnet-4-6`
- Creates an `Agent` with a system prompt and structured output validation
- Calls `copilot.invoke_async(...)` to generate and validate structured output
- Prints the parsed `PersonInfo` values or validation errors

## Requirements

- Python 3.x
- `strands`
- `pydantic`
- AWS credentials configured for Amazon Bedrock
- Access to the `global.anthropic.claude-sonnet-4-6` Bedrock model

## Usage

Run the agent script from the folder:

```powershell
python agent.py
```

### Start the code

1. Open a terminal in `1_stuctured_output.response`
2. Verify your Python environment and AWS Bedrock credentials
3. Run `python agent.py`
4. Observe the structured output or validation error in the terminal

The script invokes the agent asynchronously, then prints the parsed structured fields:

- `name`
- `age`
- `email`
- `occupation`
- `address`

## Customization

- Change `bedrock_model.model_id` and `region_name` to use a different Bedrock model or region
- Update the input prompt text in `invoke_async(...)` to parse a different person description
- Extend `PersonInfo` with additional fields if you want the agent to extract more structured data

## Notes

- The script wraps the agent call in a `try`/`except` block to handle `ValidationError`
- `structured_output_model=PersonInfo` ensures the returned output is validated against the schema
- `temperature=0.3` keeps the output focused and less random
