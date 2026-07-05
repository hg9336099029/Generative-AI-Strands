import os
from bedrock_agentcore.memory import MemoryClient

# This is typically done once, separately from your agent application
client = MemoryClient(region_name="ap-south-1")
comprehensive_memory = client.create_memory_and_wait(
    name="ComprehensiveAgentMemory",
    description="Full-featured memory with all built-in strategies",
    strategies=[
        {
            "summaryMemoryStrategy": {
                "name":"SessionSummarizer",
                "namespaces": ["/summaries/{actorId}/{sessionId}/"]
            }
        },
        {
            "userPreferenceMemoryStrategy": {
                "name":"PreferenceLearner",
                "namespaces": ["/preferences/{actorId}/"]
            }
        },
        {
            "semanticMemoryStrategy": {
                "name":"FactExtractor",
                "namespaces": ["/facts/{actorId}/"]
            }
        }
    ]
)

# Export the LTM memory ID as an environment variable for reuse
ltm_memory_id = comprehensive_memory.get('id')
print(f"Created LTM memory with ID: {ltm_memory_id}")
os.environ['AGENTCORE_LTM_MEMORY_ID'] = ltm_memory_id