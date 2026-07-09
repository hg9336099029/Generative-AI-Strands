from workflows.graph import graph

def run_research_team(topic: str):
    
    build_graph = graph()
    result = build_graph(topic)
    return result

def get_final_brief(result) -> str:
    """Extract the Writer's final Markdown brief as plain text."""
    writer_result = result.results.get("writer")

    if not writer_result:
        return "no brief generated -- graph did not reach the writer node"
    return str(writer_result.result)