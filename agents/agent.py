from langchain_core.tools import tool
import os
import sys
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from typing import Annotated, Literal, List, Optional
from typing_extensions import TypedDict
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ollama_client import OllamaClient

class UserQuery(BaseModel):
    topic: str  # main subject/domain (e.g., "NBA", "restaurants", "stocks")
    tasks: List[str]  # specific pieces of info requested (e.g., ["scores", "player stats"])
    timeframe: Optional[str] = None  # natural language time (e.g., "last night", "next week")
    location: Optional[str] = None   # if relevant (e.g., "Seattle", "NYC")
    filters: Optional[List[str]] = None  # extra constraints (e.g., ["vegan", "under $20"])
    raw_query: str  # original user query for traceability


class State(TypedDict):
    messages: Annotated[list, add_messages]
    query: UserQuery
    # urls: List[str]
    # results: List[str]


def init_llm():
    return OllamaClient(model="llama3.2")


def build_graph():
    graph_builder = StateGraph(State)

    graph_builder.add_node("handle_user_input", handle_user_input)
    graph_builder.add_node("search_web", search_web)
    # graph_builder.add_node("scrape", scrape)
    # graph_builder.add_node("agentql", agentql)
    # graph_builder.add_node("web_surfer", web_surfer)
    # graph_builder.add_node("summarize", summarize)

    graph_builder.set_entry_point("handle_user_input")
    graph_builder.add_edge("handle_user_input", "search_web")

    graph_builder.add_edge("search_web", END)
    # graph_builder.add_edge("search_web", "scrape")
    # graph_builder.add_edge("scrape", "summarize")
    # graph_builder.add_edge("summarize", END)

    graph = graph_builder.compile()
    return graph

# Nodes ------------------------------------------------------------------------------------
def choose_mode(state: State):
    # choose between supplying URL or searching
    pass

def handle_user_input(state: State):
    last_message = state["messages"][-1]
    
    system_prompt = """You are an intent extraction engine.
Given a user query, extract and return the following fields:

topic: str  # main subject/domain (e.g., "NBA", "restaurants", "stocks")
tasks: List[str]  # specific pieces of info requested (e.g., ["scores", "player stats"])
timeframe: Optional[str] = None  # natural language time (e.g., "last night", "next week")
location: Optional[str] = None   # if relevant (e.g., "Seattle", "NYC")
filters: Optional[List[str]] = None  # extra constraints (e.g., ["vegan", "under $20"])
raw_query: str  # original user query for traceability

Return ONLY valid JSON matching this structure."""

    extracted_query = model.extract_structured(
        last_message.content, 
        UserQuery, 
        system_prompt
    )

    return {"query": extracted_query}

def search_web(state:State):
    return "searched"

def scrape(state:State):
    return "scraped"

def agentql(state: State) -> State:
    return "ql"

def web_surfer(state: State) -> State:
    return "im a surfer"

def summarize(state: State) -> State:
    return "summary to write to DB"
# Tools -------------------------------------------------------------------------------------

# @tool
# def scrape():
#     print("I am scraper")
#     return {"result": "yes"}

model = init_llm()
graph = build_graph()
user_query = input("What can I do for you today?\n")
state = graph.invoke({"messages": [{"role": "user", "content": user_query}]})
print(state["messages"][-1].content)
print(state["query"])