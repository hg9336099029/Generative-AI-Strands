import asyncio
from strands import Agent
from strands.tools import tool
from strands_tools import file_read, file_write
from strands.session.file_session_manager import FileSessionManager
from strands.models import BedrockModel
#----------------- CUSTOM TOOL-------------------#

@tool
def count_lines(content: str) -> str:
    """
    Count the number of lines in a file.
    """
    return f"Total lines in file: {len(content.splitlines())}"


# ----------------BASIC COPILOT AGENT------------------#


bedrock_model = BedrockModel(
    model_id="global.anthropic.claude-sonnet-4-6",
    region_name="us-west-2",
    # temperature controls the randomness of the agent's responses. 
    # A lower temperature-------> will make the agent's responses more acurate and focused
    # higher temperature ------>will make agent's response more creative and diverse/random. 
    temperature=0.2,
    # max_tokens----> limits the length of the agent's response.
    max_tokens=1000 
)

session_manager = FileSessionManager(session_id="test-session")

copilotx = Agent(
    system_prompt="""
    You are a Basic Coding Copilot.

    Your responsibilities:
    1. Read source code files.
    2. Identify bugs and coding issues.
    3. Explain the issues clearly.
    4. Generate corrected code.
    5. Write corrected code into a new file.
    6. Never overwrite the original file.
    7. Save corrected code as fixed_<filename>.
    """,
    # Create an agent with the session manager
    session_manager=session_manager,

    tools=[
        file_read,
        file_write,
        count_lines
    ],
    model = bedrock_model # model to use for the agent
)


#----------- STREAMING FUNCTION -----------------#

async def process_streaming_response(question):

    stream = copilotx.stream_async(question)

    async for event in stream:

        if "data" in event:
            print(event["data"], end="", flush=True)

    print("\n")

# -----------------MAIN PROGRAM---------------------#


while True:

    file_path = input(
        "\nEnter Python file path (or type exit): "
    )

    if file_path.lower() == "exit":
        print("\nExiting Copilot Agent...")
        break

    prompt = f"""
    Read the Python file located at:
    {file_path}
    Perform the following tasks:

    1. Read the file contents.
    2. Count total lines using the count_lines tool.
    3. Analyze the code.
    4. Identify bugs, syntax errors, logical errors,
       bad practices, or possible improvements.
    5. Generate corrected code.
    6. Write corrected code into a new file named:
       fixed_{file_path}
    7. Explain:
       - What problems were found
       - Why they occurred
       - What fixes were applied
    """

    asyncio.run(
        process_streaming_response(prompt)
    )

print("\nThank you for using the Basic Copilot Agent.")