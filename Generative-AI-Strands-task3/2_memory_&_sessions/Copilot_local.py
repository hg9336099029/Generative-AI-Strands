import asyncio
from strands import Agent
from strands.session.file_session_manager import FileSessionManager
from strands.tools import tool 
from strands.models import BedrockModel

async def main():
    # In the context of AI agents, Bedrock usually refers to Amazon Bedrock...
    bedrock_model = BedrockModel(
        model_id="global.anthropic.claude-sonnet-4-6",
        region_name="us-west-2",
        temperature=0.3,
        max_tokens=1000 
    )

    # Create a Local session manager with a unique session ID
    session_manager = FileSessionManager(
        session_id="user-124",
        storage_dir="./2_memory_&_sessions/session"  # Stores sessions in the local filesystem
    )

    tutor_agent = Agent(
        system_prompt="""
        You are a copilot that helps users learn about to give some 
        information about the any topic. You will be given a question, 
        and you should use your knowledge and reasoning abilities to 
        provide a clear and concise answer.
        """,
        # Create an agent with the session manager using the convenience shorthand
        session_manager=session_manager,
        model=bedrock_model,

        # point ---> where I take a lot of time to debug

        # The duplication in your response is happening because Strands agents
        # display their reasoning and responses in real-time to the console by default.
        #
        # Because your code uses an async iterator (stream_async()) and manually
        # prints event["data"] to the console as it arrives, the response is being
        # printed twice: once by the agent's default background handler, and once
        # by your custom print(event["data"]) loop.
        #
        #---> To fix this and stop the double-printing, you need to disable the agent's
        #---> default console output by setting callback_handler=None when creating your agent.
        callback_handler=None
    )

    # Async function that iterates over streamed agent events
    async def process_streaming_response(question):
        # Get an async iterator for the agent's response stream
        agent_stream = tutor_agent.stream_async(question)

        # Process events as they arrive
        async for event in agent_stream:
            if "data" in event:
                print(event["data"], end="", flush=True)

    #------------------start the Tutor Agent------------#
    while True:
        question = input("\nAsk something what is in your mind : ")
        if question != "":
            # AWAIT the response on the active event loop instead of recreating it
            await process_streaming_response(question)
        else:
            print("Ask a valid question")

# Run the single event loop to encompass the agent's full lifecycle
if __name__ == "__main__":
    asyncio.run(main())