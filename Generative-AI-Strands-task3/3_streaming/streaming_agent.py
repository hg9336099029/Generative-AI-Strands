import asyncio
from strands import Agent
from strands.tools import tool 
from strands.models import BedrockModel

# 1. Define a simple tool for the agent to use
@tool
def get_weather(location: str) -> str:
    """Returns the weather for a given location."""
    return f"The weather in {location} is 72 degrees and sunny."

async def main():

    bedrock_model = BedrockModel(
        model_id="global.anthropic.claude-sonnet-4-6",
        region_name="us-west-2",
        temperature=0.3
    )

    # Add the tool to the agent
    streaming_agent = Agent(
        system_prompt="You are a helpful assistant. Use tools if necessary.",
        model=bedrock_model,
        tools=[get_weather], # Register the tool
        callback_handler=None # Disable default console printing
    )
 
    # create asynchronous output function
    async def process_streaming_response(question):
        print("\nAgent: ", end="", flush=True)
        
        # Add mid-stream error handling using try...except
        try:
            agent_stream = streaming_agent.stream_async(question)
            
            async for event in agent_stream:
                # Handle standard text token streaming
                if "data" in event:
                    print(event["data"], end="", flush=True)
                #  Handle tool execution events gracefully mid-stream
                elif "tool_call" in event:
                    print(f"\n[Agent is using a tool: {event['tool_call']['name']}]... ", end="", flush=True)

        except Exception as e:
            print(f"\n[Stream interrupted due to an error: {e}. Please try asking again.]")
        print() 

    # Test the stream with a question that requires the tool
    test_question = "What is the weather like in Seattle today?"
    print(f"User: {test_question}")
    await process_streaming_response(test_question)

if __name__ == "__main__":
    asyncio.run(main())

