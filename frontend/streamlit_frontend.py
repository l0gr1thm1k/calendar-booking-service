import streamlit as st
import requests
import json
import uuid


api_url = "http://0.0.0.0:7100/stream?protocol=json"
st.set_page_config(page_title="HouseWhisper Booking Agent", layout="wide")

# Custom CSS
st.markdown("""
    <style>
        .stApp { background-color: #f4f4f9; }
        h1 { color: #00FF99; text-align: center; }
        .stChatMessage { border-radius: 10px; padding: 10px; margin: 10px 0; }
        .stChatMessage.user { background-color: #e8f0fe; }
        .stChatMessage.assistant { background-color: #d1e7dd; }
        .stButton>button { background-color: #00AAFF; color: white; }
    </style>
""", unsafe_allow_html=True)

# Manage Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# 💬 Chat Interface
st.title("🤖 HouseWhisper Booking Agent")
st.caption("A helpful agent that helps manage your calendar")

# Display messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about your calendar..."):
    chat_history = "\n".join([msg["content"] for msg in st.session_state.messages[-4:]])  # Last 5 messages
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        # Stream response
        messages_payload = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in st.session_state.messages[-4:]
        ]
        messages_payload.append({"role": "user", "content": prompt})

        payload = {
            "messages": messages_payload,
            "id": str(uuid.uuid4())
        }

        try:
            response = requests.post(
                api_url,
                headers={"accept": "application/json", "Content-Type": "application/json"},
                json=payload,
                stream=True
            )

            for line in response.iter_lines():
                if line:
                    data = json.loads(line.decode())  # ✅ now succeeds
                    token = data.get("response", "")
                    full_response += token
                    response_placeholder.markdown(full_response + "▌")

            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"API error: {str(e)}")
            st.session_state.messages.append({"role": "assistant", "content": "Sorry, I encountered an error."})