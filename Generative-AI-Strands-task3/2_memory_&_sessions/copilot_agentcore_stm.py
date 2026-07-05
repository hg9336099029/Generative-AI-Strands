import os
import asyncio
from datetime import datetime
from strands import Agent
from strands.tools import tool 
from strands.models import BedrockModel
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig, RetrievalConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager

# Provide the Memory ID (Created via AWS Console or setup script)
MEM_ID = os.environ.get("AGENTCORE_MEMORY_ID", "your-memory-id")
ACTOR_ID = "test_actor_id"
SESSION_ID = "test_session_id"

# Configure Retrieval Behavior to learn user preferences
user_prefs_retrieval = RetrievalConfig(
    top_k=10,
    relevance_score=0.2,
    strategy_id="userPreferenceMemoryStrategy" 
)

# Add the retrieval_config to your AgentCoreMemoryConfig
agent_core_config = AgentCoreMemoryConfig(
    memory_id=MEM_ID,
    actor_id=ACTOR_ID,
    session_id=SESSION_ID,
    # Namespaces must start and end with a forward slash
    retrieval_config={
        "/preferences/{actorId}/": user_prefs_retrieval
    }
)

bedrock_model = BedrockModel(
    model_id="global.anthropic.claude-sonnet-4-6",
    region_name="us-west-2",
    temperature=0.2,
    max_tokens=1000 
)

# Use a Context Manager (with block) to safely handle the session and prevent data loss
with AgentCoreMemorySessionManager(agent_core_config) as session_manager:

    copilot = Agent(
        system_prompt="""
        You are a helpful assistant that can answer questions 
        about a person based on the information provided in the 
        PersonInfo model. You also remember the user's choices 
        from previous interactions.
        """,
        session_manager=session_manager,
        model=bedrock_model,
        callback_handler=None
    )

    
    # The agent will learn this preference (LTM) and remember it for this session (STM)
    print("\nUser: I like sushi with tuna")
    response_1 = copilot("I like sushi with tuna")
    print(f"Agent: {response_1}")

    # The agent will recall the preference stored in memory to answer the question
    print("\nUser: What should I buy for lunch today?")
    response_2 = copilot("What should I buy for lunch today?")
    print(f"Agent: {response_2}")