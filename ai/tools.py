import os
import py_compile
import tempfile

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


def _validar_sintaxis(contenido: str) -> tuple[bool, str]:
    """
    Verifica que el contenido sea Python válido.
    Devuelve (True, "") si es válido, o (False, mensaje_error) si no.
    """
    try:
        # Escribe en un archivo temporal para compilar sin tocar el proyecto
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


def escribir_archivo(ruta: str, contenido: str) -> str:
    """
    Escribe contenido en un archivo del proyecto.
    Primero valida la sintaxis y luego pide confirmación al usuario.
    """
    # Paso 1: validar sintaxis antes de tocar cualquier archivo
    valido, error = _validar_sintaxis(contenido)
    if not valido:
        return (
            f"ERROR DE SINTAXIS en el código para '{ruta}':\n{error}\n"
            f"El archivo NO fue modificado. Corrige el código e intenta de nuevo."
        )

    # Paso 2: mostrar el código al usuario y pedir confirmación
    print(f"\n{'='*50}")
    print(f"📝 El orquestador quiere guardar: {ruta}")
    print(f"{'='*50}")
    print(contenido)
    print(f"{'='*50}")

    confirmacion = input(f"\n¿Confirmas guardar '{ruta}'? (s/n): ").strip().lower()

    if confirmacion != "s":
        return f"Guardado cancelado por el usuario. El archivo '{ruta}' no fue modificado."

    # Paso 3: guardar el archivo
    ruta_completa = os.path.join(PROYECTO, ruta)
    try:
        with open(ruta_completa, "w", encoding="utf-8") as f:
            f.write(contenido)
        return f"Archivo '{ruta}' guardado correctamente."
    except Exception as e:
        return f"ERROR al escribir '{ruta}': {e}"
