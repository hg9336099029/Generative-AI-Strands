from strands import Agent
from strands.models import BedrockModel
from pydantic import BaseModel 
from typing import List #

# Structured Output----> Structured output means forcing the LLM to return data in a predefined structure instead of arbitrary text.
# Normally LLMs return free-text responses. Applications need predictable JSON that code can safely consume.


bedrock_model=BedrockModel(
    model_id="global.anthropic.claude-sonnet-4-6",
    region_name="us-west-2",
    temperature=0.2,
    # max_tokens----> limits the length of the agent's response.
    max_tokens=1000
)


copilot= Agent(
    system_prompt="""
    You are a helpful Ai Copilot
    """,
    model=bedrock_model
)

response =copilot("can you explain the first step to learn about the strands framework?")

print(response)

