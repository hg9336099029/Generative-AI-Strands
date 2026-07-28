#A plugin is a package that groups multiple related tools and integrations together, 
# enabling an AI agent to perform complex tasks through external services.

from strands import tool

# -------------------------------
# Calculator Tool
# -------------------------------
@tool
def calculator(expression: str) -> str:
    """
    Evaluate a mathematical expression.
    Example:
        5 * 8
    """
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Calculation Error: {e}"


# -------------------------------
# Weather Tool
# -------------------------------
@tool
def weather(city: str) -> str:
    """
    Returns dummy weather information.
    """
    return f"The weather in {city} is 31°C and Sunny."


# -------------------------------
# User Information Tool
# -------------------------------
@tool
def fetch_user(username: str) -> str:
    """
    Fetch user information.
    """
    users = {
        "harsh": "Software Engineer Intern",
        "rahul": "Backend Developer",
        "aman": "ML Engineer"
    }

    return users.get(username.lower(), "User not found")


# -------------------------------
# Plugin Class
# -------------------------------
class UtilityPlugin:
    """
    A plugin groups multiple tools together.
    """

    def get_tools(self):
        return [
            calculator,
            weather,
            fetch_user
        ]