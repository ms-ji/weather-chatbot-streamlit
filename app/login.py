import streamlit as st
import streamlit_authenticator as stauth
import yaml
from pathlib import Path

def login_gate(config_path: str = "config.yaml"):
    base_dir = Path(__file__).resolve().parent
    config_file = (base_dir / config_path).resolve()

    if not config_file.exists():
        st.error(f"config.yaml을 찾을 수 없습니다: {config_file}")
        st.stop()

    with open(config_file, "r", encoding="utf-8") as file:
        config = yaml.load(file, Loader=stauth.SafeLoader)

    authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
        config.get("preauthorized", None),
    )

    with st.sidebar:
        authenticator.login(location="sidebar", fields={"Form name": "Login"})

    # 상태는 session_state에서 읽기
    name = st.session_state.get("name")
    authentication_status = st.session_state.get("authentication_status")
    username = st.session_state.get("username")

    ok = True if authentication_status else False if authentication_status is False else None
    return authenticator, name, ok, username
