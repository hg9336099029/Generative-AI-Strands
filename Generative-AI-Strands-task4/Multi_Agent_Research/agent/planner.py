from strands import Agent
from prompts import load_prompt
from config import AGENT_MODEL_ID, AWS_REGION, AGENT_TEMPERATURE
from strands.models import BedrockModel

planner_prompt = load_prompt("planner.txt")

# Create specialized agents   
model=BedrockModel(
    model_id=AGENT_MODEL_ID,
    region_name=AWS_REGION,
    temperature=AGENT_TEMPERATURE,
)

planner_agent = Agent(
    model=model,
    system_prompt=planner_prompt 
)

 

