import streamlit as st
import requests
import json
import uuid
import re
import os
from pathlib import Path
import streamlit.components.v1 as components


def running_in_docker():
    return os.path.exists('/.dockerenv')


if running_in_docker():
    url_base = "booking-service-api"
else:
    url_base = "0.0.0.0"

api_url = f"http://{url_base}:7100/stream?protocol=json"

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


# Display messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about your calendar..."):
    session_id = str(uuid.uuid4())
    chat_history = "\n".join([msg["content"] for msg in st.session_state.messages[-5:]])
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
            for msg in st.session_state.messages[-5:]
        ]
        messages_payload.append({"role": "user", "content": prompt})

        payload = {
            "messages": messages_payload,
            "id": session_id
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
                    data = json.loads(line.decode())
                    token = data.get("response", "")
                    full_response += token
                    response_placeholder.markdown(full_response + "▌")

            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

            raw_html = Path("frontend/weekly_calendar.html").read_text()
            resized_html = re.sub(
                r'style="height:\d+px; width:100%;"',
                'style="height:350px; width:600px;"',
                raw_html
            )
            wrapped_html = f"""
            <div style="width: 825px; height: 650px; margin: auto;">
                {resized_html}
            </div>
            """
            components.html(wrapped_html, height=650, scrolling=False)

        except Exception as e:
            st.error(f"API error: {str(e)}")
            st.session_state.messages.append({"role": "assistant", "content": "Sorry, I encountered an error."})