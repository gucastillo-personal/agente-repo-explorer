from langchain_core.tools import tool
from agent_manual import list_files, read_file, search_text


@tool(description="Lista los archivos de un directorio del repositorio.")
def list_files_tool(path: str):
    """Devuelve los nombres de los archivos y carpetas de una ruta."""
    return list_files(path)


@tool(description="Lee el contenido de un archivo del repositorio.")
def read_file_tool(path: str):
    """Devuelve el contenido de un archivo, con un límite de caracteres."""
    return read_file(path)


@tool(description="Busca un texto dentro de los archivos del repositorio.")
def search_text_tool(query: str):
    """Devuelve las líneas que contienen el texto solicitado."""
    return search_text(query)


tools = [list_files_tool, read_file_tool, search_text_tool]