from flask import Blueprint, request, jsonify
import json
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, List, Dict, Any, Annotated
from app.web.hooks import login_required
from langgraph.graph.message import add_messages


from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools.tavily_search import TavilySearchResults



bp = Blueprint('chatbot', __name__, url_prefix="/api/chatbot")

# System message
system_message = """You are a helpful assistant for a PDF Portfolio application. 
Your primary goal is to help users understand this application's features and how to use it.

About this application:
- It's a PDF Portfolio application that lets users upload and chat with their PDF documents
- The app uses AI to answer questions about PDF content
- The source code is available at: https://github.com/govardhan27/pdf-chat/
- Key features: document upload, AI chat with PDFs, conversation history

When answering technical questions:
1. Focus on the structure and components common in Flask+Svelte applications
2. Describe how the components likely work together
3. Reference typical files and directories that would be in such a project
4. Explain technical concepts in accessible terms

Always provide the GitHub URL when asked about the source code.
Keep responses concise and helpful. Format links in HTML when appropriate.
"""


memory = MemorySaver()

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

tool = TavilySearchResults(max_results=2)
tools = [tool]
from langchain_core.messages import SystemMessage
# Define the LLM
llm = ChatOpenAI(temperature=0)
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    messages = state["messages"]
     # Check if any message is a SystemMessage
    if not any(isinstance(msg, SystemMessage) for msg in messages):
        # Add a SystemMessage at the beginning
        messages = [SystemMessage(content=system_message)] + messages
    
    message = llm_with_tools.invoke(messages)
    return {"messages": [message]}

graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)

# Any time a tool is called, we return to the chatbot to decide the next step
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "1"}}

# @bp.route('/', methods=['POST'])
# @login_required
# def chat():
#     data = request.json
#     user_message = data.get('message', '')
#     history = data.get('history', [])
    
#     # Add system message if this is the first request
#     if not history:
#         history = [{"role": "assistant", "content": "Hi! I can help you with information about this PDF-Chat application. What would you like to know?"}]
    
#     # Add user message
#     history.append({"role": "user", "content": user_message})
    
#     # Run the agent graph
#     events = graph.stream({"messages": history}, config=config, stream_mode="values")
    
#     for event in events:
#         print("event", event["messages"][-1].pretty_print())
#         event["messages"][-1].pretty_print()
    
#     return jsonify({"response": 'hello'})

from flask import Response, stream_with_context

@bp.route('/', methods=['POST'])
@login_required
def chat():
    data = request.json
    user_message = data.get('message', '')
    history = data.get('history', [])
    
    # Add system message if this is the first request
    if not history:
        history = [{"role": "assistant", "content": "Hi! I can help you with information about this PDF-Chat application. What would you like to know?"}]
    
    # Add user message
    history.append({"role": "user", "content": user_message})
    
    def generate():
        # Convert dictionary messages to LangChain message objects if needed
        lang_history = []
        for msg in history:
            if msg["role"] == "user":
                lang_history.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                lang_history.append(AIMessage(content=msg["content"]))
            elif msg["role"] == "system":
                lang_history.append(SystemMessage(content=msg["content"]))
        
        # Run the agent graph
        events = graph.stream({"messages": lang_history}, config=config, stream_mode="values")
        
        # Collect full response
        full_response = ""
        
        # Stream each chunk
        for event in events:
            chunk = event["messages"][-1].content
            if isinstance(chunk, str):
                # For non-streaming responses, we get the full content at once
                full_response = chunk
                yield f"data: {json.dumps({'chunk': chunk, 'full': full_response})}\n\n"
            else:
                # For streaming responses, we get chunks
                chunk_text = chunk.delta if hasattr(chunk, 'delta') else str(chunk)
                full_response += chunk_text
                yield f"data: {json.dumps({'chunk': chunk_text, 'full': full_response})}\n\n"
        
        # Signal completion
        yield f"data: {json.dumps({'done': True, 'full': full_response})}\n\n"
    
    return Response(stream_with_context(generate()), 
                   content_type='text/event-stream')
