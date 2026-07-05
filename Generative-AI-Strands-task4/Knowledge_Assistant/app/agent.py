# app/agent.py
# ------------
# Builds the Knowledge Assistant: a Strands Agent backed by a Bedrock
# Claude model, with retrieve_knowledge (app/tools.py) as its only tool.
# The agentic behavior - deciding when to retrieve, judging sufficiency,
# retrying, citing sources, admitting "not found" - is driven entirely by
# the system prompt in app/config.py.

from strands import Agent
from strands.models import BedrockModel
from .config import AGENT_MODEL_ID, AGENT_TEMPERATURE, AWS_REGION, SYSTEM_PROMPT
from .tools import retrieve_knowledge


def build_agent() -> Agent:

    model = BedrockModel(
        model_id=AGENT_MODEL_ID,
        region_name=AWS_REGION,
        temperature=AGENT_TEMPERATURE,
    )

    agent = Agent(
        model=model,
        tools=[retrieve_knowledge],
        system_prompt=SYSTEM_PROMPT,
    )

    return agent