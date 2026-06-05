import os

# Directorio raiz del proyecto (un nivel arriba de esta carpeta)
PROYECTO = os.path.join(os.path.dirname(__file__), "..", "medula_city")


def leer_archivo(ruta: str) -> str:
    """Lee un archivo del proyecto y devuelve su contenido."""
    ruta_completa = os.path.join(PROYECTO, ruta)
    try:
        with open(ruta_completa, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"ERROR: No existe el archivo '{ruta}'"


def listar_archivos(directorio: str = ".") -> str:
    """Lista todos los archivos .py del proyecto."""
    ruta_completa = os.path.join(PROYECTO, directorio)
    try:
        archivos = [f for f in os.listdir(ruta_completa) if f.endswith(".py")]
        return "\n".join(archivos) if archivos else "No se encontraron archivos .py"
    except FileNotFoundError:
        return f"ERROR: No existe el directorio '{directorio}'"


def escribir_archivo(ruta: str, contenido: str) -> str:
    """Escribe contenido en un archivo del proyecto. Sin confirmación — ya fue aprobado por el usuario en el navegador."""
    ruta_completa = os.path.join(PROYECTO, ruta)
    try:
        with open(ruta_completa, "w", encoding="utf-8") as f:
            f.write(contenido)
        return f"Archivo '{ruta}' guardado correctamente."
    except Exception as e:
        return f"ERROR al escribir '{ruta}': {e}"
