#                  Planner
#                     │
#                     ▼
#               Coordinator
#           ┌────────┼────────┐
#           ▼        ▼        ▼
#      Research1 Research2 Research3
#           │        │        │
#           └────────┼────────┘
#                    ▼
#               Aggregator
#                    │
#                    ▼
#                 Critic
#                /      \
#              PASS     FAIL
#              |         |
#              ▼         ▼
#           Writer   Coordinator
#                        │
#                  Research Again

from strands.multiagent import GraphBuilder
from agent.researcher import research_agent1, research_agent2, research_agent3
from agent.planner import planner_agent
from agent.writer import writer_agent
from agent.critic import critic_agent
from agent.coordinator import coordinator_agent
from agent.aggregator import aggregator_agent
from workflows.conditions import get_next_node

# create multiple nodes for researcher agent with parrallel processing
graph_agent = GraphBuilder()
graph_agent.add_node(planner_agent, "planner")
graph_agent.add_node(coordinator_agent, "coordinator")

graph_agent.add_node(research_agent1, "researcher1")
graph_agent.add_node(research_agent2, "researcher2")
graph_agent.add_node(research_agent3, "researcher3")

graph_agent.add_node(aggregator_agent, "aggregator")

graph_agent.add_node(critic_agent, "critic")

# create node for writer agent
graph_agent.add_node(writer_agent,"writer")

# add edges between nodes to define the flow of information
graph_agent.add_edge("planner", "coordinator")
graph_agent.add_edge("coordinator", "researcher1")
graph_agent.add_edge("coordinator", "researcher2")
graph_agent.add_edge("coordinator", "researcher3")
graph_agent.add_edge("researcher1", "aggregator")
graph_agent.add_edge("researcher2", "aggregator")
graph_agent.add_edge("researcher3", "aggregator")
graph_agent.add_edge("aggregator", "critic")

#------------same as the lamda function-----------#
# def check(review, retries):
#     return get_next_node(review, retries) == "writer"


graph_agent.add_edge("critic", "writer", condition=lambda review, retries: get_next_node(review, retries) == "writer")
graph_agent.add_edge("critic", "coordinator", condition=lambda review, retries: get_next_node(review, retries) == "coordinator")


# Set entry points (optional - will be auto-detected if not specified)
graph_agent.set_entry_point("planner")

# Build the graph
graph = graph_agent.build()




