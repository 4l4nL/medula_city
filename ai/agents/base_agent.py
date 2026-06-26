import json
import openai
from tools import leer_archivo, listar_archivos
from tool_definitions import HERRAMIENTAS

# Mapa: nombre de herramienta → función real de Python
TOOL_EXECUTORS = {
    "leer_archivo": leer_archivo,
    "listar_archivos": listar_archivos,
}

def execute_tool(name: str, arguments: dict) -> str:
    """Encuentra la función correcta y la ejecuta."""
    funcion = TOOL_EXECUTORS.get(name)
    if not funcion:
        return f"ERROR: tool '{name}'does not exist"
    try:
        return funcion(**arguments)
    except TypeError as e:
        return f"ERROR: wrong arguments for '{name}': {e}"


def run_agent(system_prompt: str, task: str, model: str = "qwen3.6:latest") -> str:
    """Runs any agent given a system prompt and a task, returning the agent's response."""
    client = openai.OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": task},
    ]

    while True:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=HERRAMIENTAS,
            tool_choice="auto",
        )

        message = response.choices[0].message

        if message.tool_calls:
            messages.append(message)
            for tool_call in message.tool_calls:
                name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                result = execute_tool(name, arguments)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })
        else:
            return message.content or ""