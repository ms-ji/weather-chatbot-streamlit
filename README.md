## 🌤️ Weather Chatbot (Streamlit)

로그인 기반 · 사용량 제한 · 실시간 날씨 조회가 가능한 AI 챗봇 웹 애플리케이션

### 📌 프로젝트 소개

이 프로젝트는 Streamlit 기반의 날씨 챗봇 서비스로
사용자 인증, 대화 상태 관리, Redis 기반 사용량 제한, 외부 API 연동까지 포함한
실사용을 고려한 웹 애플리케이션입니다.

- 로그인 여부에 따른 기능 제한
- 사용자별 24시간 채팅 횟수 제한
- 새로고침 시 로그인 유지 / 대화 초기화
- 배포 환경을 고려한 환경 변수 관리
- 실제 서비스 운영 시 발생하는 문제들을 직접 해결하는 것을 목표로 제작

### ✨ 주요 기능
#### 🔐 로그인 / 인증

streamlit-authenticator를 이용한 사용자 로그인
쿠키 기반 인증으로 새로고침 시 로그인 상태 유지
사용자 변경 시 이전 채팅 내역 자동 초기화

#### 💬 AI 챗봇

OpenAI API를 활용한 자연어 응답
시스템 프롬프트 및 응답 온도(창의성) 조절 가능

#### 📅 규칙 기반 응답 기능

다음과 같은 질문은 모델 호출 없이 규칙 기반으로 처리합니다.

- 현재 시간 제공
- 간단한 인사 응답

#### 🌤️ 날씨 조회

특정 키워드 입력 시 날씨 모드 활성화
지역 버튼 선택으로 현재 날씨 정보 조회
외부 Weather API 연동

#### ⏳ 사용량 제한 (Redis)

Redis(Upstash) 기반 사용자별 채팅 횟수 저장
첫 사용 시점부터 24시간 동안 최대 5회 제한
TTL(Time To Live)을 활용한 자동 초기화
사용자별 남은 / 사용 횟수 실시간 표시

### 🔄 UX 설계

- 새로고침 시
  - 로그인 상태 유지
  - 대화 내용 초기화
  - 챗봇 인사 메시지 자동 출력
- 로그인하지 않은 경우 채팅 차단 안내 메시지 제공

### 🛠️ 기술 스택
**구분	기술**
- Frontend	Streamlit
- Authentication	streamlit-authenticator
- AI	OpenAI API
- Storage	Redis (Upstash)
- External API	Weather API
- Deployment	Streamlit Cloud
- Language	Python

### 🧩 시스템 구조 요약

- 로그인 상태: 쿠키 기반 인증
- 대화 내용: st.session_state (세션 단위)
- 채팅 횟수: Redis (사용자별 키 + TTL)
- 환경 변수 관리: Streamlit Secrets / 환경 변수

### 🌐 배포

- Streamlit Cloud를 이용한 배포
- 민감 정보(API Key, Redis URL)는 Secrets를 통해 관리
- .env, venv, 키 파일은 GitHub에 업로드하지 않음
