# ### The Basic Idea
# Strands follows a simple **model-driven loop**:

# Input → Model Thinks → Tools Used → Response Generated
import asyncio #------>
from strands import Agent
from strands.session.file_session_manager import FileSessionManager
from strands.tools import tool 
from strands.models import BedrockModel

# In the context of AI agents, Bedrock usually refers to Amazon Bedrock, 
# a fully managed service from Amazon Web Services (AWS) that provides 
# access to foundation models (LLMs and other AI models) through a single API.

bedrock_model = BedrockModel(
    model_id="global.anthropic.claude-sonnet-4-6",
    region_name="us-west-2",
    # temperature controls the randomness of the agent's responses. 
    # A lower temperature-------> will make the agent's responses more acurate and focused
    # higher temperature ------>will make agent's response more creative and diverse/random. 
    temperature=0.3,
    # max_tokens----> limits the length of the agent's response.
    max_tokens=500 
)

tutor_agent =Agent(
    # system prompt---> it tells the agent about the role and behavior it should follow
    # for example, you can specify that the agent should act as a personal tutor for a specific subject
    system_prompt ="""
    You are a personal tutor agent for a student who is learning 
    about the strands framework.Your role to provide clear and concise explanation 
    and answer any questions the student may have about the strands framework. 
    You should also provide examples and resources to help the student understand the concepts better.
    """,
    model = bedrock_model, # model to use for the agent
)


#---------Full response-----------------#

# response = tutor_agent("can you explain the first step to learn about the strands framework?")
# print(response)

# #-------------streaming response--------#
# question="can you explain the first step to learn about the strands framework?"


# # Async function that iterates over streamed agent events
# async def process_streaming_response(question):

#     # Get an async iterator for the agent's response stream
#     agent_stream = tutor_agent.stream_async(question)

#     # Process events as they arrive
#     async for event in agent_stream:
#         if "data" in event:
#             # Print text chunks as they're generated
#             print(event["data"], end="", flush=True)

# # Run the agent with the async event processing
# asyncio.run(process_streaming_response(question))


#flush=True tells Python:
#"Don't keep the output in a buffer. Display it immediately."
#What is a buffer?
#When you use print(), Python often stores the output temporarily 
# in memory (a buffer) before showing it on the screen. This reduces the number of write operations and improves performance.



# print(response.metrics.get_summary())
# ----------> This give you a summary of the metrics collected during the agent's 
# execution, such as tool usage, response times, and other relevant information that can help you understand how 
# the agent performed and identify areas for improvement. and you alsoi use thisto debug your agent's behavior and optimize its performance.------>#


# # Print metrics if available
# if hasattr(tutor_agent, "metrics"):
#     print(tutor_agent.metrics.get_summary())


#print(tutor_agent.model.config) #--------->default model use by stands framework 
# is "global.anthropic.claude-sonnet-4-6" but you can change it to any other model 
# available in the strands framework by specifying the model name in the Agent constructor.

#---------------- Without session management----------------#

# tutor_agent1=Agent(
#     model=bedrock_model
# )
# response1= tutor_agent1("I am learning python")

# response2=tutor_agent1("what I was learning")

# print(response2)

#---------with session management-------------#

# Create a session manager with a unique session ID
# session_manager = FileSessionManager(session_id="test-session")


# tutor_agent1=Agent(
#     model=bedrock_model,
#     # Create an agent with the session manager
#     session_manager=session_manager
# )


# # Use the agent - all messages and state are automatically persisted
# response1= tutor_agent1("I am learning python")

# response2=tutor_agent1("what I was learning")

# print(response2)
