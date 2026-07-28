# Task 2: Plugins Demo

This folder contains a small plugin-based AI assistant demo using the `strands` library.

## Overview

The demo shows how to wrap multiple related tools into a plugin and expose them to an agent.

- `app.py` launches an interactive assistant loop.
- `plugins.py` defines reusable tools and a plugin class.

## Tools included

- `calculator(expression: str)` — evaluates simple mathematical expressions.
- `weather(city: str)` — returns dummy weather information for a city.
- `fetch_user(username: str)` — returns profile information for a hardcoded user.

## How to run

1. Install dependencies if needed.
2. Run the demo:

```bash
python app.py
```

3. Ask questions in the prompt.
4. Type `exit` to quit.

## Example usage

- `What is 5 * 8?`
- `What is the weather in Paris?`
- `Tell me about user harsh.`

## Notes

- The agent uses a system prompt that directs it to call the appropriate tool when needed.
- This is a simple demo and can be extended with more tools or real integrations.
