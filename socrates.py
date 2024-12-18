#sk-1ZTrJ7URAOKym2HH5F7ne577XMX4lR6H_p_vvISgPJT3BlbkFJiMr9VSfeKGRTEDI_6RCYUKd5nW9b2psidyRx1JU1oA

import streamlit as st
from langchain.chat_models import ChatOpenAI
import json
import os
import random

# OpenAI API 키 설정
API_KEY = "sk-1ZTrJ7URAOKym2HH5F7ne577XMX4lR6H_p_vvISgPJT3BlbkFJiMr9VSfeKGRTEDI_6RCYUKd5nW9b2psidyRx1JU1oA"

# LangChain Chat 모델 초기화
def create_chat_model(temperature):
    return ChatOpenAI(temperature=temperature, openai_api_key=API_KEY)

# 파일 경로 관리
def get_file_path(file_name):
    if not os.path.exists("session_data"):
        os.makedirs("session_data")
    return f"session_data/{file_name}.json"

def load_json(file_name):
    file_path = get_file_path(file_name)
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

def save_json(file_name, data):
    file_path = get_file_path(file_name)
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# 초기 데이터 로드
def initialize():
    if not os.path.exists("session_data"):
        os.makedirs("session_data")
    if not os.path.exists(get_file_path("chat_history")):
        save_json("chat_history", [])
    if not os.path.exists(get_file_path("previous_chat_history")):
        save_json("previous_chat_history", [])

# 데이터 초기화 실행
initialize()

# 데이터 불러오기
def load_chat_history():
    return load_json("chat_history")

def save_chat_history(data):
    save_json("chat_history", data)

def load_previous_chat_history():
    return load_json("previous_chat_history")

def save_previous_chat_history(data):
    save_json("previous_chat_history", data)

# 질문 생성 함수
def generate_question(user_input, temperature):
    chat_model = create_chat_model(temperature)
    system_prompt = (
        "학생이 제공한 입력을 바탕으로 핵심 주제나 문장을 이해하고, 자연스러운 질문을 생성하세요. "
        "질문은 하나만 생성되어야 하며, 반복적인 패턴(예: '왜', '어떻게')을 피하도록 하세요. "
        "문법적으로 정확하고 맥락에 어긋나지 않는 질문을 작성하세요."
    )
    full_prompt = f"{system_prompt}\n\n입력: {user_input}"
    response = chat_model.predict(full_prompt)
    return response.strip()

# Streamlit UI 렌더링
def main():
    chat_history = load_chat_history()
    previous_history = load_previous_chat_history()

    # UI 헤더
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>소크라테스식 AI 튜터</h1>", unsafe_allow_html=True)

    # 온도 조정 슬라이더
    temperature = st.sidebar.slider("응답의 창의성 조정 (temperature)", 0.0, 1.0, 0.7, 0.1)

    # 메뉴 추가
    menu = st.sidebar.radio("메뉴", ["대화", "이전 기록"])

    if menu == "대화":
        # 대화 기록 출력
        st.markdown("### 대화 기록")
        if st.session_state.get("first_visit", True):
            st.session_state["first_visit"] = False
            # 첫 방문 시, 마지막 대화만 표시
            if chat_history:
                last_message = chat_history[-1]
                if last_message.get("role") == "user":
                    st.markdown(
                        f"<div style='text-align: left; background-color: #DCF8C6; color: #000; padding: 10px; border-radius: 15px; margin: 10px; display: inline-block; max-width: 80%;'>\U0001F464 {last_message.get('content', '')}</div>",
                        unsafe_allow_html=True
                    )
                elif last_message.get("role") == "assistant":
                    st.markdown(
                        f"<div style='text-align: left; background-color: #FFFBEB; color: #000; padding: 10px; border-radius: 15px; margin: 10px; display: inline-block; max-width: 80%;'>\U0001F916 {last_message.get('content', '')}</div>",
                        unsafe_allow_html=True
                    )
        else:
            # 이후 방문 시, 모든 대화 표시
            for message in chat_history:
                if message.get("role") == "user":
                    st.markdown(
                        f"<div style='text-align: left; background-color: #DCF8C6; color: #000; padding: 10px; border-radius: 15px; margin: 10px; display: inline-block; max-width: 80%;'>\U0001F464 {message.get('content', '')}</div>",
                        unsafe_allow_html=True
                    )
                elif message.get("role") == "assistant":
                    st.markdown(
                        f"<div style='text-align: left; background-color: #FFFBEB; color: #000; padding: 10px; border-radius: 15px; margin: 10px; display: inline-block; max-width: 80%;'>\U0001F916 {message.get('content', '')}</div>",
                        unsafe_allow_html=True
                    )

        # 사용자 입력 필드
        user_input = st.chat_input("말씀해주세요.")
        if user_input:
            if user_input.strip() == "/new":
                st.markdown("<p style='text-align: center; color: yellow;'>새로운 학습 내용을 입력하세요.</p>", unsafe_allow_html=True)
                save_previous_chat_history(chat_history)
                save_chat_history([])
                st.experimental_rerun()

            # 사용자 입력 처리
            chat_history.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            # 질문 생성 및 응답 처리
            try:
                ai_response = generate_question(user_input, temperature)
            except Exception as e:
                ai_response = f"오류가 발생했습니다: {e}"
            chat_history.append({"role": "assistant", "content": ai_response})
            with st.chat_message("assistant"):
                st.markdown(ai_response)

            # 업데이트된 데이터 저장
            save_chat_history(chat_history)

    elif menu == "이전 기록":
        st.markdown("### 이전 대화 기록")
        if not previous_history:
            st.markdown("<p>저장된 이전 대화 기록이 없습니다.</p>", unsafe_allow_html=True)
        else:
            for message in previous_history:
                if message.get("role") == "user":
                    st.markdown(
                        f"<div style='text-align: left; background-color: #DCF8C6; color: #000; padding: 10px; border-radius: 15px; margin: 10px; display: inline-block; max-width: 80%;'>\U0001F464 {message.get('content', '')}</div>",
                        unsafe_allow_html=True
                    )
                elif message.get("role") == "assistant":
                    st.markdown(
                        f"<div style='text-align: left; background-color: #FFFBEB; color: #000; padding: 10px; border-radius: 15px; margin: 10px; display: inline-block; max-width: 80%;'>\U0001F916 {message.get('content', '')}</div>",
                        unsafe_allow_html=True
                    )

if __name__ == "__main__":
    main()

# 스타일 추가
st.markdown("""
<style>
div[data-testid="stChatMessage"] {
    padding: 5px 0;
}
</style>
""", unsafe_allow_html=True)
