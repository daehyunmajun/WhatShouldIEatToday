import os
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

# OpenAI 클라이언트 초기화 (Render 환경변수에서 API 키를 안전하게 가져옵니다)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    req = request.get_json()
    
    # 카카오톡 유저가 입력한 말(발화) 추출
    user_utterance = req.get("userRequest", {}).get("utterance", "")
    
    try:
        # OpenAI API 호출
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # 속도가 빠르고 가성비가 좋은 모델
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "너는 메뉴 선택의 요정이야. "
                        "메뉴를 고르고 고른 이유를 짧게 말해줘. 카카오톡 봇으로 쓰일 말투로 대답해줘."
                    )
                },
                {"role": "user", "content": user_utterance}
            ],
            max_tokens=200
        )
        ai_answer = response.choices[0].message.content
    except Exception as e:
        # 에러 발생 시 예외 처리
        ai_answer = f"주방이이 고장 났어요! (에러: {str(e)}) 다시 시도해주세요!"

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
    # Render 호스팅을 위해 포트를 환경변수에서 받도록 설정
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
