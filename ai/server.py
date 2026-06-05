from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
import openai
from tools import leer_archivo, listar_archivos
from tool_definitions import HERRAMIENTAS

app = FastAPI()

EJECUTORES = {
    "leer_archivo": leer_archivo,
    "listar_archivos": listar_archivos,
}

SYSTEM_PROMPT = """Eres un asistente experto en el proyecto Medula City.
Es un juego 2D en Python + pygame donde una calaverita mexicana se mueve por un mundo virtual.
Archivos del proyecto: main.py, game.py, player.py, room.py

Tienes acceso a herramientas reales. DEBES usarlas directamente — nunca escribas JSON ni texto describiendo una llamada.

Cuando recibas una tarea:
1. Usa la herramienta listar_archivos para ver los archivos disponibles
2. Usa la herramienta leer_archivo para leer los archivos relevantes
3. Analiza el código y explica qué cambios se necesitan con fragmentos de código concretos

Reglas importantes:
- NUNCA escribas JSON como respuesta — usa las herramientas directamente
- NUNCA adivines el contenido de un archivo — siempre léelo primero
- Tu rol es leer, analizar y sugerir — no modificas archivos
- Responde en español"""


class MensajeRequest(BaseModel):
    mensaje: str
    historial: list = []


def ejecutar_herramienta(nombre: str, argumentos: dict) -> str:
    funcion = EJECUTORES.get(nombre)
    if not funcion:
        return f"ERROR: herramienta '{nombre}' no existe"
    try:
        return funcion(**argumentos)
    except TypeError as e:
        return f"ERROR: argumentos incorrectos para '{nombre}': {e}"


@app.get("/", response_class=HTMLResponse)
def index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()


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

        # Loop ReAct
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

                    # Notificar al frontend qué herramienta se está usando
                    yield f"data: {json.dumps({'tipo': 'herramienta', 'nombre': nombre})}\n\n"

                    resultado = ejecutar_herramienta(nombre, argumentos)
                    mensajes.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": resultado,
                    })
            else:
                texto = mensaje.content or ""
                # Enviar la respuesta palabra por palabra
                for palabra in texto.split(" "):
                    yield f"data: {json.dumps({'tipo': 'texto', 'contenido': palabra + ' '})}\n\n"

                # Enviar historial actualizado al final
                mensajes.append({"role": "assistant", "content": texto})
                yield f"data: {json.dumps({'tipo': 'fin', 'historial': mensajes[1:]})}\n\n"
                break

    return StreamingResponse(generar(), media_type="text/event-stream")
