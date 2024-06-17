from flask import Flask, request, jsonify
import json
import boto3
from datetime import datetime

app = Flask(__name__)

dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')  # DynamoDB 클라이언트 객체 생성

def json_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

@app.route('/ask', methods=['POST'])
def ask():
    try:
        user_question = request.json.get('question')
        user_id = request.json.get('userId')  # 사용자 ID 받기

        if not isinstance(user_id, int):
            return jsonify({"error": "userId must be an integer"}), 400
        
        # 더미 데이터로 context 설정
        score_text1 = "dummy score text from CSV"
        score_text2 = "dummy curriculum map text from CSV"
        
        question = f"""context: {score_text1}\n\n내가 방금 제공한 context는 사용자의 성적표를 담은 csv형식의 데이터야.
                \n그리고 아래에 컴퓨터공학과의 수업 커리큘럼을 담은 csv형식의 데이터를 줄게. \n{score_text2}
                \n\n두 파일 모두 첫 번째 줄은 다음의 각 행들에 대한 열 정보를 나타내고 있어. 이를 잘 참고해서 다음 질문에 대해 대답을 해줘. \n\n{user_question}"""
        
        question_prefix = "Human:\n"
        question_suffix = "\n\nAssistant:"
        question = question_prefix + question + question_suffix
        
        # Claude parameter signature
        body = {
            "prompt": question,
            "max_tokens_to_sample": 600,
            "temperature": 0.1,
            "top_k": 60,
            "top_p": 0.5,
            "anthropic_version": "bedrock-2023-05-31"
        }
        
        # Bedrock 모델 호출
        response = bedrock_runtime.invoke_model(
            body=json.dumps(body),
            modelId="anthropic.claude-v2",
            contentType="application/json"
        )
        
        response_body = json.loads(response['body'].read().decode('utf-8'))
        answer = response_body['completion']
        
        # DynamoDB에 질문과 답변 저장
        item_data = {
            'id': {'N': str(user_id)},  # 사용자 ID (숫자 타입으로 설정)
            'timestamp': {'N': str(int(datetime.now().timestamp()))},  # 현재 시간
            'message': {'S': answer},  # 시스템 메시지 (답변)
            'sender': {'S': 'bot'},  # 메시지 보낸 주체 (bot)
            'text': {'S': user_question}  # 사용자가 질문한 내용
        }
        
        # DynamoDB에 아이템 삽입
        dynamodb_client.put_item(
            TableName="inha-team-04-chat-messages",
            Item=item_data
        )
        
        return jsonify({"response": answer})
    
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
