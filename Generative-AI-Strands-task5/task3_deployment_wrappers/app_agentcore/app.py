# To run: python app_agentcore.py
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from agent import agent

app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload):
    """
    Standard AgentCore entrypoint. 
    Payload arrives as a dict; response must be a dict [4].
    """
    user_prompt = payload.get("prompt", "")
    result = agent(user_prompt)
    
    # Returns standard JSON response format [6]
    return {"result": result.message, "status": "success"}

if __name__ == "__main__":
    app.run() 

