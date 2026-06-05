HERRAMIENTAS = [
    {
        "type": "function",
        "function": {
            "name": "leer_archivo",
            "description": "Lee el contenido de un archivo del proyecto Medula City.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ruta": {
                        "type": "string",
                        "description": "Nombre del archivo a leer, ej: 'player.py'"
                    }
                },
                "required": ["ruta"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "listar_archivos",
            "description": "Lista todos los archivos .py disponibles en el proyecto.",
            "parameters": {
                "type": "object",
                "properties": {
                    "directorio": {
                        "type": "string",
                        "description": "Directorio a listar. Usa '.' para el directorio actual.",
                    }
                },
                "required": []
            }
        }
    }
]
