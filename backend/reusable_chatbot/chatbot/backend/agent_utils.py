"""Agent utility functions for the chatbot."""

from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model


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
