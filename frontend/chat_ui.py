"""
Streamlit Chat Interface - Enhanced Edition

Beautiful, intuitive web UI for chatting with the MCP LLM Assistant.
Connects to the FastAPI backend for all LLM and Docker interactions.

Features:
- Modern, responsive design with custom CSS
- Real-time health monitoring
- Smart suggestions and quick actions
- Conversation management
- Rich message formatting
"""

import streamlit as st
import requests
from typing import List, Dict, Any
import time
import logging
from pathlib import Path
from datetime import datetime
import json

# Setup logging for frontend
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path(__file__).parent.parent / "logs" / "frontend.log"),
    ],
)
logger = logging.getLogger(__name__)


# --- Page Configuration ---
st.set_page_config(
    page_title="MCP AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/yourusername/mcp_llm_assistant",
        "Report a bug": "https://github.com/yourusername/mcp_llm_assistant/issues",
        "About": "# MCP AI Assistant\nIntelligent AI-powered assistant for Docker MCP management",
    },
)


# --- Constants ---
FASTAPI_URL = "http://127.0.0.1:8000/chat"
HEALTH_URL = "http://127.0.0.1:8000/health"


# --- Custom CSS for Beautiful UI ---
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    :root {
        color-scheme: only light;
    }

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        color: #1f2933;
    }

    body,
    .stApp,
    .block-container {
        background: #ffffff !important;
        color: #1f2933 !important;
    }

    .block-container {
        padding: 2rem 2.5rem !important;
    }

    .stApp > header,
    .stApp [data-testid="stHeader"],
    .stApp [data-testid="stToolbar"],
    .stApp [data-testid="stDecoration"],
    .stApp [data-testid="stStatusWidget"],
    [data-testid="stBottom"],
    [data-testid="stChatInputContainer"],
    footer {
        background: transparent !important;
    }

    section[data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid #e5e7eb !important;
        box-shadow: 4px 0 24px rgba(15, 23, 42, 0.05) !important;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4 {
        color: #111827 !important;
        font-weight: 700 !important;
    }

    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {
        color: #4b5563 !important;
    }

    .stMarkdown,
    .stMarkdown p,
    .stMarkdown li {
        color: #1f2933 !important;
        line-height: 1.65 !important;
    }

    .stMarkdown strong {
        color: #111827 !important;
    }

    .stButton button {
        border-radius: 12px !important;
        border: 1px solid #2563eb !important;
        background: #2563eb !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        padding: 0.65rem 1.2rem !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }

    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.18) !important;
        background: #1d4ed8 !important;
        border-color: #1d4ed8 !important;
    }

    .stButton button:active {
        transform: translateY(0);
        box-shadow: none !important;
    }

    .stButton button[kind="secondary"] {
        background: #ffffff !important;
        color: #2563eb !important;
    }

    .stButton button[kind="primary"] {
        background: #ea580c !important;
        border-color: #ea580c !important;
        box-shadow: 0 8px 20px rgba(234, 88, 12, 0.18) !important;
    }

    .stButton button[kind="primary"]:hover {
        background: #c2410c !important;
        border-color: #c2410c !important;
    }

    .stChatMessage {
        background: #ffffff !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 14px !important;
        padding: 1.25rem !important;
        margin: 1rem 0 !important;
        box-shadow: 0 12px 24px rgba(15, 23, 42, 0.06) !important;
    }

    .stChatMessage[data-testid*="user"] {
        background: #eff6ff !important;
        border-left: 4px solid #2563eb !important;
    }

    .stChatMessage[data-testid*="assistant"] {
        background: #fff7ed !important;
        border-left: 4px solid #ea580c !important;
    }

    .stChatMessage p,
    .stChatMessage div,
    .stChatMessage span {
        color: #1f2933 !important;
    }

    .stChatMessage code {
        background: #f1f5f9 !important;
        color: #2563eb !important;
        border-radius: 6px !important;
        padding: 0.2rem 0.4rem !important;
    }

    .stChatMessage pre {
        background: #f1f5f9 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        border: 1px solid #e2e8f0 !important;
    }

    .stApp input,
    .stApp textarea,
    .stApp select,
    .stApp [role="textbox"] {
        background: #ffffff !important;
        border: 1px solid #d1d5db !important;
        border-radius: 12px !important;
        color: #1f2933 !important;
        padding: 0.65rem 1rem !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }

    .stApp input:focus,
    .stApp textarea:focus,
    .stApp select:focus,
    .stApp [role="textbox"]:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.18) !important;
        outline: none !important;
    }

    .stChatInput {
        border: 1px solid #d1d5db !important;
        border-radius: 16px !important;
        background: #ffffff !important;
        box-shadow: 0 -4px 24px rgba(15, 23, 42, 0.05) !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }

    .stChatInput:focus-within {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.15) !important;
    }

    .stChatInput input,
    .stChatInput textarea,
    .stChatInput [contenteditable="true"] {
        background: #ffffff !important;
        color: #1f2933 !important;
    }

    .stChatInput input::placeholder,
    .stChatInput textarea::placeholder {
        color: #94a3b8 !important;
    }

    div[data-testid="stChatInputContainer"],
    .stChatFloatingInputContainer,
    .stBottom,
    .stBottom > div {
        background: #ffffff !important;
    }

    .stSuccess {
        background: #ecfdf5 !important;
        border-left: 4px solid #22c55e !important;
    }

    .stError {
        background: #fef2f2 !important;
        border-left: 4px solid #ef4444 !important;
    }

    .stWarning {
        background: #fffbeb !important;
        border-left: 4px solid #f59e0b !important;
    }

    .stInfo {
        background: #eff6ff !important;
        border-left: 4px solid #2563eb !important;
    }

    div[data-testid="stMetric"] {
        background: #ffffff !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05) !important;
        padding: 1.25rem !important;
    }

    div[data-testid="stMetric"] label {
        color: #6b7280 !important;
        letter-spacing: 0.04em !important;
        text-transform: uppercase !important;
        font-weight: 600 !important;
    }

    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #111827 !important;
        font-weight: 700 !important;
    }

    div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: #2563eb !important;
    }

    .stSpinner > div {
        border-top-color: #2563eb !important;
        border-right-color: #93c5fd !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 1px solid #e5e7eb !important;
        padding-bottom: 0.5rem !important;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 12px 12px 0 0 !important;
        border: 1px solid transparent !important;
        color: #6b7280 !important;
        padding: 0.6rem 1.3rem !important;
        background: #ffffff !important;
        margin-bottom: -1px !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #1f2933 !important;
        border-color: #e5e7eb !important;
    }

    .stTabs [aria-selected="true"] {
        border-color: #2563eb !important;
        border-bottom-color: #ffffff !important;
        color: #2563eb !important;
        background: #f8fafc !important;
    }

    .streamlit-expanderHeader {
        background: #f8fafc !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }

    .streamlit-expanderHeader:hover {
        background: #eef2f7 !important;
    }

    .streamlit-expanderContent {
        background: #ffffff !important;
        border-radius: 0 0 12px 12px !important;
        border: 1px solid #e5e7eb !important;
        border-top: none !important;
        padding: 1rem !important;
    }

    .stDownloadButton button {
        background: #10b981 !important;
        border: 1px solid #0f9d76 !important;
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    .stDownloadButton button:hover {
        background: #0f9d76 !important;
        border-color: #0f9d76 !important;
        box-shadow: 0 8px 20px rgba(15, 157, 118, 0.18) !important;
    }

    .stSelectbox [data-baseweb="select"] {
        background: #ffffff !important;
        border-radius: 12px !important;
        border: 1px solid #d1d5db !important;
    }

    a {
        color: #2563eb !important;
        text-decoration: none !important;
        font-weight: 500 !important;
    }

    a:hover {
        color: #1d4ed8 !important;
        text-decoration: underline !important;
    }

    blockquote {
        border-left: 4px solid #2563eb !important;
        padding-left: 1rem !important;
        background: #f8fafc !important;
        color: #1f2933 !important;
        border-radius: 4px !important;
    }

    hr {
        border-color: #e5e7eb !important;
        margin: 2rem 0 !important;
    }

    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 999px;
    }

    ::-webkit-scrollbar-thumb {
        background: #cbd5f5;
        border-radius: 999px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #a5b4fc;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# --- Helper Functions ---


def check_backend_health() -> Dict[str, Any]:
    """
    Checks if the FastAPI backend is running and healthy.

    Returns:
        Health status dictionary or error info
    """
    try:
        logger.info("Checking backend health...")
        response = requests.get(HEALTH_URL, timeout=5)
        response.raise_for_status()
        health_data = response.json()
        logger.info(f"Backend health: {health_data.get('status', 'unknown')}")
        return health_data
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Backend connection error: {e}")
        return {
            "status": "unreachable",
            "error": "Cannot connect to backend. Is the FastAPI server running?",
        }
    except requests.exceptions.Timeout as e:
        logger.error(f"Backend health check timeout: {e}")
        return {
            "status": "unreachable",
            "error": "Backend health check timed out. Server may be overloaded.",
        }
    except requests.exceptions.HTTPError as e:
        logger.error(f"Backend HTTP error: {e}")
        return {
            "status": "error",
            "error": f"Backend returned error: {e.response.status_code}",
        }
    except Exception as e:
        logger.error(f"Unexpected error checking backend health: {e}")
        return {"status": "error", "error": f"Unexpected error: {str(e)}"}


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
        logger.info(f"Sending chat message: {prompt[:50]}...")
        payload = {"prompt": prompt, "history": history}

        response = requests.post(
            FASTAPI_URL,
            json=payload,
            timeout=60,  # Give enough time for Docker commands
        )
        response.raise_for_status()

        reply = response.json()["reply"]
        logger.info(f"Received response: {reply[:50]}...")
        return reply

    except requests.exceptions.Timeout as e:
        error_msg = "⏱️ Request timed out. The operation took too long to complete."
        logger.error(f"Chat timeout: {e}")
        return error_msg

    except requests.exceptions.ConnectionError as e:
        error_msg = "❌ Cannot connect to the backend. Please ensure the FastAPI server is running."
        logger.error(f"Chat connection error: {e}")
        return error_msg

    except requests.exceptions.HTTPError as e:
        logger.error(f"Chat HTTP error: {e.response.status_code} - {e}")
        if e.response.status_code == 503:
            return (
                "⚠️ Backend service unavailable. Check if Docker is "
                "running and the MCP container is started."
            )
        elif e.response.status_code == 422:
            return "❌ Invalid request format. Please check your input."
        elif e.response.status_code == 429:
            return "⚠️ Rate limit exceeded. Please wait a moment and " "try again."
        else:
            try:
                error_detail = e.response.json().get("detail", str(e))
            except Exception:
                error_detail = str(e)
            return f"❌ Server error ({e.response.status_code}): " f"{error_detail}"

    except requests.exceptions.JSONDecodeError as e:
        error_msg = "❌ Invalid response from server. Please try again."
        logger.error(f"JSON decode error: {e}")
        return error_msg

    except KeyError as e:
        error_msg = "❌ Unexpected response format from server."
        logger.error(f"Missing key in response: {e}")
        return error_msg

    except Exception as e:
        error_msg = f"❌ Unexpected error: {str(e)}"
        logger.error(f"Unexpected chat error: {e}", exc_info=True)
        return error_msg


# --- Sidebar ---

with st.sidebar:
    # Header with logo
    st.markdown(
        """
        <div style='text-align: center; padding: 1rem 0;'>
            <h1 style='font-size: 2rem; margin: 0;'>🤖</h1>
            <h2 style='margin: 0.5rem 0 0 0; font-size: 1.5rem; color: #1f2933;'>MCP AI Assistant</h2>
            <p style='color: #4b5563; margin: 0.5rem 0 0 0; font-size: 0.9rem;'>Intelligent Docker Management</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # Health Status with enhanced UI
    st.subheader("📊 System Status")

    with st.spinner("Checking backend..."):
        health = check_backend_health()

    # Create status indicator
    if health.get("status") == "healthy":
        status_html = """
        <div style='padding: 1rem; border-radius: 8px; background: #ecfdf5; border: 1px solid #a7f3d0;'>
            <div style='display: flex; align-items: center; margin-bottom: 0.5rem;'>
                <span style='display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: #22c55e; margin-right: 8px;'></span>
                <strong style='color: #15803d;'>System Healthy</strong>
            </div>
            <p style='margin: 0.25rem 0; font-size: 0.9rem; color: #4b5563;'>
                ✅ All systems operational
            </p>
        </div>
        """
        st.markdown(status_html, unsafe_allow_html=True)

        # System details in expander
        with st.expander("📦 System Details", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Docker", "Connected", delta="Healthy")
            with col2:
                st.metric("LLM", "Active", delta="Ready")

            if health.get("container_name"):
                st.info(f"📦 Container: `{health.get('container_name')}`")
            if health.get("container_status"):
                st.info(f"🔄 Status: `{health.get('container_status')}`")
            if health.get("model"):
                st.info(f"🧠 Model: `{health.get('model')}`")

    elif health.get("status") == "partial":
        status_html = """
        <div style='padding: 1rem; border-radius: 8px; background: #fffbeb; border: 1px solid #fde68a;'>
            <div style='display: flex; align-items: center; margin-bottom: 0.5rem;'>
                <span style='display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: #f59e0b; margin-right: 8px;'></span>
                <strong style='color: #b45309;'>Partial Availability</strong>
            </div>
        </div>
        """
        st.markdown(status_html, unsafe_allow_html=True)

        if not health.get("docker_connected"):
            st.error("🐳 Docker not connected")
        if not health.get("llm_configured"):
            st.error("🧠 LLM not configured")

    elif health.get("status") == "unreachable":
        status_html = """
        <div style='padding: 1rem; border-radius: 8px; background: #fef2f2; border: 1px solid #fecaca;'>
            <div style='display: flex; align-items: center; margin-bottom: 0.5rem;'>
                <span style='display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: #ef4444; margin-right: 8px;'></span>
                <strong style='color: #b91c1c;'>Backend Unreachable</strong>
            </div>
        </div>
        """
        st.markdown(status_html, unsafe_allow_html=True)

        st.error(health.get("error", "Unknown error"))

        with st.expander("🔧 Troubleshooting", expanded=True):
            st.markdown(
                """
                **To start the backend:**
                ```bash
                cd mcp_llm_assistant
                ./daemon.sh start
                ```

                **Check status:**
                ```bash
                ./daemon.sh status
                ```

                **View logs:**
                ```bash
                tail -f logs/backend.log
                ```
                """
            )
    else:
        st.error("❌ System Unhealthy")
        st.error(health.get("error", "Unknown error"))

    st.markdown("---")

    # Quick Actions with enhanced buttons
    st.subheader("⚡ Quick Actions")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Refresh", use_container_width=True, type="primary"):
            st.rerun()
    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.messages = []
            st.session_state.conversation_stats = {
                "total_messages": 0,
                "total_tokens_estimate": 0,
            }
            st.rerun()

    # Export conversation button
    if len(st.session_state.get("messages", [])) > 1:
        if st.button("� Export Chat", use_container_width=True):
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "messages": st.session_state.messages,
            }
            st.download_button(
                label="📥 Download JSON",
                data=json.dumps(export_data, indent=2),
                file_name=f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True,
            )

    st.markdown("---")

    # Conversation Statistics
    if len(st.session_state.get("messages", [])) > 1:
        st.subheader("📈 Statistics")

        stats = st.session_state.get(
            "conversation_stats", {"total_messages": 0, "total_tokens_estimate": 0}
        )

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Messages", len(st.session_state.messages))
        with col2:
            user_messages = len(
                [m for m in st.session_state.messages if m["role"] == "user"]
            )
            st.metric("Your Queries", user_messages)

        st.markdown("---")

    # Smart Suggestions with tabs
    st.subheader("💡 Smart Actions")

    tab1, tab2, tab3 = st.tabs(["🐳 Docker", "📝 Notion", "🔧 System"])

    with tab1:
        st.markdown("**Docker Commands:**")
        if st.button(
            "📋 List Containers", use_container_width=True, key="btn_containers"
        ):
            st.session_state.suggested_prompt = "List all Docker containers"
        if st.button(
            "🔍 List MCP Servers", use_container_width=True, key="btn_servers"
        ):
            st.session_state.suggested_prompt = "Show me all available MCP servers"
        if st.button("📜 Show Logs", use_container_width=True, key="btn_logs"):
            st.session_state.suggested_prompt = "Show me the recent container logs"

    with tab2:
        st.markdown("**Notion Actions:**")
        if st.button(
            "🔎 Search Workspace", use_container_width=True, key="btn_notion_search"
        ):
            st.session_state.suggested_prompt = "Search my Notion workspace"
        if st.button(
            "📊 List Databases", use_container_width=True, key="btn_notion_dbs"
        ):
            st.session_state.suggested_prompt = "List all my Notion databases"
        if st.button("📄 Create Page", use_container_width=True, key="btn_notion_page"):
            st.session_state.suggested_prompt = "Help me create a new Notion page"

    with tab3:
        st.markdown("**System Info:**")
        if st.button("🏥 Health Check", use_container_width=True, key="btn_health"):
            st.session_state.suggested_prompt = "Run a system health check"
        if st.button("ℹ️ System Info", use_container_width=True, key="btn_info"):
            st.session_state.suggested_prompt = "Tell me about the system"

    st.markdown("---")

    # Documentation Links with enhanced styling
    st.subheader("📚 Resources")

    # Add helpful keyboard shortcuts
    with st.expander("⌨️ Keyboard Shortcuts"):
        st.markdown(
            """
            <div style='font-size: 0.9rem; color: #9CA3AF;'>
                <p><kbd>Ctrl</kbd> + <kbd>Enter</kbd> - Send message</p>
                <p><kbd>Ctrl</kbd> + <kbd>K</kbd> - Clear chat</p>
                <p><kbd>Ctrl</kbd> + <kbd>R</kbd> - Refresh page</p>
                <p><kbd>/</kbd> - Focus input field</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div style='padding: 0.5rem;'>
            <a href='http://127.0.0.1:8000/docs' target='_blank'
               style='display: block; padding: 0.5rem; margin: 0.25rem 0;
                      background: rgba(79, 70, 229, 0.1); border-radius: 6px;
                      text-decoration: none; color: #A5B4FC; border: 1px solid rgba(79, 70, 229, 0.3);'>
                📖 API Documentation
            </a>
            <a href='http://127.0.0.1:8000/health' target='_blank'
               style='display: block; padding: 0.5rem; margin: 0.25rem 0;
                      background: rgba(79, 70, 229, 0.1); border-radius: 6px;
                      text-decoration: none; color: #A5B4FC; border: 1px solid rgba(79, 70, 229, 0.3);'>
                🏥 Health Endpoint
            </a>
            <a href='http://127.0.0.1:8000/metrics' target='_blank'
               style='display: block; padding: 0.5rem; margin: 0.25rem 0;
                      background: rgba(79, 70, 229, 0.1); border-radius: 6px;
                      text-decoration: none; color: #A5B4FC; border: 1px solid rgba(79, 70, 229, 0.3);'>
                📊 System Metrics
            </a>
            <a href='https://developers.notion.com/reference' target='_blank'
               style='display: block; padding: 0.5rem; margin: 0.25rem 0;
                      background: rgba(79, 70, 229, 0.1); border-radius: 6px;
                      text-decoration: none; color: #A5B4FC; border: 1px solid rgba(79, 70, 229, 0.3);'>
                📝 Notion API Docs
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # Footer with version
    st.caption("v2.0.0 • Enhanced Edition")
    st.caption("Made with ❤️ using AI")


# --- Main Chat Interface ---

st.title("💬 MCP AI Assistant")
st.markdown(
    """
    <div style='margin-top: -1rem; margin-bottom: 1.5rem;'>
        <p style='font-size: 1.1rem; color: #9CA3AF; margin-bottom: 0.5rem;'>
            Your intelligent companion for Docker MCP management and Notion integration
        </p>
        <div style='display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap;'>
            <span style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white; padding: 0.25rem 0.75rem; border-radius: 12px;
                        font-size: 0.85rem; font-weight: 600;'>
                v2.0.0 Enhanced
            </span>
            <span style='background: rgba(34, 197, 94, 0.2); color: #22C55E;
                        padding: 0.25rem 0.75rem; border-radius: 12px;
                        font-size: 0.85rem; font-weight: 600;'>
                ✨ New Theme
            </span>
            <span style='background: rgba(59, 130, 246, 0.2); color: #3B82F6;
                        padding: 0.25rem 0.75rem; border-radius: 12px;
                        font-size: 0.85rem; font-weight: 600;'>
                🚀 Production Ready
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.conversation_stats = {
        "total_messages": 0,
        "total_tokens_estimate": 0,
    }
    # Add enhanced welcome message
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": """👋 **Welcome to MCP AI Assistant!**

I'm your intelligent companion for Docker and Notion management. Here's what I can do:

**🐳 Docker & MCP:**
- Execute commands in your containers
- List and monitor running containers
- Retrieve and analyze container logs
- Manage MCP servers and tools

**📝 Notion Integration:**
- Search your workspace
- Create and update pages
- Query databases
- Manage properties and schemas

**💡 Smart Features:**
- Natural language understanding
- Proactive tool usage
- Real-time health monitoring
- Conversation export

Try clicking one of the **Smart Actions** in the sidebar, or ask me anything!""",
        }
    )

# Display chat history with enhanced formatting
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Add timestamp for messages (except welcome)
        if idx > 0 and "timestamp" in message:
            st.caption(
                f"🕐 {datetime.fromisoformat(message['timestamp']).strftime('%I:%M %p')}"
            )

# Show helpful example prompts if conversation is empty (only welcome message)
if len(st.session_state.messages) == 1:
    st.markdown("### 💡 Try These Example Prompts:")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div style='background: rgba(99, 102, 241, 0.1); padding: 1rem;
                        border-radius: 12px; border: 1px solid rgba(99, 102, 241, 0.3);
                        margin-bottom: 1rem;'>
                <h4 style='margin: 0 0 0.5rem 0; color: #A5B4FC;'>🐳 Docker</h4>
                <ul style='margin: 0; padding-left: 1.5rem; color: #9CA3AF;'>
                    <li>List all running containers</li>
                    <li>Show me MCP server status</li>
                    <li>Get logs from the last hour</li>
                </ul>
            </div>

            <div style='background: rgba(167, 139, 250, 0.1); padding: 1rem;
                        border-radius: 12px; border: 1px solid rgba(167, 139, 250, 0.3);'>
                <h4 style='margin: 0 0 0.5rem 0; color: #C4B5FD;'>📝 Notion</h4>
                <ul style='margin: 0; padding-left: 1.5rem; color: #9CA3AF;'>
                    <li>Search my workspace</li>
                    <li>List all databases</li>
                    <li>Create a new task page</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div style='background: rgba(59, 130, 246, 0.1); padding: 1rem;
                        border-radius: 12px; border: 1px solid rgba(59, 130, 246, 0.3);
                        margin-bottom: 1rem;'>
                <h4 style='margin: 0 0 0.5rem 0; color: #93C5FD;'>🔧 System</h4>
                <ul style='margin: 0; padding-left: 1.5rem; color: #9CA3AF;'>
                    <li>Check system health</li>
                    <li>Show available tools</li>
                    <li>What can you do?</li>
                </ul>
            </div>

            <div style='background: rgba(16, 185, 129, 0.1); padding: 1rem;
                        border-radius: 12px; border: 1px solid rgba(16, 185, 129, 0.3);'>
                <h4 style='margin: 0 0 0.5rem 0; color: #6EE7B7;'>💬 Natural Language</h4>
                <ul style='margin: 0; padding-left: 1.5rem; color: #9CA3AF;'>
                    <li>Find my latest notes</li>
                    <li>Help me debug a container</li>
                    <li>Explain how MCP works</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

# Handle suggested prompts from sidebar
suggested_prompt = None
if "suggested_prompt" in st.session_state:
    suggested_prompt = st.session_state.suggested_prompt
    del st.session_state.suggested_prompt

# Chat input with enhanced placeholder
prompt = None
if suggested_prompt:
    prompt = suggested_prompt
elif user_input := st.chat_input(
    "Ask about Docker, Notion, or anything else...", key="chat_input"
):
    prompt = user_input

if prompt:
    # Check backend health before sending
    health = check_backend_health()
    if health.get("status") == "unreachable":
        st.error("❌ Backend is not running. Please start the FastAPI server first.")
        st.info("Run: `./daemon.sh start` in the project directory")
        st.stop()

    # Add user message to session state with timestamp
    user_message = {
        "role": "user",
        "content": prompt,
        "timestamp": datetime.now().isoformat(),
    }
    st.session_state.messages.append(user_message)

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
        st.caption(f"🕐 {datetime.now().strftime('%I:%M %p')}")

    # Get assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        status_placeholder = st.empty()

        # Show thinking indicator with steps
        with status_placeholder:
            with st.status("🤔 Processing your request...", expanded=True) as status:
                st.write("📡 Connecting to backend...")
                time.sleep(0.3)

                st.write("� Analyzing your message...")
                time.sleep(0.3)

                # Prepare history (exclude the current prompt)
                history_for_api = st.session_state.messages[:-1]

                st.write("⚡ Generating response...")

                # Send request to backend
                start_time = time.time()
                assistant_reply = send_chat_message(prompt, history_for_api)
                elapsed_time = time.time() - start_time

                status.update(
                    label="✅ Response ready!", state="complete", expanded=False
                )

        # Clear status and display the response
        status_placeholder.empty()
        message_placeholder.markdown(assistant_reply)

        # Show response metrics in columns
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption(f"⏱️ {elapsed_time:.2f}s")
        with col2:
            # Estimate tokens (rough: ~4 chars per token)
            est_tokens = len(assistant_reply) // 4
            st.caption(f"📊 ~{est_tokens} tokens")
        with col3:
            st.caption(f"🕐 {datetime.now().strftime('%I:%M %p')}")

    # Add assistant response to session state with timestamp
    assistant_message = {
        "role": "assistant",
        "content": assistant_reply,
        "timestamp": datetime.now().isoformat(),
        "response_time": elapsed_time,
    }
    st.session_state.messages.append(assistant_message)

    # Update conversation stats
    st.session_state.conversation_stats["total_messages"] = len(
        st.session_state.messages
    )


# --- Footer ---

st.markdown("---")

# Enhanced footer with metrics
footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.markdown(
        """
        <div style='text-align: center;'>
            <p style='margin: 0; color: #6b7280; font-size: 0.9rem;'>Powered by</p>
            <p style='margin: 0; font-weight: 600; color: #1f2933;'>Google Gemini 🧠</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with footer_col2:
    st.markdown(
        """
        <div style='text-align: center;'>
            <p style='margin: 0; color: #6b7280; font-size: 0.9rem;'>Built with</p>
            <p style='margin: 0; font-weight: 600; color: #1f2933;'>FastAPI ⚡ & Streamlit 🎈</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with footer_col3:
    st.markdown(
        """
        <div style='text-align: center;'>
            <p style='margin: 0; color: #6b7280; font-size: 0.9rem;'>Integrations</p>
            <p style='margin: 0; font-weight: 600; color: #1f2933;'>Docker 🐳 & Notion 📝</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
