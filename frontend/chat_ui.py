"""
Streamlit Chat Interface

Interactive web UI for chatting with the MCP LLM Assistant.
Connects to the FastAPI backend for all LLM and Docker interactions.
"""

import streamlit as st
import requests
from typing import List, Dict, Any
import time


# --- Page Configuration ---
st.set_page_config(
    page_title="MCP LLM Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --- Constants ---
FASTAPI_URL = "http://127.0.0.1:8000/chat"
HEALTH_URL = "http://127.0.0.1:8000/health"


# --- Helper Functions ---


def check_backend_health() -> Dict[str, Any]:
    """
    Checks if the FastAPI backend is running and healthy.

    Returns:
        Health status dictionary or error info
    """
    try:
        response = requests.get(HEALTH_URL, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {
            "status": "unreachable",
            "error": "Cannot connect to backend. Is the FastAPI server running?",
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def send_chat_message(prompt: str, history: List[Dict[str, str]]) -> str:
    """
    Sends a chat message to the FastAPI backend.

    Args:
        prompt: The user's message
        history: Previous conversation messages

    Returns:
        The assistant's response or error message
    """
    try:
        payload = {"prompt": prompt, "history": history}

        response = requests.post(
            FASTAPI_URL,
            json=payload,
            timeout=60,  # Give enough time for Docker commands
        )
        response.raise_for_status()

        return response.json()["reply"]

    except requests.exceptions.Timeout:
        return "⏱️ Request timed out. The operation took too long to complete."

    except requests.exceptions.ConnectionError:
        return "❌ Cannot connect to the backend. Please ensure the FastAPI server is running."

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 503:
            return "⚠️ Backend service unavailable. Check if Docker is running and the MCP container is started."
        else:
            error_detail = e.response.json().get("detail", str(e))
            return f"❌ Server error: {error_detail}"

    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"


# --- Sidebar ---

with st.sidebar:
    st.title("🤖 MCP Assistant")
    st.markdown("---")

    # Health Status
    st.subheader("System Status")

    with st.spinner("Checking backend..."):
        health = check_backend_health()

    if health.get("status") == "healthy":
        st.success("✅ System Healthy")
        st.info(f"📦 Container: {health.get('container_name', 'N/A')}")
        st.info(f"🔄 Status: {health.get('container_status', 'N/A')}")
    elif health.get("status") == "partial":
        st.warning("⚠️ Partial Availability")
        if not health.get("docker_connected"):
            st.error("Docker not connected")
        if not health.get("llm_configured"):
            st.error("LLM not configured")
    elif health.get("status") == "unreachable":
        st.error("❌ Backend Unreachable")
        st.error(health.get("error", "Unknown error"))
        st.markdown(
            """
        **To start the backend:**
        ```bash
        cd mcp_llm_assistant
        source venv/bin/activate
        uvicorn app.main:app --reload
        ```
        """
        )
    else:
        st.error("❌ System Unhealthy")
        st.error(health.get("error", "Unknown error"))

    st.markdown("---")

    # Quick Actions
    st.subheader("Quick Actions")

    if st.button("🔄 Refresh Status", use_container_width=True):
        st.rerun()

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")

    # Example Prompts
    st.subheader("Example Prompts")
    st.markdown(
        """
    Try asking:
    - "What containers are running?"
    - "List MCP servers"
    - "Show me the container logs"
    - "Execute 'docker mcp server list'"
    - "What's in the /app directory?"
    """
    )

    st.markdown("---")

    # Documentation Links
    st.subheader("Resources")
    st.markdown(
        """
    - [API Docs](http://127.0.0.1:8000/docs)
    - [Health Check](http://127.0.0.1:8000/health)
    """
    )


# --- Main Chat Interface ---

st.title("💬 MCP LLM Assistant")
st.caption("Chat with your Docker containers using AI")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add welcome message
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": """👋 Hello! I'm your MCP Assistant.

I can help you interact with your Docker containers and MCP tools. I can:
- Execute commands in your containers
- List running containers
- Retrieve container logs
- Provide guidance on Docker and MCP operations

What would you like to do?""",
        }
    )

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about your MCP container..."):
    # Check backend health before sending
    health = check_backend_health()
    if health.get("status") == "unreachable":
        st.error("❌ Backend is not running. Please start the FastAPI server first.")
        st.stop()

    # Add user message to session state
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        # Show thinking indicator
        with st.spinner("🤔 Thinking..."):
            # Prepare history (exclude the current prompt)
            history_for_api = st.session_state.messages[:-1]

            # Send request to backend
            start_time = time.time()
            assistant_reply = send_chat_message(prompt, history_for_api)
            elapsed_time = time.time() - start_time

        # Display the response
        message_placeholder.markdown(assistant_reply)

        # Show response time in small text
        st.caption(f"⏱️ Response time: {elapsed_time:.2f}s")

    # Add assistant response to session state
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})


# --- Footer ---

st.markdown("---")
st.caption("Powered by Google Gemini 🧠 | FastAPI ⚡ | Docker 🐳")
