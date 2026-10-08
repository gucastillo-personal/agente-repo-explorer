from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition

from agent_system import SYSTEM
from tools import tools

llm = ChatAnthropic(model="claude-sonnet-5-5", max_tokens=2048).bind_tools(tools)


def call_model(state: MessagesState):
    reply = llm.invoke([SystemMessage(content=SYSTEM)] + state["messages"])
    return {"messages": [reply]}


builder = StateGraph(MessagesState)
builder.add_node("agent", call_model)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")
graph = builder.compile()


def run_agent(question):
    result = graph.invoke(
        {"messages": [("user", question)]},
        {"recursion_limit": 25},
    )
    content = result["messages"][-1].content
    if isinstance(content, list):  # a veces llega como lista de bloques
        content = "".join(b["text"] for b in content if b.get("type") == "text")
    return content


if __name__ == "__main__":
    while True:
        q = input("\nPregunta (enter para salir): ").strip()
        if not q:
            break
        print(run_agent(q))