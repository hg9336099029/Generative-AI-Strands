from pathlib import Path

PROMPT_DIR = Path(__file__).parent

def load_prompt(filename: str) -> str:
    with open(PROMPT_DIR / filename, "r", encoding="utf-8") as file:
        return file.read()