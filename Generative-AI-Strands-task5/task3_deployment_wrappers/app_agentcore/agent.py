from strands import Agent, tool

@tool
def get_status(system: str) -> str:
    """Returns the operational status of a system."""
    return f"System '{system}' is fully operational."

# Shared agent instance
agent = Agent(
    tools=[get_status],
    system_prompt="You are a deployment tester. Use your tool to check system status."
)
