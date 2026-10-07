# Agente Repo Explorer

Agente de línea de comandos que explora un repositorio local y responde preguntas sobre su código. Construido desde cero con la API de Claude (sin frameworks) para entender el loop de un agente: el modelo decide qué herramienta usar, el código la ejecuta y el resultado vuelve al modelo hasta que responde.

## Demo

```
Pregunta: ¿Dónde se maneja la autenticación?

-> list_files({'path': '.'})
-> search_text({'query': 'auth'})
-> read_file({'path': 'src/auth/login.py'})

Respuesta: La autenticación se maneja en src/auth/login.py, donde ...
```

> Reemplazá este ejemplo por una traza real de tu agente.

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