from openai import OpenAI
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

def get_openai_client():
    api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

    if not api_key:
        st.error("OPENAI_API_KEY not found.")
        st.stop()

    return OpenAI(api_key=api_key)