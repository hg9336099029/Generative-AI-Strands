import os
from datetime import datetime
from strands.models import BedrockModel
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig, RetrievalConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager
from strands import Agent

MEM_ID = os.environ.get("AGENTCORE_LTM_MEMORY_ID", "ComprehensiveAgentMemory-2klCIx99PZ")
ACTOR_ID = "test_actor_id"
SESSION_ID = "test_session_id-7"

config = AgentCoreMemoryConfig(

    memory_id=MEM_ID,
    session_id=SESSION_ID,
    actor_id=ACTOR_ID,
    batch_size=10,  
    
    # retrieval_config (Optional): A dictionary that maps hierarchical namespaces to specific 
    # retrieval rules and memory strategies. 
    retrieval_config={
        
        # NAMESPACE 1: User Preferences
        # Namespaces must start and end with a forward slash (/)  
        # The `{actorId}` placeholder is automatically replaced at runtime by your ACTOR_ID.
        "/preferences/{actorId}/": RetrievalConfig(
            # top_k: Returns up to the top 5 most relevant preference records.
            top_k=5,
            # relevance_score: The minimum semantic match threshold (0.0 to 1.0). 
            # 0.2 is the default. Setting it low ensures the agent can easily find the match.
            relevance_score=0.2, 
            # strategy_id: Tells the database to actively learn and store user preferences 
            # across sessions in this specific namespace.
            strategy_id="prefere_id"  
        ),
        
        # NAMESPACE 2: Factual Knowledge
        "/facts/{actorId}/": RetrievalConfig(
            # top_k: Returns up to 10 factual records.
            top_k=10,
            # relevance_score: Requires a slightly higher semantic match (0.3) to retrieve facts .
            relevance_score=0.3,
            # strategy_id: Tells the database to extract and store durable, factual information 
            # learned during the conversation.
            strategy_id="FactExtractor_id"    
        ),
        
        # NAMESPACE 3: Session Summaries
        # Notice this namespace uses BOTH {actorId} and {sessionId} because summaries are 
        # scoped to a specific conversation [4].
        "/summaries/{actorId}/{sessionId}/": RetrievalConfig(
            # top_k: Returns up to 5 summary records.
            top_k=5,
            # relevance_score: Requires a 0.5 match threshold.
            relevance_score=0.5,
            # strategy_id: Automatically generates and stores summaries of the conversation 
            # sessions for efficient context retrieval later.
            strategy_id="SessionSummarizer_id"    
        ),

        "/episodic/{actorId}/{sessionId}/": RetrievalConfig(
            # top_k: Returns up to 5 summary records.
            top_k=5,
            # relevance_score: Requires a 0.5 match threshold.
            relevance_score=0.5,
            # strategy_id: Automatically generates and stores summaries of the conversation 
            # sessions for efficient context retrieval later.
            strategy_id="episodic_id"    
        ),
    }
)

bedrock_model = BedrockModel(
    model_id="global.anthropic.claude-sonnet-4-6",
    region_name="ap-south-1",
    temperature=0.2,
    max_tokens=1000 
)

# Removed the redundant try/finally block. The 'with' block flushes the batch_size automatically.
with AgentCoreMemorySessionManager(config, region_name="ap-south-1") as session_manager:

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

    # #Run this FIRST to teach the agent
    # print("\nUser: I like sushi with tuna")
    # response_1 = copilot("I like sushi with tuna")
    # print(f"Agent: {response_1}")

    # 2. You can test recall right away, or in a new session later
    print("\nUser: You know what i like?")
    response_2 = copilot("You know what i like?")
    print(f"Agent: {response_2}")