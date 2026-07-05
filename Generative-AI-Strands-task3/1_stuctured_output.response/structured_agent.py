# Input Text
#       │
#       ▼
# Agent.invoke_async()
#       │
#       ▼
# LLM reads text
#       │
#       ▼
# Extract fields according to PersonInfo schema
#       │
#       ▼
# Validate using Pydantic
#       │
#       ▼
# Create PersonInfo object
#       │
#       ▼
# Return result

import asyncio
from strands import Agent
from strands.tools import tool
from pydantic import BaseModel ,Field
from strands.models import BedrockModel
from pydantic import ValidationError
from strands.types.exceptions import StructuredOutputException


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

#--------- schema for PersonInfo model -----#
class PersonInfo(BaseModel):

    """Model that contains information about a Person"""
    name: str = Field(..., description="The name of the person")
    age: int = Field(..., description="The age of the person")
    email: str = Field(..., description="The email address of the person")
    occupation: str =Field(..., description="The occupation of the person")
    address: dict = Field(..., description="The address of the person")



copilot = Agent(
    system_prompt="""
    You are a helpful assistant that can answer questions 
    about a person based on the information provided in the 
    PersonInfo model.you will be given a PersonInfo object, 
    and you should use the information in that object to answer 
    questions about the person.
    """,
    model=bedrock_model
)

#------------Normal response from the agent without asynchronous call.-----------------#

# response = copilot(
#     """John Smith is a 30 year-old software engineer.
#     his email address is john.smith@example.com. 
#     Can you tell me more about him ?""",

#     #-----pass the PersonInfo model to the agent so that it can use it to answer questions about the person.
#     structured_output_model=PersonInfo
# )


#------ validation of the response to ensure it conforms to the PersonInfo model.--------#

try:
    #------------Asynchronous response from the agent with asynchronous call.-----------------#
    response= asyncio.run(
        copilot.invoke_async(
            """John Smith is a 30 year-old software engineer.
            his email address is john.smith@example.com. 
            Can you tell me more about him ? adress is 123 Main St, Anytown, USA""",
            #-----pass the PersonInfo model to the agent so that it can use it to answer questions about the person.
            structured_output_model=PersonInfo
            )
    )
    #------------Access the `structured_output` from the result-----------#
    
    person_info: PersonInfo = response.structured_output
    print(f"Structured output: {person_info}")
    print(f"name: {person_info.name}")
    print(f"age: {person_info.age}")
    print(f"email: {person_info.email}")
    print(f"occupation: {person_info.occupation}")
    print(f"address: {person_info.address}")
except ValidationError as e:
    print(f"Structured output failed: {e}")
finally:
    print("Agent invocation completed.")



