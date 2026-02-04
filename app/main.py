from openai import OpenAI
import streamlit as st
import time

from login import login_gate

from config import OPENAI_KEY, WEATHER_KEY
from geocoding import get_single_coordinate
from llm_engine import llm_reply
from rule_base_engine import rule_based_reply
from weather import get_current_weather
from usage_limit import DAILY_LIMIT, consume_24h, get_remaining_24h

# 클라이언트 생성
client = OpenAI(api_key=OPENAI_KEY)

st.set_page_config(page_title='Weather챗봇',page_icon="✨")
st.title("✨챗봇")

WELCOME_MESSAGE = "안녕하세요! ✨ 무엇을 도와드릴까요?"

#--------------------------------------------
# 로그인 기능
#--------------------------------------------
authenticator, name, ok, username = login_gate("config.yaml")

# 로그 아웃 클릭 시 
if ok:
    logout_clicked = authenticator.logout("Logout", "sidebar")
    st.sidebar.title(f"Welcome {name}")

    if logout_clicked:
        for k in ['messages', 'weather_mode']:
            st.session_state.pop(k, None)
        st.rerun()

else:
    st.sidebar.info("로그인 후 이용 가능합니다.")


# 로그인 성공 후, 유저 변경 감지해서 세션 초기화
prev_user = st.session_state.get("active_username")

if ok is True:
    if prev_user != username:
        # 유저가 바뀌었으면 채팅 세션 초기화
        for k in ["messages", "weather_mode"]:
            st.session_state.pop(k, None)
        st.session_state["active_username"] = username
        st.rerun()
else:
    # 로그아웃 상태면 active_username 제거
    st.session_state.pop("active_username", None)

#--------------------------------------------
# 하루 채팅 횟수 초기화
#--------------------------------------------
if ok is True:
    left = get_remaining_24h(username)
    st.sidebar.caption(f"24시간 사용한 채팅:  {DAILY_LIMIT - left}  / {DAILY_LIMIT}")

#---------------------------------------------
# 사이드 바 : 시스템 프롬프트, 온도, 초기화 버튼
#---------------------------------------------
with st.sidebar:
    st.markdown("### 🌤️ 날씨 기능 안내")
    st.markdown(
        """
        아래 문장을 입력하면 **지역 선택 버튼**으로  
        원하는 지역의 날씨를 조회할 수 있어요!

        **사용 가능한 문장 예시**
        - `"날씨"`
        - `"오늘 날씨"`
        - `"날씨 알려줘"`
        - `"기온"`
        - `"몇 도야?"`

        👉 이 표현들을 입력하면 날씨 조회 모드가 자동으로 실행됩니다.
        """
    )
    st.divider() # 선
    system_prompt = st.text_area(
        label="시스템 프롬프트",
        value='당신은 친절한 도우미 입니다. 간결하게 답변하세요.',
        height=150,
        max_chars=300
    )
    temperature = st.slider(label="창의성",
                            min_value=0.0,
                            max_value=1.0,
                            step=0.1,
                            value=0.5)
    if st.button('대화 초기화') == True:
        #st.session_state.clear()
        for k in ['messages', 'weather_mode']:
            st.session_state.pop(k, None)
        st.rerun()


#--------------------------------------------------
# 세션 상태 초기화
#--------------------------------------------------
if 'messages' not in st.session_state:
   st.session_state.messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'assistant', 'content': WELCOME_MESSAGE},
    ]

if 'weather_mode' not in st.session_state:
    st.session_state.weather_mode = False

# system_prompt 가 변경되면 최신화
st.session_state.messages[0]["content"] = system_prompt


#--------------------------------------------------
# 대화 렌더링(system은 숨김)
#--------------------------------------------------
for m in st.session_state.messages:
   if m['role'] == 'system':
      continue
   with st.chat_message(m['role']):
      st.markdown(m['content'])

#--------------------------------------------------
# 메세지(질문) 입력
#--------------------------------------------------
prompt = st.chat_input('메시지를 입력하세요.')

if prompt:
    # 0) 먼저 사용자 입력은 화면에 보여주고
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    with st.chat_message('user'):
        st.markdown(prompt)

    # 1) 로그인 안 했으면 여기서 종료
    if ok is not True:
        login_msg = "🔒 로그인을 하세요."
        with st.chat_message('assistant'):
            st.markdown(login_msg)
        st.session_state.messages.append({'role': 'assistant', 'content': login_msg})
        st.stop()  # 아래 LLM/날씨 로직 실행 막기

    # 하루 5회 제한 체크
    key_cnt = f"chat_count_{username}"
    used = st.session_state.get(key_cnt, 0)

    # 24시간 5회 제한 (Redis)
    allowed, left = consume_24h(username)
    if not allowed:
        limit_msg = f" 24시간 동안 사용 가능 횟수({DAILY_LIMIT}회)를 모두 사용했어요. 잠시 후 다시 이용해 주세요!"
        with st.chat_message('assistant'):
            st.markdown(limit_msg)
        st.session_state.messages.append({'role': 'assistant', 'content': limit_msg})
        st.stop()

    st.sidebar.caption(f"24시간 남은 채팅: {left} / {DAILY_LIMIT}")

    # 여기까지 통과하면 1회 차감(카운트 +1)
    st.session_state[key_cnt] = used + 1
    # 2) 어시스턴트 답변
    handled, rule_reply, intent = rule_based_reply(prompt, temperature)

    with st.chat_message('assistant'):
       if handled and intent == "weather":
           # 안내 멘트만 출력하고, weather_mode 켜두기
           st.markdown(rule_reply)
           st.session_state.messages.append({
               'role': 'assistant',
               'content': rule_reply
           })
           st.session_state.weather_mode = True
       else:
           # 일반 규칙/LLM 응답
           placeholder = st.empty()
           if handled:
               full_text = rule_reply
           else:
               full_text = llm_reply(system_prompt,client, st.session_state.messages,temperature)

           streamed = ""
           for char in full_text:
               streamed += char
               placeholder.markdown(streamed)
               time.sleep(0.01)

           st.session_state.messages.append({
               'role': 'assistant',
               'content': full_text
           })
#---------------------------------------------------
# 날씨 선택 모드 처리 (버튼 + 날씨 조회)
#---------------------------------------------------
if st.session_state.weather_mode:
    with st.chat_message("assistant"):
        #st.markdown("어느 지역의 날씨가 궁금하세요? 아래 버튼을 눌러주세요.")
        regions = [
            ("서울특별시", "서울"),
            ("부산광역시", "부산"),
            ("대구광역시", "대구"),
            ("인천광역시", "인천"),
            ("광주광역시", "광주"),
            ("대전광역시", "대전"),
            ("울산광역시", "울산"),
            ("세종특별자치시", "세종"),
            ("경기도", "수원"),
            ("강원특별자치도", "춘천"),
            ("충청북도", "청주"),
            ("충청남도", "홍성"),
            ("전북특별자치도", "전주"),
            ("전라남도", "무안"),
            ("경상북도", "안동"),
            ("경상남도", "창원"),
            ("제주특별자치도", "제주"),
        ]

        cols = st.columns(3)
        city = None
        city_label = None

        for i,(label,query_name) in enumerate(regions):
            col = cols[i%3]
            with col:
                if st.button(label,key=f"region_{i}"):
                    city = query_name
                    city_label = label

        # 버튼이 실제로 눌렸을 때만
        if city is not None:
            if not WEATHER_KEY:
                weather_text = "⚠️ WEATHER_API_KEY가 설정되어 있지 않습니다."
            else:
                lat, lon = get_single_coordinate(
                    city_name=city,
                    country_code="KR",
                    api_key=WEATHER_KEY
                )
                if lat and lon:
                    w = get_current_weather(lat, lon, WEATHER_KEY)
                    if w:
                        weather_text = (
                            f"**{city_label} 현재 날씨**\n\n"
                            f"- 위치: {w['location']} ({w['country']})\n"
                            f"- 상태: {w['description']}\n"
                            f"- 기온: {w['temperature']}°C (체감 {w['feels_like']}°C)\n"
                            f"- 습도: {w['humidity']}%\n"
                            f"- 기압: {w['pressure']} hPa\n"
                            f"- 풍속: {w['wind_speed']} m/s\n"
                        )
                    else:
                        weather_text = "날씨 정보를 가져오지 못했습니다."
                else:
                    weather_text = "해당 도시의 좌표를 찾지 못했습니다."

            st.markdown(weather_text)
            st.session_state.messages.append({
                'role': 'assistant',
                'content': weather_text
            })

            # 모드 종료 후 다시 렌더링
            st.session_state.weather_mode = False
            st.rerun()















