import json

import boto3
from langchain_community.document_loaders import CSVLoader, PyPDFLoader

def printJson(dataObj):
    print(json.dumps(dataObj, sort_keys=True, indent=4))


bedrock = boto3.client(service_name="bedrock", region_name="us-east-1")
pdf_path = '~/environment/Chatbot/0616_tmp/pdf_score.pdf'
loader = PyPDFLoader(pdf_path)
docs = loader.load()

bedrock_runtime = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")
question = "내가 총 몇학점을 수강했어?"
body = json.dumps({"prompt": question})
response = bedrock_runtime.invoke_model(body=body, modelId="meta.llama3-70b-instruct-v1:0")
response_body = json.loads(response.get("body").read())
print(response_body["generation"])

pdf_text = "\n".join([doc.page_content for doc in docs])
combined_prompt = f"{pdf_text}\n\n질문: {question}\n이 질문에 한국어로 답해 주세요."

# llama 파라미터 시그니처
body = json.dumps(
    {
        "prompt": question,
        "temperature": 0.2,
        "top_p": 0.3,  # vs. topP in titan
        "max_gen_len": 512,
    }
)
