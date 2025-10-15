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
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        color: #f0f0f0;
    }

    /* Main app styling - Dark cyberpunk gradient */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #16213e 50%, #0f3460 100%);
        background-attachment: fixed;
        color: #f0f0f0;
    }

    /* Animated background particles */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image:
            radial-gradient(circle at 20% 50%, rgba(120, 119, 198, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(99, 102, 241, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 20%, rgba(167, 139, 250, 0.1) 0%, transparent 50%);
        pointer-events: none;
        animation: particles 20s ease-in-out infinite;
    }

    @keyframes particles {
        0%, 100% { opacity: 0.3; transform: scale(1); }
        50% { opacity: 0.6; transform: scale(1.1); }
    }

    /* Chat messages - Glassmorphism */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(20px);
        border-radius: 16px !important;
        padding: 1.5rem !important;
        margin: 1rem 0 !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        color: #f0f0f0 !important;
    }

    .stChatMessage:hover {
        background: rgba(255, 255, 255, 0.12) !important;
        border-color: rgba(99, 102, 241, 0.5) !important;
        transform: translateY(-4px) scale(1.01) !important;
        box-shadow: 0 12px 48px rgba(99, 102, 241, 0.4) !important;
    }

    /* User message - Purple gradient */
    .stChatMessage[data-testid*="user"] {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.25) 0%, rgba(139, 92, 246, 0.25) 100%) !important;
        border-left: 4px solid #8B5CF6 !important;
    }

    /* Assistant message - Blue gradient */
    .stChatMessage[data-testid*="assistant"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.25) 0%, rgba(147, 51, 234, 0.25) 100%) !important;
        border-left: 4px solid #60A5FA !important;
    }

    /* Message content text */
    .stChatMessage p, .stChatMessage div, .stChatMessage span {
        color: #f0f0f0 !important;
    }

    .stChatMessage code {
        color: #fbbf24 !important;
        background: rgba(0, 0, 0, 0.4) !important;
    }

    /* Sidebar styling - Premium dark */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1729 0%, #0a0e27 100%) !important;
        border-right: 1px solid rgba(99, 102, 241, 0.3) !important;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.4) !important;
    }

    section[data-testid="stSidebar"] > div {
        background: transparent !important;
    }

    /* Sidebar text */
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {
        color: #e5e7eb !important;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4 {
        color: #f0f0f0 !important;
    }

    /* Buttons - Gradient with glow */
    .stButton button {
        border-radius: 12px !important;
        border: none !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4) !important;
        position: relative !important;
        overflow: hidden !important;
    }

    .stButton button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        transition: left 0.5s;
    }

    .stButton button:hover::before {
        left: 100%;
    }

    .stButton button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.6) !important;
    }

    .stButton button:active {
        transform: translateY(-1px) !important;
    }

    /* Primary button variant */
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
        box-shadow: 0 4px 16px rgba(245, 87, 108, 0.4) !important;
    }

    .stButton button[kind="primary"]:hover {
        box-shadow: 0 8px 24px rgba(245, 87, 108, 0.6) !important;
    }

    /* Input fields - Futuristic */
    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        border-radius: 12px !important;
        border: 2px solid rgba(99, 102, 241, 0.4) !important;
        background: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(10px) !important;
        color: #f0f0f0 !important;
        padding: 0.75rem 1rem !important;
        transition: all 0.3s ease !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus {
        border-color: #8B5CF6 !important;
        box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.25), 0 0 20px rgba(139, 92, 246, 0.4) !important;
        background: rgba(255, 255, 255, 0.12) !important;
    }

    .stTextInput input::placeholder, .stTextArea textarea::placeholder {
        color: #9ca3af !important;
    }

    /* Alert boxes - Enhanced */
    .stSuccess {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, rgba(16, 185, 129, 0.15) 100%) !important;
        border-left: 4px solid #22C55E !important;
        border-radius: 12px !important;
        padding: 1.25rem !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 4px 16px rgba(34, 197, 94, 0.2) !important;
    }

    .stError {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(220, 38, 38, 0.15) 100%) !important;
        border-left: 4px solid #EF4444 !important;
        border-radius: 12px !important;
        padding: 1.25rem !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 4px 16px rgba(239, 68, 68, 0.2) !important;
    }

    .stWarning {
        background: linear-gradient(135deg, rgba(251, 191, 36, 0.15) 0%, rgba(245, 158, 11, 0.15) 100%) !important;
        border-left: 4px solid #FBBF24 !important;
        border-radius: 12px !important;
        padding: 1.25rem !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 4px 16px rgba(251, 191, 36, 0.2) !important;
    }

    .stInfo {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(37, 99, 235, 0.15) 100%) !important;
        border-left: 4px solid #3B82F6 !important;
        border-radius: 12px !important;
        padding: 1.25rem !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 4px 16px rgba(59, 130, 246, 0.2) !important;
    }

    /* Headings - Animated gradient text */
    h1 {
        background: linear-gradient(135deg, #818cf8 0%, #a78bfa 50%, #f0abfc 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em !important;
        animation: gradient-shift 4s ease infinite !important;
        background-size: 200% 200% !important;
    }

    h2 {
        color: #f0f0f0 !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em !important;
    }

    h3 {
        color: #e5e7eb !important;
        font-weight: 600 !important;
    }

    h4 {
        color: #d1d5db !important;
        font-weight: 600 !important;
    }

    p {
        color: #e5e7eb !important;
    }

    /* Labels and captions */
    label {
        color: #d1d5db !important;
    }

    .stCaption {
        color: #9ca3af !important;
    }

    @keyframes gradient-shift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }

    /* Status indicators - Glowing */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 10px;
        animation: pulse-glow 2s ease-in-out infinite;
        box-shadow: 0 0 10px currentColor;
    }

    .status-healthy {
        background-color: #22C55E;
        box-shadow: 0 0 16px #22C55E, 0 0 32px rgba(34, 197, 94, 0.5);
    }

    .status-warning {
        background-color: #FBBF24;
        box-shadow: 0 0 16px #FBBF24, 0 0 32px rgba(251, 191, 36, 0.5);
    }

    .status-error {
        background-color: #EF4444;
        box-shadow: 0 0 16px #EF4444, 0 0 32px rgba(239, 68, 68, 0.5);
    }

    @keyframes pulse-glow {
        0%, 100% {
            opacity: 1;
            transform: scale(1);
        }
        50% {
            opacity: 0.6;
            transform: scale(1.1);
        }
    }

    /* Code blocks - Terminal style */
    .stCodeBlock {
        border-radius: 12px !important;
        border: 1px solid rgba(99, 102, 241, 0.3) !important;
        background: rgba(0, 0, 0, 0.5) !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3) !important;
    }

    code {
        background: rgba(99, 102, 241, 0.1) !important;
        border-radius: 4px !important;
        padding: 2px 6px !important;
        font-family: 'SF Mono', 'Monaco', 'Cascadia Code', monospace !important;
    }

    /* Metrics - Card style */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%) !important;
        padding: 1.25rem !important;
        border-radius: 12px !important;
        border: 1px solid rgba(99, 102, 241, 0.3) !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.3s ease !important;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4) !important;
    }

    div[data-testid="stMetric"] label {
        color: #d1d5db !important;
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }

    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #f0f0f0 !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }

    div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: #a5b4fc !important;
    }

    /* Spinner - Cyberpunk */
    .stSpinner > div {
        border-top-color: #6366F1 !important;
        border-right-color: #8B5CF6 !important;
        animation: spin 1s cubic-bezier(0.4, 0, 0.2, 1) infinite !important;
    }

    /* Chat input - Floating */
    .stChatInput {
        border-radius: 16px !important;
        border: 2px solid rgba(139, 92, 246, 0.4) !important;
        background: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(20px) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important;
        transition: all 0.3s ease !important;
    }

    .stChatInput:focus-within {
        border-color: #8B5CF6 !important;
        box-shadow: 0 8px 32px rgba(139, 92, 246, 0.5), 0 0 0 4px rgba(139, 92, 246, 0.2) !important;
        transform: translateY(-2px);
    }

    .stChatInput input {
        color: #f0f0f0 !important;
    }

    .stChatInput input::placeholder {
        color: #9ca3af !important;
    }

    /* Scrollbar - Sleek */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        transition: all 0.3s ease;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #7c8aed 0%, #8b5fb5 100%);
        box-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
    }

    /* Tabs - Modern */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: transparent !important;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 12px !important;
        padding: 10px 20px !important;
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
        color: #9ca3af !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.05) !important;
        border-color: rgba(99, 102, 241, 0.4) !important;
        color: #e5e7eb !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border-color: transparent !important;
        color: white !important;
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4) !important;
    }

    /* Expander - Accordion style */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.03) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
        padding: 1rem !important;
        transition: all 0.3s ease !important;
    }

    .streamlit-expanderHeader:hover {
        background: rgba(255, 255, 255, 0.05) !important;
        border-color: rgba(99, 102, 241, 0.4) !important;
    }

    /* Download button */
    .stDownloadButton button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        box-shadow: 0 4px 16px rgba(16, 185, 129, 0.4) !important;
    }

    .stDownloadButton button:hover {
        box-shadow: 0 8px 24px rgba(16, 185, 129, 0.6) !important;
    }

    /* Select box */
    .stSelectbox [data-baseweb="select"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border-radius: 12px !important;
        border: 2px solid rgba(99, 102, 241, 0.3) !important;
    }

    /* Divider */
    hr {
        border-color: rgba(99, 102, 241, 0.2) !important;
        margin: 2rem 0 !important;
    }

    /* Link styling */
    a {
        color: #a5b4fc !important;
        text-decoration: none !important;
        transition: all 0.3s ease !important;
        font-weight: 500 !important;
    }

    a:hover {
        color: #c7d2fe !important;
        text-shadow: 0 0 10px rgba(165, 180, 252, 0.5) !important;
    }

    /* Markdown content in chat */
    .stMarkdown {
        color: #e5e7eb !important;
    }

    .stMarkdown p {
        color: #e5e7eb !important;
        line-height: 1.7 !important;
    }

    .stMarkdown li {
        color: #e5e7eb !important;
    }

    .stMarkdown strong {
        color: #f0f0f0 !important;
        font-weight: 700 !important;
    }

    .stMarkdown em {
        color: #d1d5db !important;
    }

    /* Blockquotes */
    blockquote {
        border-left: 4px solid #8B5CF6 !important;
        padding-left: 1rem !important;
        color: #d1d5db !important;
        background: rgba(139, 92, 246, 0.1) !important;
        border-radius: 4px !important;
        margin: 1rem 0 !important;
    }

    /* Lists */
    ul, ol {
        color: #e5e7eb !important;
    }

    li::marker {
        color: #a5b4fc !important;
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
