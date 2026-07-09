import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from agent.planner import planner_agent
from agent.coordinator import coordinator_agent
from agent.researcher import (
    research_agent1,
    research_agent2,
    research_agent3,
)
from agent.aggregator import aggregator_agent
from agent.critic import critic_agent
from agent.writer import writer_agent


def extract_text(response):
    if isinstance(response, str):
        return response

    if hasattr(response, "message"):
        message = response.message
        if isinstance(message, dict):
            content = message.get("content")
            if isinstance(content, list) and content:
                first = content[0]
                if isinstance(first, dict) and "text" in first:
                    return first["text"]
            elif isinstance(content, str):
                return content
        elif isinstance(message, str):
            return message

    if hasattr(response, "structured_output") and response.structured_output is not None:
        return str(response.structured_output)

    return str(response)


def extract_confidence(review_text):
    if not isinstance(review_text, str):
        return None
    for line in review_text.splitlines():
        if "confidence score" in line.lower():
            parts = line.split(":", 1)
            if len(parts) == 2:
                try:
                    return float(parts[1].strip())
                except ValueError:
                    return None
    return None


def should_rerun_research(review_text, threshold=80.0):
    confidence = extract_confidence(review_text)
    return confidence is not None and confidence < threshold


def run_planner():

    topic = "what is aws?"

    print("=" * 80)
    print("PLANNER")
    print("=" * 80)

    response = planner_agent(topic)
    text = extract_text(response)

    print(text)

    return text


def run_coordinator(plan):

    print("=" * 80)
    print("COORDINATOR")
    print("=" * 80)

    response = coordinator_agent(plan)
    text = extract_text(response)

    print(text)

    return text


def parse_research_assignments(assignments_text):
    questions = {
        "Researcher 1": [],
        "Researcher 2": [],
        "Researcher 3": [],
    }
    current_researcher = None

    for raw_line in assignments_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("---"):
            continue

        researcher_match = re.match(r"^\**\s*Researcher\s*\d+\s*:\**$", line, re.IGNORECASE)
        if researcher_match:
            cleaned = re.sub(r"\*", "", line).strip()
            current_researcher = cleaned.split(":", 1)[0].strip()
            continue

        if current_researcher:
            question_match = re.match(r"^(?:[-*]|\d+\.)\s*(.*)$", line)
            if question_match:
                question = question_match.group(1).strip()
                if question:
                    questions.setdefault(current_researcher, []).append(question)
                continue

            if questions.get(current_researcher):
                questions[current_researcher][-1] += " " + line

    return questions


def run_researchers(assignments_text=None):
    assignments = parse_research_assignments(assignments_text) if assignments_text else {}

    def build_prompt(researcher_key):
        questions = assignments.get(researcher_key) 
        if len(questions) == 1:
            return questions[0]
        return "Research tasks:\n" + "\n".join(f"- {q}" for q in questions)

    print("=" * 80)
    print("RESEARCHER 1")
    print("=" * 80)
    q1 = build_prompt("Researcher 1")
    r1 = extract_text(research_agent1(q1))
    print(r1)

    print("=" * 80)
    print("RESEARCHER 2")
    print("=" * 80)
    q2 = build_prompt("Researcher 2")
    r2 = extract_text(research_agent2(q2))
    print(r2)

    print("=" * 80)
    print("RESEARCHER 3")
    print("=" * 80)
    q3 = build_prompt("Researcher 3")
    r3 = extract_text(research_agent3(q3))
    print(r3)

    return r1, r2, r3


def run_aggregator(r1, r2, r3):

    print("=" * 80)
    print("AGGREGATOR")
    print("=" * 80)

    combined = f"""

Research 1

{r1}

----------------

Research 2

{r2}

----------------

Research 3

{r3}

"""

    response = aggregator_agent(combined)
    text = extract_text(response)

    print(text)

    return text


def run_critic(research):

    print("=" * 80)
    print("CRITIC")
    print("=" * 80)

    response = critic_agent(research)
    text = extract_text(response)

    print(text)

    return text


def run_writer(research):

    print("=" * 80)
    print("WRITER")
    print("=" * 80)

    response = writer_agent(research)
    text = extract_text(response)
    print(text)
    return text


def main():

    # Planner
    plan = run_planner()
    # Coordinator
    assignments = run_coordinator(plan)
    # Researchers
    r1, r2, r3 = run_researchers(assignments)
    # Aggregator
    combined = run_aggregator(r1, r2, r3)
    # Critic
    try:
        review = run_critic(combined)

    except Exception as error:
        print("CRITIC FAILED:", error)
        review = combined
    
    # Rerun research if critic confidence is too low
    if should_rerun_research(review):
        print("LOW CONFIDENCE DETECTED: re-running research stage")
        r1, r2, r3 = run_researchers()
        combined = run_aggregator(r1, r2, r3)
        review = run_critic(combined)


    # Writer
    report = run_writer(review)

    print("\n")
    print("=" * 80)
    print("FINAL REPORT")
    print("=" * 80)

    print(report)


if __name__ == "__main__":
    main()