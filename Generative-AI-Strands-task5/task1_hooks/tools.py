from strands import tool

# A simple calculator tool that evaluates a mathematical expression.
@tool
def calculator(expression: str) -> str:
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Calculation Error: {e}"


# A weather tool that returns a mock weather report for a given city.
@tool
def weather(city: str) -> str:
    return f"The current weather in {city} is sunny with a temperature of 25°C."


# A tool that returns the same message.
@tool
def echo(message: str) -> str:
    """
    Returns the same message.
    """
    return message


# A tool that returns a secret message, which should be blocked by a hook.
@tool
def secret_tool() -> str:
    """
    Tool that should be blocked by a hook.
    """
    return "TOP SECRET DATA"