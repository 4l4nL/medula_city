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
    },
    {
        "type": "function",
        "function": {
            "name": "proponer_escritura",
            "description": "Propone escribir un archivo con nuevo contenido. El usuario debe confirmar antes de que se guarde.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ruta": {
                        "type": "string",
                        "description": "Nombre del archivo a modificar, ej: 'player.py'"
                    },
                    "contenido": {
                        "type": "string",
                        "description": "Contenido completo y correcto del archivo"
                    },
                    "descripcion": {
                        "type": "string",
                        "description": "Explicación breve de qué cambios se hicieron y por qué"
                    }
                },
                "required": ["ruta", "contenido", "descripcion"]
            }
        }
    }
]
