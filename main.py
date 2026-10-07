import os
import sys
import anthropic

client = anthropic.Anthropic()  # lee ANTHROPIC_API_KEY del entorno
MODEL = "claude-sonnet-5-5"
MAX_ITERATIONS = 10
MAX_FILE_CHARS = 20_000
MAX_SEARCH_RESULTS = 50
SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__"}
ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")

SYSTEM = (
    "Eres un asistente que explora un repositorio de código para responder "
    "preguntas. Empieza listando archivos, usa search_text para ubicar código "
    "y read_file para leer solo lo necesario. Responde de forma concisa y "
    "menciona los archivos que consultaste."
)

PATH_SCHEMA = {"type": "object",
               "properties": {"path": {"type": "string"}},
               "required": ["path"]}

tools = [
    {"name": "list_files",
     "description": "Lista archivos de un directorio (ruta relativa al repo)",
     "input_schema": PATH_SCHEMA},
    {"name": "read_file",
     "description": "Lee el contenido de un archivo (ruta relativa al repo)",
     "input_schema": PATH_SCHEMA},
    {"name": "search_text",
     "description": "Busca un texto en todos los archivos del repo",
     "input_schema": {"type": "object",
                      "properties": {"query": {"type": "string"}},
                      "required": ["query"]}},
]


def safe_path(path):
    full = os.path.abspath(os.path.join(ROOT, path))
    if os.path.commonpath([ROOT, full]) != ROOT:
        raise ValueError("Ruta fuera del repositorio")
    return full


def list_files(path):
    return "\n".join(sorted(os.listdir(safe_path(path))))


def read_file(path):
    with open(safe_path(path), "r", encoding="utf-8", errors="replace") as f:
        content = f.read(MAX_FILE_CHARS + 1)
    if len(content) > MAX_FILE_CHARS:
        content = content[:MAX_FILE_CHARS] + "\n...[archivo truncado]"
    return content


def search_text(query):
    results = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            file_path = os.path.join(dirpath, name)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for n, line in enumerate(f, 1):
                        if query in line:
                            rel = os.path.relpath(file_path, ROOT)
                            results.append(f"{rel}:{n}: {line.strip()}")
                            if len(results) >= MAX_SEARCH_RESULTS:
                                return "\n".join(results)
            except (UnicodeDecodeError, OSError):
                continue  # binarios o ilegibles
    return "\n".join(results) or "Sin resultados"


def run_tool(name, args):
    """Devuelve (contenido, es_error)."""
    try:
        if name == "list_files":
            return list_files(args["path"]), False
        if name == "read_file":
            return read_file(args["path"]), False
        if name == "search_text":
            return search_text(args["query"]), False
        return f"Herramienta desconocida: {name}", True
    except Exception as e:
        return f"Error: {e}", True


def run_agent(question):
    messages = [{"role": "user", "content": question}]
    for _ in range(MAX_ITERATIONS):
        resp = client.messages.create(
            model=MODEL, max_tokens=1024, system=SYSTEM,
            tools=tools, messages=messages)
        messages.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason != "tool_use":
            return "".join(b.text for b in resp.content if b.type == "text")
        results = []
        for b in resp.content:
            if b.type == "tool_use":
                content, is_error = run_tool(b.name, b.input)
                results.append({"type": "tool_result", "tool_use_id": b.id,
                                "content": content, "is_error": is_error})
        messages.append({"role": "user", "content": results})
    return "Se alcanzó el límite de iteraciones sin una respuesta final."


if __name__ == "__main__":
    print(f"Explorando: {ROOT}")
    while True:
        q = input("\nPregunta (enter para salir): ").strip()
        if not q:
            break
        print(run_agent(q))