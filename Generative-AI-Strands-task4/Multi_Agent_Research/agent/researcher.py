from strands import Agent
from prompts import load_prompt
from config import AGENT_MODEL_ID, AWS_REGION, AGENT_TEMPERATURE
from strands.models import BedrockModel
from tools.retrieval_tool import retrieve_and_format

researcher_prompt = load_prompt("researcher.txt")

model=BedrockModel(
    model_id=AGENT_MODEL_ID,
    region_name=AWS_REGION,
    temperature=AGENT_TEMPERATURE
)

research_agent1 = Agent(
    model=model,
    system_prompt=researcher_prompt,
    tools=[retrieve_and_format],
)

research_agent2 = Agent(
    model=model,
    system_prompt=researcher_prompt,
    tools=[retrieve_and_format],
)

research_agent3 = Agent(
    model=model,
    system_prompt=researcher_prompt,
    tools=[retrieve_and_format],
)

