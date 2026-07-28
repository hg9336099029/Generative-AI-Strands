from strands import Agent
from hooks import LifecycleLogger
from prompts import SYSTEM_PROMPT, fetch_user_data
from tools import calculator, weather, echo, secret_tool


def print_agent_response(label: str, response: object) -> None:
    message = getattr(response, "message", None)
    if message is None:
        message = getattr(response, "output", None)
    if message is None:
        message = str(response)
    print(f"\n{label}: {message}\n")


def main():
    # Build the agent with a clear system prompt, available tools, and a lifecycle hook.
    agent = Agent(
        system_prompt=SYSTEM_PROMPT,
        tools=[fetch_user_data, calculator, weather, echo, secret_tool],
        hooks=[LifecycleLogger()]
    )

    # print("--- SCENARIO A: Valid Tool Call ---")
    # result_valid = agent("Fetch the data for the 'guest' user.")
    # print_agent_response("Final Agent Response", result_valid)

    # print("--- SCENARIO B: Blocked Tool Call (Modifying Behavior) ---")
    # result_blocked = agent("Fetch the data for the 'admin' user.")
    # print_agent_response("Final Agent Response", result_blocked)

    print("--- INTERACTIVE MODE ---")
    while True:
        question = input("Enter your question (or type 'exit' to quit): ").strip()
        if not question:
            continue
        if question.lower() in {"exit", "quit", "q"}:
            print("Goodbye!")
            break
        response = agent(question)
        print_agent_response("Agent Response", response)


if __name__ == "__main__":
    main()
    