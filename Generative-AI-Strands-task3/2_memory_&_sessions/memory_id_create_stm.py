import os
from bedrock_agentcore.memory import MemoryClient

# This is typically done once, separately from your agent application
client = MemoryClient(region_name="ap-south-1")
basic_memory = client.create_memory(
    name="BasicTestMemory",
    description="Basic memory for testing short-term functionality"
)

# Export the memory ID as an environment variable for reuse
memory_id = basic_memory.get('id')
print(f"Created memory with ID: {memory_id}")
os.environ['AGENTCORE_MEMORY_ID'] = memory_id