import streamlit as st
from agents.coordinator import coordinator

st.set_page_config(page_title="Multi-Agent System using Databricks Genie", page_icon="🤖", layout="centered")

st.title("🤖 Multi-Agent System using Databricks Genie")
st.caption("Ask questions about Sales and Customers using Databricks Genies.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hello! How can I help you with your data today?"}
    ]

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Enter your question here..."):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            try:
                response = coordinator(prompt)
                st.markdown(response)
            except Exception as e:
                response = f"❌ Error: {e}"
                st.error(response)

    # Save assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": response})