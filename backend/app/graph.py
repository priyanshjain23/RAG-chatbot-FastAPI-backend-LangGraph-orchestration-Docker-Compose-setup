from typing import TypedDict, List, Tuple
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver
from app.retrieval import get_query_engine
from app.generation import chat_llm


class ChatState(TypedDict):
    question: str
    needs_retrieval: bool
    answer: str
    history: List[Tuple[str, str]]


def build_history(history: List[Tuple[str, str]]) -> str:
    if not history:
        return ""
    return "\n\n".join(f"User: {u}\nAssistant: {a}" for u, a in history)


def classify_node(state: ChatState) -> ChatState:
    question = state["question"].strip().lower()
    small_talk = {"hi", "hello", "hey", "thanks", "thank you", "bye", "goodbye"}
    state["needs_retrieval"] = question not in small_talk
    return state


def retrieve_node(state: ChatState) -> ChatState:
    history = build_history(state["history"])
    prompt = (
        f"Previous conversation:\n{history}\n\nCurrent question:\n{state['question']}\n\n"
        "Answer the current question using the relevant documents."
        if history
        else state["question"]
    )
    response = get_query_engine().query(prompt)
    state["answer"] = str(response)
    return state


def chat_node(state: ChatState) -> ChatState:
    messages = []
    for user_msg, ai_msg in state["history"]:
        messages.append(("human", user_msg))
        messages.append(("ai", ai_msg))
    messages.append(("human", state["question"]))
    response = chat_llm.invoke(messages)
    state["answer"] = response.content
    return state


def build_graph():
    graph = StateGraph(ChatState)
    graph.add_node("classify", classify_node)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("chat", chat_node)
    graph.set_entry_point("classify")
    graph.add_conditional_edges(
        "classify",
        lambda state: "retrieve" if state["needs_retrieval"] else "chat",
        {"retrieve": "retrieve", "chat": "chat"},
    )
    graph.add_edge("retrieve", END)
    graph.add_edge("chat", END)
    return graph.compile(checkpointer=InMemorySaver())


app_graph = build_graph()
