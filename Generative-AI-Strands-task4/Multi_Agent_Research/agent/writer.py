from strands import Agent
from prompts import load_prompt
from config import AGENT_MODEL_ID, AGENT_TEMPERATURE, AWS_REGION
from strands.models import BedrockModel

writer_prompt = load_prompt("writer.txt")


# Create specialized agents   
model=BedrockModel(
    model_id=AGENT_MODEL_ID,
    region_name=AWS_REGION,
    temperature=AGENT_TEMPERATURE,
)

writer_agent = Agent(
    model=model,
    system_prompt=writer_prompt 
)
