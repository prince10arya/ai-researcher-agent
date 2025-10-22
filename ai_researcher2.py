from typing_extensions import TypedDict
from typing import Annotated, Literal
import os
from arxiv_tool import *
from read_pdf import *
from write_pdf import *
from ai_researcher import INITIAL_PROMPT, print_stream
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv
# from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import MemorySaver


load_dotenv()
# Step1: Define state
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Step2: Define ToolNode & Tools
tools = [arxiv_search_tool, read_pdf, render_latex_pdf]
tool_node = ToolNode(tools=tools)

# Step3: Setup LLM
# llm = ChatGroq(model="llama-3.3-70b-versatile")
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",api_key=os.getenv("GOOGLE_API_KEY"))
llm = llm.bind_tools(tools)
# Step4:  Setup graph]
def call_model(state: State):
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}

def should_continue(state: State) -> Literal["tools", END]:
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END


workflow = StateGraph(State)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")

checkpointer = MemorySaver()
config = {"configurable": {"thread_id": 1}}

graph = workflow.compile(checkpointer=checkpointer)


# Step5: TESTING
while True:
    user_input = input("User: ")
    if user_input:
        messages = [
            {"role": "system", "content": INITIAL_PROMPT},
            {"role": "user", "content": user_input}
        ]

        input_data = {
            "messages": messages
        }
        print_stream(graph.stream(input_data, config, stream_mode="values"))
