"""
Streamlit Chat Interface - 10x Dev Edition

A radically simplified, high-performance chat UI that focuses on:
- Zero-friction user experience
- Minimal reloads and optimal state management
- Clean, maintainable code
- Native Streamlit theming (no CSS warfare)
- Fast, responsive interactions
- Secure authentication for external access
"""

import streamlit as st
import requests
from typing import List, Dict, Any
from datetime import datetime
from functools import lru_cache
import json
from auth import check_authentication, show_logout_button

# --- Config (Constants Only) ---
FASTAPI_URL = "http://127.0.0.1:8000/chat"
HEALTH_URL = "http://127.0.0.1:8000/health"

# --- Streamlit Config (MUST be first Streamlit command) ---
st.set_page_config(
    page_title="MCP AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Authentication Check (immediately after page_config) ---
if not check_authentication():
    st.stop()

# --- Minimal Custom CSS (Streamlit-friendly) ---
st.markdown(
    """
<style>
    /* Subtle enhancements only - let Streamlit handle the rest */
    .stChatMessage {
        padding: 1rem !important;
        margin: 0.5rem 0 !important;
    }

    /* Smooth animations */
    .stButton button {
        transition: all 0.2s ease !important;
    }

    /* Better spacing */
    .block-container {
        padding-top: 2rem !important;
    }
</style>
""",
    unsafe_allow_html=True,
)


# --- Optimized Helper Functions ---


@lru_cache(maxsize=1)
@st.cache_data(ttl=10)  # Cache for 10 seconds
def check_backend_health() -> Dict[str, Any]:
    """Cached health check - prevents redundant calls."""
    try:
        response = requests.get(HEALTH_URL, timeout=3)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {
            "status": "unreachable",
            "error": str(e),
            "docker_connected": False,
            "llm_configured": False,
        }


def send_chat_message(prompt: str, history: List[Dict[str, str]]) -> str:
    """Send message to backend - streamlined error handling."""
    try:
        # Clean history - remove timestamp and other non-serializable fields
        clean_history = [
            {"role": msg["role"], "content": msg["content"]} for msg in history
        ]

        response = requests.post(
            FASTAPI_URL,
            json={"prompt": prompt, "history": clean_history},
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["reply"]

    except requests.exceptions.Timeout:
        return "⏱️ Request timed out. Try a simpler query."

    except requests.exceptions.ConnectionError:
        return "❌ Backend offline. Run `./daemon.sh start`"

    except Exception as e:
        return f"❌ Error: {str(e)}"


def init_session_state():
    """Initialize session state once - idempotent."""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": """👋 **MCP AI Assistant Ready**

I can help you with:
- 🐳 Docker & MCP operations
- 📝 Notion workspace management
- 🔧 System monitoring & logs

**Quick Start:** Try "List my Notion databases" or click a button below!""",
                "timestamp": datetime.now(),
            }
        ]

    if "chat_key" not in st.session_state:
        st.session_state.chat_key = 0  # For forcing chat input refresh


# --- Sidebar (Streamlined) ---


def render_sidebar():
    """Clean, focused sidebar with essential controls."""
    with st.sidebar:
        # Header
        st.title("🤖 MCP Assistant")
        st.caption("v2.1.0 • Optimized Edition")

        # Logout button (if authenticated)
        show_logout_button()

        st.divider()
        with st.container():
            health = check_backend_health()

            if health.get("status") == "healthy":
                st.success("✅ System Healthy")
                with st.expander("📊 Details"):
                    st.metric("Docker", "✓ Connected")
                    st.metric("LLM", health.get("model", "Unknown"))
            else:
                st.error("❌ Backend Offline")
                if st.button("🔧 Troubleshoot"):
                    st.code("./daemon.sh start", language="bash")

        st.divider()

        # Quick Actions (Simplified)
        st.subheader("⚡ Quick Actions")

        # Single column for cleaner look
        if st.button("🗑️ Clear Chat", use_container_width=True, key="clear"):
            st.session_state.messages = st.session_state.messages[:1]  # Keep welcome
            st.session_state.chat_key += 1
            st.rerun()

        if st.button("🔄 Refresh", use_container_width=True, key="refresh"):
            st.cache_data.clear()  # Clear all cached data
            st.rerun()

        # Export (only if there's content)
        if len(st.session_state.messages) > 1:
            export_data = json.dumps(
                {
                    "exported": datetime.now().isoformat(),
                    "messages": st.session_state.messages,
                },
                default=str,
                indent=2,
            )

            st.download_button(
                "💾 Export Chat",
                export_data,
                f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "application/json",
                use_container_width=True,
            )

        st.divider()

        # Smart Suggestions (Collapsed by default)
        with st.expander("💡 Suggestions", expanded=False):
            suggestions = {
                "🐳 List Containers": "List all Docker containers",
                "📊 My Databases": "Show my Notion databases",
                "📜 Recent Logs": "Show recent container logs",
                "🔍 Search Workspace": "Search my Notion workspace",
                "🏥 Health Check": "Run a system health check",
            }

            for label, prompt in suggestions.items():
                if st.button(label, use_container_width=True, key=f"sugg_{label}"):
                    # Add to messages and trigger processing
                    st.session_state.pending_prompt = prompt
                    st.rerun()

        st.divider()

        # Stats (Minimal)
        if len(st.session_state.messages) > 1:
            st.caption(f"📊 {len(st.session_state.messages)} messages in conversation")


# --- Main Chat Interface ---


def render_chat():
    """Main chat interface - clean and performant."""

    # Title
    st.title("💬 Chat")

    # Display messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            # Timestamp (subtle)
            if "timestamp" in msg and isinstance(msg["timestamp"], datetime):
                st.caption(msg["timestamp"].strftime("%-I:%M %p"))

    # Handle pending prompt from sidebar
    if "pending_prompt" in st.session_state:
        prompt = st.session_state.pending_prompt
        del st.session_state.pending_prompt
        process_message(prompt)
        st.rerun()

    # Chat input (with unique key to prevent disappearing)
    user_input = st.chat_input(
        "Ask about Docker, Notion, or anything...",
        key=f"chat_input_{st.session_state.chat_key}",
    )

    if user_input:
        process_message(user_input)
        st.rerun()


def process_message(prompt: str):
    """Process a user message - separated for reusability."""

    # Add user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now(),
        }
    )

    # Show user message immediately
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Prepare history (exclude current prompt)
            history = st.session_state.messages[:-1]
            reply = send_chat_message(prompt, history)

        st.markdown(reply)

    # Add assistant message
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": reply,
            "timestamp": datetime.now(),
        }
    )


# --- Main App ---


def main():
    """Main app entry point - authentication already checked at module level."""
    # Initialize and render the app
    init_session_state()
    render_sidebar()
    render_chat()


if __name__ == "__main__":
    main()
