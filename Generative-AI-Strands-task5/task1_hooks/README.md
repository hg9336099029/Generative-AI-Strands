# Task 1: Hooks Example

This folder demonstrates a Strands agent lifecycle hook provider that:

- logs key lifecycle events
- intercepts tool execution before it runs
- blocks specific tool calls based on guardrail logic

## Files

- `hooks.py`: defines `LifecycleLogger`, a `HookProvider` that logs lifecycle events and blocks admin-related tool calls.
- `prompts.py`: defines the system prompt and the `fetch_user_data` tool.
- `tools.py`: defines example tools including `calculator`, `weather`, `echo`, and `secret_tool`.
- `app.py`: builds the agent, attaches the hook provider, and runs two sample prompts.

## Run

1. Ensure you have the required packages installed and your model provider credentials configured.
2. Run:

```bash
python app.py
```

## Notes

- The hook blocks tool calls if the input contains the string `admin`.
- Update the `model` parameter in `app.py` if you need to use a different model or provider.
