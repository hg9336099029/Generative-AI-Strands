from strands import Agent
from plugins import UtilityPlugin


SYSTEM_PROMPT = """
You are a helpful AI assistant.

Rules:
- Use calculator for mathematical expressions.
- Use weather for weather-related questions.
- Use fetch_user for user information.
- If no tool is required, answer normally.
"""


plugin = UtilityPlugin()

agent = Agent(
    system_prompt=SYSTEM_PROMPT,
    tools=plugin.get_tools()
)


print("=== Strands Tool & Plugin Demo ===")

while True:

    question = input("\nYou: ")

    if question.lower() == "exit":
        break

    response = agent(question)

    print("\nAssistant:")
    print(response)