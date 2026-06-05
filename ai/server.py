from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from pydantic import BaseModel
import json
import openai
import py_compile
import tempfile
import os
from tools import leer_archivo, listar_archivos, escribir_archivo
from tool_definitions import HERRAMIENTAS

app = FastAPI()

EJECUTORES = {
    "leer_archivo": leer_archivo,
    "listar_archivos": listar_archivos,
}

SYSTEM_PROMPT = """You are an expert assistant for the Medula City project.
It's a 2D game in Python + pygame where a Mexican skull character moves through a virtual world.
Project files: main.py, game.py, player.py, room.py

You have access to real tools. You MUST use them directly — never write JSON or text describing a tool call.

When you receive a task:
1. Use listar_archivos to see available files
2. Use leer_archivo to read the relevant files
3. Make the necessary changes and use proponer_escritura to propose saving the file

Important rules:
- NEVER guess file contents — always read them first
- NEVER write incomplete files — always include the full file content
- When proposing changes, preserve all existing code and only add/modify what's needed
- Respond in the same language the user writes in"""


class MensajeRequest(BaseModel):
    mensaje: str
    historial: list = []


class ConfirmarRequest(BaseModel):
    ruta: str
    contenido: str


def validar_sintaxis(contenido: str) -> tuple[bool, str]:
    try:
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w",
                                         encoding="utf-8", delete=False) as tmp:
            tmp.write(contenido)
            tmp_path = tmp.name
        py_compile.compile(tmp_path, doraise=True)
        os.unlink(tmp_path)
        return True, ""
    except py_compile.PyCompileError as e:
        os.unlink(tmp_path)
        return False, str(e)


def ejecutar_herramienta(nombre: str, argumentos: dict):
    """Returns (resultado, es_propuesta, datos_propuesta)"""
    if nombre == "proponer_escritura":
        # No guardamos aún — mandamos la propuesta al frontend
        return None, True, argumentos

    funcion = EJECUTORES.get(nombre)
    if not funcion:
        return f"ERROR: herramienta '{nombre}' no existe", False, None
    try:
        return funcion(**argumentos), False, None
    except TypeError as e:
        return f"ERROR: argumentos incorrectos para '{nombre}': {e}", False, None


@app.get("/", response_class=HTMLResponse)
def index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/confirmar")
def confirmar(req: ConfirmarRequest):
    """El usuario confirmó — validamos sintaxis y guardamos el archivo."""
    valido, error = validar_sintaxis(req.contenido)
    if not valido:
        return JSONResponse({"ok": False, "error": error})
    resultado = escribir_archivo(req.ruta, req.contenido)
    return JSONResponse({"ok": True, "mensaje": resultado})


@app.post("/chat")
def chat(req: MensajeRequest):
    def generar():
        cliente = openai.OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",
        )

        mensajes = [{"role": "system", "content": SYSTEM_PROMPT}]
        mensajes += req.historial
        mensajes.append({"role": "user", "content": req.mensaje})

        while True:
            respuesta = cliente.chat.completions.create(
                model="qwen3.6:latest",
                messages=mensajes,
                tools=HERRAMIENTAS,
                tool_choice="auto",
            )

            mensaje = respuesta.choices[0].message

            if mensaje.tool_calls:
                mensajes.append(mensaje)
                for tool_call in mensaje.tool_calls:
                    nombre = tool_call.function.name
                    argumentos = json.loads(tool_call.function.arguments)

                    yield f"data: {json.dumps({'tipo': 'herramienta', 'nombre': nombre})}\n\n"

                    resultado, es_propuesta, datos = ejecutar_herramienta(nombre, argumentos)

                    if es_propuesta:
                        # Mandamos la propuesta al frontend para confirmación
                        yield f"data: {json.dumps({'tipo': 'propuesta', 'datos': datos})}\n\n"
                        # Le decimos al modelo que la propuesta fue enviada al usuario
                        mensajes.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": "Propuesta enviada al usuario para confirmación.",
                        })
                    else:
                        mensajes.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": resultado,
                        })
            else:
                texto = mensaje.content or ""
                for palabra in texto.split(" "):
                    yield f"data: {json.dumps({'tipo': 'texto', 'contenido': palabra + ' '})}\n\n"

                mensajes.append({"role": "assistant", "content": texto})
                yield f"data: {json.dumps({'tipo': 'fin', 'historial': mensajes[1:]})}\n\n"
                break

    return StreamingResponse(generar(), media_type="text/event-stream")
