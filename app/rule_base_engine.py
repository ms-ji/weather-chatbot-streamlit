import datetime as dt

def rule_based_reply(user_text:str,temperature:float)->str:
    """
       반환값:
         handled: bool      -> 규칙으로 처리했는지 여부
         reply: str         -> 규칙 답변 텍스트
         intent: str | None -> 'weather' 처리용
    """
    t = user_text.strip().lower()

    weather_triggers = ["날씨", "오늘 날씨", "날씨 알려줘","기온","몇도야?","날씨 알려줘"]

    if t in weather_triggers:
        # 버튼은 아래 chat_message 블록에 그리고
        # intent로 'weather' 넘겨주기
        return True, "어느 지역의 날씨가 궁금하세요? 아래 버튼을 눌러주세요.", "weather"

    if any(k in t for k in ['안녕','hello','hi']):
        return True,'안녕하세요! 무엇을 도와드릴까요', None

    if '시간' in t or '현재 시각' in t:
        now = dt.datetime.now().strftime('%y-%m-%d %H:%M:%S')
        return True,f'현재 시간은 **{now}** 입니다.', None


    # 기본 : 에코 + 톤 조절(temperature > 0.6 이면 💬)
    tail = "💬" if temperature > 0.6 else ""
    return False,f'말씀하신 내용: **{user_text}** {tail}', None
