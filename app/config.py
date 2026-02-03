import os

# 로컬에서는 python-dotenv 있으면 .env 로드
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

def get_secret(key: str, default=None):
    """
    1) Streamlit 배포: st.secrets에서 먼저 읽고
    2) 로컬/서버: 환경변수(os.environ/.env)에서 읽음
    """
    try:
        import streamlit as st
        return st.secrets.get(key, os.getenv(key, default))
    except Exception:
        return os.getenv(key, default)

OPENAI_KEY = get_secret("OPENAI_KEY")
WEATHER_KEY = get_secret("WEATHER_KEY")

MODEL_NAME = "gpt-4o-mini"
DEFAULT_TEMP = 0.5

# 키 누락 시 바로 알림 
if not OPENAI_KEY:
    raise RuntimeError("OPENAI_KEY가 설정되어 있지 않습니다. (st.secrets 또는 환경변수/.env 확인)")
if not WEATHER_KEY:
    raise RuntimeError("WEATHER_KEY가 설정되어 있지 않습니다. (st.secrets 또는 환경변수/.env 확인)")
