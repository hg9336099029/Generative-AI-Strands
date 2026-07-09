from strands import Agent
from prompts import load_prompt
from config import AGENT_MODEL_ID, AWS_REGION, AGENT_TEMPERATURE
from strands.models import BedrockModel

coordinator_prompt = load_prompt("coordinator.txt")

# Create specialized agents   
model=BedrockModel(
    model_id=AGENT_MODEL_ID,
    region_name=AWS_REGION,
    temperature=AGENT_TEMPERATURE,
)

coordinator_agent = Agent(
    model=model,
    system_prompt=coordinator_prompt 
)

