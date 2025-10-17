import streamlit as st
import hashlib
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def load_auth_credentials() -> dict:
    username = os.getenv("STREAMLIT_USERNAME", "admin")
    password = os.getenv("STREAMLIT_PASSWORD", "Bunzeroni1!")
    return {"username": username, "password_hash": hash_password(password)}


def check_authentication() -> bool:
    """Simple session-based authentication (no cookies, no persistence)."""
    # Check if already authenticated in this session
    if st.session_state.get("authenticated", False):
        return True

    # Show login form
    st.markdown("### 🔐 Authentication Required")
    st.info("Please login to access the MCP AI Assistant")
    credentials = load_auth_credentials()

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            if (
                username == credentials["username"]
                and hash_password(password) == credentials["password_hash"]
            ):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid username or password")
                return False

    st.caption(f"Default user: {credentials['username']}")
    st.caption("💡 Tip: Session lasts until you close the browser tab")
    return False


def logout():
    """Clear session authentication."""
    st.session_state.authenticated = False
    if "username" in st.session_state:
        del st.session_state.username
    st.rerun()


def show_logout_button():
    """Display logout button in sidebar."""
    if st.session_state.get("authenticated", False):
        username = st.session_state.get("username", "User")
        st.sidebar.caption(f"👤 {username}")
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            logout()
