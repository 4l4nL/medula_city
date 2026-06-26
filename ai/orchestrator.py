"""Orchestrator to route user tasks to specialist agents."""

import openai
from agents import arquitecto as arquitecto_mod, tester as tester_mod, anti_alan as anti_alan_mod, base_agent as base_agent_mod

# Safely get prompts and runner; fall back to sensible defaults if names differ.
ARCHITECT_PROMPT = getattr(arquitecto_mod, "SYSTEM_PROMPT", "")
TESTER_PROMPT = getattr(tester_mod, "SYSTEM_PROMPT", "")
ANTI_ALAN_PROMPT = getattr(anti_alan_mod, "SYSTEM_PROMPT", "")
run_agent = getattr(base_agent_mod, "run_agent", None)

MODEL = "qwen3.6:latest"

ROUTING_PROMPT = """You are an orchestrator for medula city.
Your job is to read the user's message and decide which specialist agent should handle it.

Reply with ONLY one of these words:
-architect -> user wants to plan, design, or understand how to implement something.
-tester -> user wants to review code, find bug, or check if something is correct.
-anti_alan -> user wants to add many features, seems to be over-engineering, or losing focus
-general -> anything else

Reply with the single word only. No explanation."""

def route(task: str) -> str:
    """Ask the LLM which agent should handle this task."""
    client = openai.OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": ROUTING_PROMPT},
            {"role": "user", "content": task},
        ],
    )

    # Defensive access in case the client response shape differs
    try:
        return response.choices[0].message.content.strip().lower()
    except Exception:
        # fallback to a default route
        return "general"

AGENTS = {
    "architect": ARCHITECT_PROMPT,
    "tester": TESTER_PROMPT,
    "anti_alan": ANTI_ALAN_PROMPT,
    "general": ARCHITECT_PROMPT,
}

AGENT_LABELS = {
    "architect": "🏛️ Architect",
    "tester": "🧪 Tester",
    "anti_alan": "🛑 Anti-Alan",
    "general": "🤖 General",
}

def orchestrate(task: str) -> str:
    """Main entry point. Routes the task to the right agent and returns the response."""
    agent = route(task)

    if agent not in AGENTS:
        agent = "general"

    print(f"\n{AGENT_LABELS[agent]} is handling this task\n")
    print("_" * 50)

    system_prompt = AGENTS[agent]

    if run_agent is None:
        return "run_agent not available"

    return run_agent(system_prompt, task, MODEL)
