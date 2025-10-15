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
    /* Main app styling */
    .stApp {
        background: linear-gradient(135deg, #0E1117 0%, #1a1d29 100%);
    }

    /* Chat messages */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
    }

    .stChatMessage:hover {
        background-color: rgba(255, 255, 255, 0.08);
        border-color: rgba(79, 70, 229, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2);
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1d29 0%, #0E1117 100%);
        border-right: 1px solid rgba(79, 70, 229, 0.3);
    }

    /* Buttons */
    .stButton button {
        border-radius: 8px;
        border: 1px solid rgba(79, 70, 229, 0.5);
        background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%);
        color: white;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(79, 70, 229, 0.3);
    }

    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(79, 70, 229, 0.5);
        border-color: rgba(79, 70, 229, 0.8);
    }

    /* Input fields */
    .stTextInput input, .stTextArea textarea {
        border-radius: 8px;
        border: 1px solid rgba(79, 70, 229, 0.3);
        background-color: rgba(255, 255, 255, 0.05);
        transition: all 0.3s ease;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: rgba(79, 70, 229, 0.8);
        box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.2);
    }

    /* Success/Error/Warning boxes */
    .stSuccess {
        background-color: rgba(34, 197, 94, 0.1);
        border-left: 4px solid #22C55E;
        border-radius: 8px;
        padding: 1rem;
    }

    .stError {
        background-color: rgba(239, 68, 68, 0.1);
        border-left: 4px solid #EF4444;
        border-radius: 8px;
        padding: 1rem;
    }

    .stWarning {
        background-color: rgba(251, 191, 36, 0.1);
        border-left: 4px solid #FBBF24;
        border-radius: 8px;
        padding: 1rem;
    }

    .stInfo {
        background-color: rgba(59, 130, 246, 0.1);
        border-left: 4px solid #3B82F6;
        border-radius: 8px;
        padding: 1rem;
    }

    /* Title animations */
    h1 {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #EC4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
        animation: gradient 3s ease infinite;
        background-size: 200% 200%;
    }

    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s ease-in-out infinite;
    }

    .status-healthy { background-color: #22C55E; }
    .status-warning { background-color: #FBBF24; }
    .status-error { background-color: #EF4444; }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    /* Code blocks */
    .stCodeBlock {
        border-radius: 8px;
        border: 1px solid rgba(79, 70, 229, 0.3);
        background-color: rgba(0, 0, 0, 0.3);
    }

    /* Metrics */
    div[data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid rgba(79, 70, 229, 0.2);
    }

    /* Spinner */
    .stSpinner > div {
        border-top-color: #4F46E5 !important;
    }

    /* Chat input */
    .stChatInput {
        border-radius: 12px;
        border: 2px solid rgba(79, 70, 229, 0.3);
        background: rgba(255, 255, 255, 0.05);
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 5px;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        border-radius: 5px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(79, 70, 229, 0.3);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%);
        border-color: rgba(79, 70, 229, 0.8);
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
            <h2 style='margin: 0.5rem 0 0 0; font-size: 1.5rem;'>MCP AI Assistant</h2>
            <p style='color: #9CA3AF; margin: 0.5rem 0 0 0; font-size: 0.9rem;'>Intelligent Docker Management</p>
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
        <div style='padding: 1rem; border-radius: 8px; background: rgba(34, 197, 94, 0.1); border: 1px solid rgba(34, 197, 94, 0.3);'>
            <div style='display: flex; align-items: center; margin-bottom: 0.5rem;'>
                <span class='status-indicator status-healthy'></span>
                <strong style='color: #22C55E;'>System Healthy</strong>
            </div>
            <p style='margin: 0.25rem 0; font-size: 0.9rem; color: #9CA3AF;'>
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
        <div style='padding: 1rem; border-radius: 8px; background: rgba(251, 191, 36, 0.1); border: 1px solid rgba(251, 191, 36, 0.3);'>
            <div style='display: flex; align-items: center; margin-bottom: 0.5rem;'>
                <span class='status-indicator status-warning'></span>
                <strong style='color: #FBBF24;'>Partial Availability</strong>
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
        <div style='padding: 1rem; border-radius: 8px; background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3);'>
            <div style='display: flex; align-items: center; margin-bottom: 0.5rem;'>
                <span class='status-indicator status-error'></span>
                <strong style='color: #EF4444;'>Backend Unreachable</strong>
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
    <p style='font-size: 1.1rem; color: #9CA3AF; margin-top: -1rem;'>
        Your intelligent companion for Docker MCP management and Notion integration
    </p>
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

# Handle suggested prompts from sidebar
if "suggested_prompt" in st.session_state:
    prompt = st.session_state.suggested_prompt
    del st.session_state.suggested_prompt
    # Process the suggested prompt
    st.rerun()

# Chat input with enhanced placeholder
if prompt := st.chat_input(
    "Ask about Docker, Notion, or anything else...", key="chat_input"
):
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
            <p style='margin: 0; color: #9CA3AF; font-size: 0.9rem;'>Powered by</p>
            <p style='margin: 0; font-weight: 600;'>Google Gemini 🧠</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with footer_col2:
    st.markdown(
        """
        <div style='text-align: center;'>
            <p style='margin: 0; color: #9CA3AF; font-size: 0.9rem;'>Built with</p>
            <p style='margin: 0; font-weight: 600;'>FastAPI ⚡ & Streamlit 🎈</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with footer_col3:
    st.markdown(
        """
        <div style='text-align: center;'>
            <p style='margin: 0; color: #9CA3AF; font-size: 0.9rem;'>Integrations</p>
            <p style='margin: 0; font-weight: 600;'>Docker 🐳 & Notion 📝</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
