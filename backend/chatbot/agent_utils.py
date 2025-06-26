"""Agent utility functions for the chatbot."""

from datetime import datetime
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model


@tool
def get_current_datetime() -> str:
    """Get the current date and time.

    Returns:
        str: Current date and time in a readable format
    """
    now = datetime.now()
    return now.strftime("%A, %B %d, %Y at %I:%M %p")


@tool
def get_current_date() -> str:
    """Get the current date only.

    Returns:
        str: Current date in a readable format
    """
    now = datetime.now()
    return now.strftime("%A, %B %d, %Y")


@tool
def get_current_time() -> str:
    """Get the current time only.

    Returns:
        str: Current time in a readable format
    """
    now = datetime.now()
    return now.strftime("%I:%M %p")


def init_llm(model_name="gpt-4o-mini", provider="openai"):
    """Initialize and return a chat model."""
    return init_chat_model(model_name, model_provider=provider)


def create_agent(llm, tools, prompt):
    """Create a react agent with the given LLM, tools, and prompt."""
    return create_react_agent(llm, tools, prompt=prompt)


def answer_question(agent, question):
    """Answer a question using the agent executor."""
    for step in agent.stream(
        {"messages": [{"role": "user", "content": question}]},
        stream_mode="values",
    ):
        step["messages"][-1].pretty_print()
