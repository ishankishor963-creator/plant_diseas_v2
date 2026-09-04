"""
auth.py
-------
Single shared-password gate for the whole app (not per-user accounts —
this is a one-farm app, so one password for everyone with the link is
enough). Call `require_login()` at the very top of Home.py, before
anything else renders.

SETTING THE PASSWORD
Add this to `.streamlit/secrets.toml` (create the file if it doesn't
exist — never commit it to git):

    APP_PASSWORD = "your-password-here"

If no APP_PASSWORD secret is set, the app falls back to the demo
password "farm2026" and shows a small notice so you don't get locked
out during local development — set the real secret before deploying
anywhere public.
"""

import streamlit as st

DEMO_FALLBACK_PASSWORD = "farm2026"


def _get_configured_password() -> str:
    try:
        return st.secrets.get("APP_PASSWORD", DEMO_FALLBACK_PASSWORD)
    except Exception:
        return DEMO_FALLBACK_PASSWORD


def _render_login_screen():
    from utils.theme import inject_theme  # local import avoids circularity

    inject_theme()

    st.markdown(
        """
        <div style="max-width:420px;margin:8vh auto 0 auto;text-align:center;">
            <div style="font-family:'Space Grotesk',sans-serif;font-weight:700;
                        font-size:1.6rem;color:#eef0f7;display:flex;align-items:center;
                        justify-content:center;gap:0.6rem;margin-bottom:0.3rem;">
                <span style="width:12px;height:12px;border-radius:50%;
                             background:linear-gradient(135deg,#22d3ee,#8b5cf6);
                             box-shadow:0 0 12px #8b5cf6;"></span>
                AgroSentry
            </div>
            <div style="color:#7d7c94;font-size:0.9rem;margin-bottom:1.6rem;">
                Farm Ops Dashboard &mdash; enter the shared access code to continue
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, mid, _ = st.columns([1, 1.3, 1])
    with mid:
        with st.container(border=True):
            st.markdown('<div class="card-marker"></div>', unsafe_allow_html=True)
            pw = st.text_input("Access code", type="password", key="login_pw")
            if _get_configured_password() == DEMO_FALLBACK_PASSWORD:
                st.caption(
                    f'ℹ️ No APP_PASSWORD secret set yet — using the demo code '
                    f'"{DEMO_FALLBACK_PASSWORD}". Set a real one in secrets.toml '
                    f'before sharing this app.'
                )
            if st.button("Enter dashboard", type="primary", use_container_width=True):
                if pw == _get_configured_password():
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("Incorrect access code — try again.")


def require_login():
    """Blocks the whole app until the correct shared password is entered."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.set_page_config(
            page_title="AgroSentry — Sign in",
            page_icon="\U0001F33E",
            layout="wide",
            initial_sidebar_state="collapsed",
        )
        _render_login_screen()
        st.stop()


def logout_button():
    if st.sidebar.button("\U0001F6AA Log out", use_container_width=True):
        st.session_state["authenticated"] = False
        st.rerun()
