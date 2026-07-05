# ### The Basic Idea
# Strands follows a simple **model-driven loop**:

# ```
# Input → Model Thinks → Tools Used → Response Generated
import asyncio
from strands import Agent
from strands.session.file_session_manager import FileSessionManager
from strands.tools import tool 
from strands.models import BedrockModel
from strands.session.s3_session_manager import S3SessionManager
import boto3

# In the context of AI agents, Bedrock usually refers to Amazon Bedrock, 
# a fully managed service from Amazon Web Services (AWS) that provides 
# access to foundation models (LLMs and other AI models) through a single API.

bedrock_model = BedrockModel(
    model_id="global.anthropic.claude-sonnet-4-6",
    region_name="us-west-2",
    # temperature controls the randomness of the agent's responses. 
    # A lower temperature-------> will make the agent's responses more acurate and focused
    # higher temperature ------>will make agent's response more creative and diverse/random. 
    temperature=0.1,
    # max_tokens----> limits the length of the agent's response.
    max_tokens=1000 
)


# Create a session manager that stores data in S3
session_manager = S3SessionManager(
    session_id="user-456",
    bucket="my-agent-sessions1234",
)

# Create an agent with the session manager

copilot = Agent(
    system_prompt="""
    You are a helpful assistant that can answer questions 
    about a person based on the information provided in the 
    PersonInfo model.you will be given a PersonInfo object, 
    and you should use the information in that object to answer 
    questions about the person.
    """,
    session_manager=session_manager,
    model=bedrock_model,
    callback_handler=None
)

#-------------streaming response--------#
# Async function that iterates over streamed agent events
async def process_streaming_response(question):

    # Get an async iterator for the agent's response stream
    agent_stream = copilot.stream_async(question)

    # Process events as they arrive
    async for event in agent_stream:
        if "data" in event:
            # Print text chunks as they're generated
            print(event["data"], end="", flush=True)

# #flush=True tells Python:
# #"Don't keep the output in a buffer. Display it immediately."
# #What is a buffer?
# #When you use print(), Python often stores the output temporarily 
# # in memory (a buffer) before showing it on the screen. This reduces the number of write operations and improves performance.

# #------------------start the Tutor Agent------------#
while True:
    question=input("\n Ask something what is in your mind : ")
    if question!="":
        # Run the agent with the async event processing
        asyncio.run(process_streaming_response(question))
    else:
        print("Ask the valid Question")
        break



