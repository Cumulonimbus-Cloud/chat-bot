from flask import Flask, request, jsonify, send_file
from datetime import datetime
from transcript_for_grade_card import pdf_to_csv
from langchain_community.document_loaders import CSVLoader

import json, os, boto3

app = Flask(__name__)


bedrock = boto3.client(service_name="bedrock", region_name="us-east-1")
bedrock_runtime = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")
dynamodb_client = boto3.client('dynamodb')  # DynamoDB 클라이언트 객체 생성

s3_client = boto3.client('s3')
BUCKET_NAME = 'inha-team-04-prod-s3'


def json_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def get_latest_file(bucket_name, prefix):
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    if 'Contents' not in response:
        return None

    # 가장 최근에 수정된 파일 찾기
    latest_file = max(response['Contents'], key=lambda x: x['LastModified'])
    return latest_file['Key']
    
    
@app.route('/ask', methods=['POST'])
def ask():
    try:
        user_question = request.json.get('question')
        user_id = request.json.get('userId')  # 사용자 ID 받기
        
        if not isinstance(user_id, int):
            return jsonify({"error": "userId must be an integer"}), 400
        prefix = f"grade_card/{user_id}/"
        latest_file_key = get_latest_file(BUCKET_NAME, prefix)
        if not latest_file_key:
            return jsonify({"message": "No files found"}), 404
        
        # S3에서 최신 파일 가져오기
        file_obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=latest_file_key)
        csv_content = file_obj['Body'].read().decode('utf-8')
        
        # csv_content를 모델에 넣을 수 있는 형식으로 변환
        score_text1 = csv_content  # 여기서는 간단히 csv 내용을 텍스트로 사용
        
        # data for curriculum
        curri_reg_path = "/home/ec2-user/environment/Chatbot/0616_tmp/assets/2023_graduated_regulation.csv"
        curri_map_path = "/home/ec2-user/environment/Chatbot/0616_tmp/assets/curriculum_map.csv"
        total_score_path = "/home/ec2-user/environment/Chatbot/0616_tmp/assets/total_score_Hwang.csv" # total_score
        summary_score_path = "/home/ec2-user/environment/Chatbot/0616_tmp/assets/summary_score_Hwang.csv" # summary_score
        
        load1 = CSVLoader(curri_reg_path)
        doc1 = load1.load()
        load2 = CSVLoader(curri_map_path)
        doc2 = load2.load()
        docs = doc1 + doc2
        score_text2 = " ".join([doc.page_content for doc in docs])
        
        load_tsp = CSVLoader(total_score_path)
        total_score = load_tsp.load()
        load_ssp = CSVLoader(summary_score_path)
        summary_score = load_ssp.load()
        
        question = f"""context: {score_text1}\n\n내가 방금 제공한 context는 사용자의 성적표를 담은 csv형식의 데이터야.
                \n그리고 아래에 컴퓨터공학과의 수업 커리큘럼과 졸업요건을 담은 csv형식의 데이터를 줄게. \n{score_text2}
                \n\n그리고 다음은 금학기 이수 내역을 제외하고 사용자가 지금까지 이수한 전체 수업 학점에 대한 데이터를 csv형식으로 담은 파일이야. \n {total_score}
                \n\n그리고 다음은 사용자가 지금까지 이수한 교선, 교필, 전선, 전필, 일선, 교직의 총 학점의 데이터를 담고있어. 교선은 교양 선택, 교필은 교양 필수, 전선은 전공 선택, 전필은 전공 필수, 일선은 일반 선택, 교직은 교직을 의미해. \n{summary_score}
                \n\n두 파일 모두 첫 번째 줄은 다음의 각 행들에 대한 열 정보를 나타내고 있어. 이를 잘 참고해서 다음 질문에 대해 대답을 해줘. \n\n{user_question}
                """
        
        question_prefix = "Human:\n"
        question_suffix = "\n\nAssistant:"
        question = question_prefix + question + question_suffix
        
        # Claude parameter signature
        body = {
            "prompt": question,
            "max_tokens_to_sample": 700,
            "temperature": 0.05,
            "top_k": 100,
            "top_p": 0.25,
            "anthropic_version": "bedrock-2023-05-31"
        }
        
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
        
        dynamodb_client.put_item(
            TableName="inha-team-04-chat-messages",
            Item=item_data
        )
        
        return jsonify({"response": answer})
    
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@app.route('/chat_history', methods=['GET'])
def chat_history():
    try:
        user_id = request.args.get('userId')  # GET 요청에서는 request.args 사용

        if user_id is None or not user_id.isdigit():
            return jsonify({"error": "userId must be an integer"}), 400

        # 특정 사용자의 채팅 내역을 시간 순서대로 쿼리
        response = dynamodb_client.query(
            TableName="inha-team-04-chat-messages",
            KeyConditionExpression='id = :id_value',
            ExpressionAttributeValues={
                ':id_value': {'N': str(user_id)}  # 숫자 타입으로 전달
            },
            ScanIndexForward=True  # 시간 순서대로 정렬 (오름차순)
        )
        items = response['Items']
        
        return jsonify({"chat_history": items})
    
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
        




@app.route('/upload_grade_card', methods=['POST'])
def upload_csv():
    user_id = request.form.get('userId')
    file = request.files['file']
    if not file or not user_id:
        return jsonify({"message": "File or userId missing"}), 400

    # 임시 파일 경로 설정
    pdf_path = os.path.join('uploads', f"{user_id}_{file.filename}")
    csv_filename = f"{user_id}_transcript.csv"
    csv_path = os.path.join('uploads', csv_filename)

    # 업로드 디렉터리 생성
    os.makedirs('uploads', exist_ok=True)

    # PDF 파일 저장
    file.save(pdf_path)

    # PDF 파일을 CSV로 변환
    pdf_to_csv(pdf_path, csv_path)

    # CSV 파일을 S3에 업로드
    s3_file_path = f"grade_card/{user_id}/{csv_filename}"
    s3_client.upload_file(csv_path, BUCKET_NAME, s3_file_path)

    # 파일 URL 생성
    file_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_file_path}"
    
    # 로컬에 저장된 파일 삭제 (선택 사항)
    os.remove(pdf_path)
    os.remove(csv_path)

    return jsonify({"message": "File uploaded successfully", "url": file_url}), 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
