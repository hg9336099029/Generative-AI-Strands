from strands import Agent
from prompts import load_prompt
from config import AGENT_MODEL_ID, AWS_REGION, AGENT_TEMPERATURE
from strands.models import BedrockModel
aggregator_prompt = load_prompt("aggregator.txt")

# Create specialized agents   
model=BedrockModel(
    model_id=AGENT_MODEL_ID,
    region_name=AWS_REGION,
    temperature=AGENT_TEMPERATURE,
)

aggregator_agent = Agent(
    model=model,
    system_prompt=aggregator_prompt
)

