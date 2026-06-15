import os
import requests
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 실시간 날씨 정보를 가져오는 함수 (서울 기준)
def get_current_weather():
    try:
        # wttr.in 서비스를 이용해 서울의 현재 날씨 상태(%C)와 기온(%t)을 한글로 가져옵니다.
        # 카카오톡 5초 제한을 위해 타임아웃을 1.5초로 타이트하게 잡습니다.
        url = "https://wttr.in/Seoul?format=%C+(%t)&lang=ko"
        response = requests.get(url, timeout=1.5)
        
        if response.status_code == 200:
            return response.text.strip()
    except Exception:
        # 날씨 서버가 느리거나 에러가 나면 챗봇이 멈추지 않도록 기본값을 반환합니다.
        pass
    return "적당한 날씨"

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    req = request.get_json()
    
    # 카카오톡 유저가 입력한 말(발화) 추출
    user_utterance = req.get("userRequest", {}).get("utterance", "")
    
    # 1. 실시간 날씨 정보 가져오기 (예: "맑음 (+23°C)" 또는 "흐림 (+15°C)")
    current_weather = get_current_weather()
    
    try:
        # 2. OpenAI API 호출 (시스템 프롬프트에 실시간 날씨 주입)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        f"너는 메뉴 선택의 요정이야. 현재 실시간 날씨는 [{current_weather}]야. 온도는 섭씨로 얘기해줘"
                        "이 날씨 상태와 기온을 반드시 언급하면서, 오늘 날씨에 딱 어울리는 메뉴를 하나 고르고 "
                        "그 고른 이유를 친절하고 유쾌하게 설명해줘. "
                        "카카오톡 봇으로 쓰일 말투(~요, ~해보세요!)로 150자 이내로 짧게 대답해줘."
                    )
                },
                {"role": "user", "content": user_utterance}
            ],
            max_tokens=200
        )
        ai_answer = response.choices[0].message.content
    except Exception as e:
        ai_answer = f"주방이 고장 났어요! (에러: {str(e)}) 다시 시도해주세요!"

    # 카카오톡 스킬 규격에 맞는 JSON 응답 포맷
    res = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": ai_answer
                    }
                }
            ]
        }
    }
    return jsonify(res)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
