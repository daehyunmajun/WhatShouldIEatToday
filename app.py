import os
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    req = request.get_json()
    
    # 1. 카카오톡이 보낸 컨텍스트 리스트 가져오기
    contexts = req.get("contexts", [])
    
    # 컨텍스트 '이름'들만 추출해서 리스트로 만듭니다.
    context_names = [ctx.get("name") for ctx in contexts]
    
    # 2. 유저의 선택값 한글로 매칭하기 (기본값 세팅)
    cuisine = "아무거나"
    if "step1_korean" in context_names: cuisine = "한식"
    elif "step1_western" in context_names: cuisine = "양식"
    elif "step1_chinese" in context_names: cuisine = "중식"
    elif "step1_japanese" in context_names: cuisine = "일식"

    taste = "상관없음"
    if "step2_spicy" in context_names: taste = "매운것"
    elif "step2_mild" in context_names: taste = "안매운것"

    carb = "상관없음"
    if "step3_bread" in context_names: carb = "빵"
    elif "step3_rice" in context_names: carb = "밥"
    elif "step3_noodle" in context_names: carb = "면"
    elif "step3_ricecake" in context_names: carb = "떡"

    temp = "상관없음"
    if "step4_hot" in context_names: temp = "뜨거운것"
    elif "step4_cold" in context_names: temp = "차가운것"

    # 3. GPT 프롬프트 작성
    prompt = (
        f"사용자가 다음과 같은 4가지 조건으로 음식을 먹고 싶어해:\n"
        f"1. 음식 종류: {cuisine}\n"
        f"2. 맵기: {taste}\n"
        f"3. 주성분: {carb}\n"
        f"4. 온도감: {temp}\n\n"
        f"이 4가지 조건을 완벽하게 만족하는 음식 메뉴 하나를 추천해주고, "
        f"왜 이 메뉴를 추천하는지 친절하고 센스 있는 카카오톡 챗봇 말투로 150자 이내로 대답해줘."
    )

    try:
        # 4. OpenAI API 호출
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 사용자의 취향을 분석해 최고의 식사 메뉴를 찾아주는 맞춤형 요정이야."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200
        )
        ai_answer = response.choices[0].message.content
    except Exception as e:
        ai_answer = f"메뉴를 고르던 중 주방에서 오류가 났어요! ({str(e)})"

    # 5. 카카오톡 응답 포맷
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
