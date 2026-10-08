# Agente Repo Explorer

Agente de línea de comandos que explora un repositorio local y responde preguntas sobre su código. Construido desde cero con la API de Claude (sin frameworks) para entender el loop de un agente: el modelo decide qué herramienta usar, el código la ejecuta y el resultado vuelve al modelo hasta que responde.

## Ejecutar y observar el flujo en VS Code

1. Abre [main.py](main.py) y marca un punto de parada en `run_agent()` o en la llamada a `client.messages.create()`.
2. En el menú **Run and Debug**, selecciona **Depurar agente-repo-explorer** y pulsa el botón de ejecución.
3. En la terminal integrada, escribe la siguiente pregunta:

```text
Pregunta (enter para salir): ¿qué hace este proyecto?
```

El programa debe mostrar una respuesta del agente. Si el modelo solicita una herramienta, VS Code debe mostrar el valor de `tool_use`, la ejecución de `run_tool()` y el resultado que se devuelve al modelo.

> La sección de demo siguiente contiene una salida ilustrativa. El comportamiento real depende de la respuesta de Claude, de la clave API y del repositorio que se está explorando.

## Demo

```
Pregunta: ¿qué hace este proyecto?

-> list_files({'path': '.'})
-> search_text({'query': 'auth'})
-> read_file({'path': 'src/auth/login.py'})

```

```
Respueta: 

Este proyecto es **Agente Repo Explorer**, un agente de línea de comandos en Python queresponde preguntas sobre el código de un repositorio local. Está construido directamente sobre la API de Claude, sin frameworks. Su propósito es didáctico: mostrar cómo funciona el loop de un agente.

**Cómo funciona**
- Se ejecuta con `python main.py /ruta/al/repo`. Abre un prompt interactivo, y una línea vacía lo cierra.
- Para cada pregunta, `run_agent()` envía la conversación a Claude junto con tres herramientas:
  - `list_files` lista un directorio.
  - `read_file` lee un archivo, truncado a 20.000 caracteres.
  - `search_text` busca texto literal, con un máximo de 50 resultados.
- Mientras la respuesta tenga `stop_reason == "tool_use"`, el código ejecuta las herramientas y devuelve los resultados al modelo. Cuando el modelo responde con texto, esa es la respuesta final.

**Seguridad y límites**
- `safe_path` impide acceder a rutas fuera del repo explorado.
- Los errores de las herramientas se devuelven al modelo con `is_error`.
- `MAX_ITERATIONS = 10` evita loops infinitos.
- `search_text` ignora `.git`, `.venv`, `node_modules` y `__pycache__`.
- El agente solo lee, no modifica archivos.

**Discrepancias entre el README y el código**
- El README muestra en la demo líneas `-> list_files(...)`, pero `main.py` no imprime las llamadas a herramientas.
- `.env.example` define `ANTHROPIC_API_KEY`, pero el código no carga archivos `.env`. La variable tiene que estar exportada en el entorno.
- `MODEL = "claude-sonnet-5-5"` conviene revisarlo, porque podría no ser un identificador de modelo válido.

Archivos consultados: `README.md`, `main.py`, `.env.example`.
```

## Cómo funciona

```
Pregunta -> Claude -> ¿pide herramienta? -- sí --> tu código la ejecuta
              ^                                          |
              |______________ tool_result _______________|
                         no -> respuesta final
```

- **Loop:** se repite mientras `stop_reason == "tool_use"`. Cuando el modelo responde con texto, termina.
- **Memoria:** la API no guarda estado, así que el historial completo de `messages` se envía en cada vuelta.
- **Herramientas:** las ejecuta el código, no el modelo. Eso permite controlar permisos y límites.

### Herramientas

| Herramienta | Qué hace |
|---|---|
| `list_files` | Lista el contenido de un directorio del repo |
| `read_file` | Lee un archivo (truncado a 20.000 caracteres) |
| `search_text` | Busca texto en todo el repo (máx. 50 resultados) |

### Decisiones de diseño y seguridad

- Las rutas se restringen al repo explorado, así que el agente no puede leer archivos fuera de él.
- Los errores de las herramientas se devuelven al modelo con `is_error` para que pueda corregirse.
- Límite de iteraciones (`MAX_ITERATIONS`) para evitar loops infinitos.
- Se ignoran carpetas como `.git`, `node_modules` y `.venv`.

## Requisitos

- Python 3.10+
- Una API key de Anthropic

## Instalación y uso

```bash
git clone https://github.com/gucastillo-personal/agente-repo-explorer.git
cd agente-repo-explorer
python -m venv .venv && source .venv/bin/activate
pip install anthropic
export ANTHROPIC_API_KEY="tu_key"
python main.py /ruta/al/repo/a/explorar
```

El programa abre un menú interactivo. Introduce una pregunta y escribe Enter para salir.

## Documentación

- [Agente manual y LangGraph](docs/agente-manual-vs-langgraph.md): explica cómo se implementó el mismo agente con ambos enfoques y muestra el diagrama Mermaid del grafo.
- [Generador del diagrama Mermaid](draw_graph_marmaid.py): imprime el grafo actual con `graph.get_graph().draw_mermaid()`.

## Limitaciones conocidas

- `search_text` busca texto literal, no entiende sinónimos ni semántica.
- Solo lectura: no modifica archivos.
- Sin evaluación automática todavía.

## Próximos pasos

- [ ] Conjunto de preguntas de prueba con respuestas esperadas (evals)
- [ ] Búsqueda más tolerante (insensible a mayúsculas, regex)
- [ ] Herramienta `tree` para ver la estructura completa de una vez
- [ ] Reimplementación con LangGraph para comparar

## Aprendizajes

Proyecto de la Clase 1 de mi plan de estudio de IA agéntica. Compara workflows (pasos definidos por código) con agentes (el modelo decide los pasos) y aplica el principio de empezar simple.