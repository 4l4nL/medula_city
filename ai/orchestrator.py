import json
import openai
from tools import leer_archivo, listar_archivos
from tool_definitions import HERRAMIENTAS

# Mapa: nombre de herramienta → función real de Python
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


def ejecutar_herramienta(nombre: str, argumentos: dict) -> str:
    """Encuentra la función correcta y la ejecuta."""
    funcion = EJECUTORES.get(nombre)
    if not funcion:
        return f"ERROR: herramienta '{nombre}' no existe"
    try:
        return funcion(**argumentos)
    except TypeError as e:
        return f"ERROR: argumentos incorrectos para '{nombre}': {e}"


def orquestar(tarea: str) -> str:
    """
    El orquestador principal.
    Recibe una tarea en lenguaje natural y coordina herramientas hasta completarla.
    """
    cliente = openai.OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",  # Ollama no necesita key real, pero el campo es obligatorio
    )

    mensajes = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": tarea},
    ]

    print(f"\n🎯 Tarea: {tarea}\n")
    print("─" * 50)

    # El loop ReAct — repite hasta que el modelo decida que terminó
    while True:
        respuesta = cliente.chat.completions.create(
            model="qwen3.6:latest",
            messages=mensajes,
            tools=HERRAMIENTAS,
            tool_choice="auto",
        )

        mensaje = respuesta.choices[0].message

        # ¿El modelo quiere usar una herramienta?
        if mensaje.tool_calls:
            # Agregamos la respuesta del modelo al historial
            mensajes.append(mensaje)

            for tool_call in mensaje.tool_calls:
                nombre = tool_call.function.name
                argumentos = json.loads(tool_call.function.arguments)

                print(f"🔧 Usando: {nombre}({argumentos})")

                resultado = ejecutar_herramienta(nombre, argumentos)

                # Preview del resultado en consola (máx 120 caracteres)
                preview = resultado[:120].replace("\n", " ")
                print(f"   → {preview}...\n")

                # Agregamos el resultado al historial para que el modelo lo lea
                mensajes.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": resultado,
                })

        # ¿El modelo ya terminó?
        else:
            respuesta_final = mensaje.content or ""
            print("✅ Tarea completada:\n")
            print(respuesta_final)
            return respuesta_final
