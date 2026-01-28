# app.py
import streamlit as st
import uuid
from agent import ask_agent

st.set_page_config(page_title="Bedrock Agent Chat", page_icon="🤖")
st.title("🤖 Bedrock Agent Chat UI")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# show history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask something...")

if user_input:
    # show user
    with st.chat_message("user"):
        st.markdown(user_input)

    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    # call agent
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = ask_agent(
                user_input,
                st.session_state.session_id
            )
            st.markdown(response)

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )
