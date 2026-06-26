from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from pydantic import BaseModel
import json
import openai
import py_compile
import tempfile
import os
from tools import escribir_archivo, leer_archivo, listar_archivos
from tool_definitions import HERRAMIENTAS
from agents.arquitecto import SYSTEM_PROMPT as ARCHITECT_PROMPT
from agents.tester import SYSTEM_PROMPT as TESTER_PROMPT
from agents.anti_alan import SYSTEM_PROMPT as ANTI_ALAN_PROMPT

app = FastAPI()

TOOL_EXECUTORS = {
    "leer_archivo": leer_archivo,
    "listar_archivos": listar_archivos,
}

MODEL = "qwen3.6:latest"

MASTER_PROMPT = f"""You are an AI orchestrator for the Medula City project.
A 2D game in Python + pygame with a Mexican skull character.

Based on the user's message, act as the right specialist:

--- ARCHITECT ---
{ARCHITECT_PROMPT}

--- TESTER ---
{TESTER_PROMPT}

--- ANTI-ALAN ---
{ANTI_ALAN_PROMPT}

Always start your response by stating which role you are taking and why.
Use tools to read files before making any suggestions."""


class ChatRequest(BaseModel):
    mensaje: str
    historial: list = []


class ConfirmarRequest(BaseModel):
    ruta: str
    contenido: str


def validate_syntax(content: str) -> tuple[bool, str]:
    try:
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w",
                                         encoding="utf-8", delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        py_compile.compile(tmp_path, doraise=True)
        os.unlink(tmp_path)
        return True, ""
    except py_compile.PyCompileError as e:
        os.unlink(tmp_path)
        return False, str(e)


def execute_tool(name: str, arguments: dict):
    """Returns (result, is_proposal, proposal_data)"""
    if name == "proponer_escritura":
        return None, True, arguments

    function = TOOL_EXECUTORS.get(name)
    if not function:
        return f"ERROR: tool '{name}' does not exist", False, None
    try:
        return function(**arguments), False, None
    except TypeError as e:
        return f"ERROR: wrong arguments for '{name}': {e}", False, None


@app.get("/", response_class=HTMLResponse)
def index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/confirmar")
def confirmar(req: ConfirmarRequest):
    valid, error = validate_syntax(req.contenido)
    if not valid:
        return JSONResponse({"ok": False, "error": error})
    result = escribir_archivo(req.ruta, req.contenido)
    return JSONResponse({"ok": True, "mensaje": result})


@app.post("/chat")
def chat(req: ChatRequest):
    def generate():
        client = openai.OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",
        )

        messages = [{"role": "system", "content": MASTER_PROMPT}]
        messages += req.historial
        messages.append({"role": "user", "content": req.mensaje})

        while True:
            response = client.chat.completions.create(
                model=MODEL,
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

                    yield f"data: {json.dumps({'tipo': 'herramienta', 'nombre': name})}\n\n"

                    result, is_proposal, data = execute_tool(name, arguments)

                    if is_proposal:
                        yield f"data: {json.dumps({'tipo': 'propuesta', 'datos': data})}\n\n"
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": "Proposal sent to user for confirmation.",
                        })
                    else:
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result,
                        })
            else:
                text = message.content or ""
                for word in text.split(" "):
                    yield f"data: {json.dumps({'tipo': 'texto', 'contenido': word + ' '})}\n\n"

                messages.append({"role": "assistant", "content": text})
                yield f"data: {json.dumps({'tipo': 'fin', 'historial': messages[1:]})}\n\n"
                break

    return StreamingResponse(generate(), media_type="text/event-stream")
