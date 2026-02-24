import streamlit as st
from langchain_groq import ChatGroq


def get_llm():
    """
    LLM factory. Change ONLY this function when switching from Groq to Claude.

    To switch to Claude:
        1. pip install langchain-anthropic
        2. Add ANTHROPIC_API_KEY to secrets.toml
        3. Replace the body below with:
               from langchain_anthropic import ChatAnthropic
               return ChatAnthropic(
                   model="claude-3-5-sonnet-20241022",
                   api_key=st.secrets["ANTHROPIC_API_KEY"],
               )
    """
    return ChatGroq(
        model="llama3-70b-8192",
        api_key=st.secrets["GROQ_API_KEY"],
        temperature=0.1,
    )
