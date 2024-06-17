from flask import Flask, request, jsonify
import json
import boto3
from langchain_community.document_loaders import CSVLoader

app = Flask(__name__)

bedrock = boto3.client(service_name="bedrock", region_name="us-east-1")
bedrock_runtime = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")

def load_csv(file_path):
    loader = CSVLoader(file_path)
    docs = loader.load()
    return " ".join([doc.page_content for doc in docs])

@app.route('/ask', methods=['POST'])
def ask():
    try:
        user_question = request.json.get('question')
        
        # user_score
        file_path_user_score = '/home/ec2-user/environment/Chatbot/0616_tmp/contents_uk.csv'
        score_text1 = load_csv(file_path_user_score)
        
        # curri_map
        file_path_curri_map = "/home/ec2-user/environment/Chatbot/0616_tmp/curriculum_map.csv"
        score_text2 = load_csv(file_path_curri_map)
        
        question = f"""context: {score_text1}\n\n내가 방금 제공한 context는 사용자의 성적표를 담은 csv형식의 데이터야.
                \n그리고 아래에 컴퓨터공학과의 수업 커리큘럼을 담은 csv형식의 데이터를 줄게. \n{score_text2}
                \n\n두 파일 모두 첫 번째 줄은 다음의 각 행들에 대한 열 정보를 나타내고 있어. 이를 잘 참고해서 다음 질문에 대해 대답을 해줘. \n\n{user_question}"""
        
        question_prefix = "Human:\n"
        question_suffix = "\n\nAssistant:"
        question = question_prefix + question + question_suffix
        
        # claude 파라미터 시그니처
        body = json.dumps({
            "prompt": question,
            "max_tokens_to_sample": 600,
            "temperature": 0.1,
            "top_k": 60,
            "top_p": 0.5,
            "anthropic_version": "bedrock-2023-05-31"
        })
        
        response = bedrock_runtime.invoke_model(body=body, modelId="anthropic.claude-v2:1")
        response_body = json.loads(response.get("body").read())
        
        return jsonify({"response": response_body['completion']})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
