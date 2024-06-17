import json, pymupdf4llm

import boto3
from langchain_community.document_loaders import CSVLoader, PyPDFLoader
from langchain_community.document_loaders import UnstructuredMarkdownLoader

def printJson(dataObj):
    print(json.dumps(dataObj, sort_keys=True, indent=4))


bedrock = boto3.client(service_name="bedrock", region_name="us-east-1")

bedrock_runtime = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")

# graduate_regulation
file_path_user_score = '/home/ec2-user/environment/Chatbot/0616_tmp/assets/2024_graduated_regulation.csv'

loader = CSVLoader(file_path_user_score)
docs = loader.load()
graduate_regulation = " ".join([doc.page_content for doc in docs])

# user_score
file_path_user_score = '/home/ec2-user/environment/Chatbot/0616_tmp/assets/contents_score_Hwang.csv'

loader = CSVLoader(file_path_user_score)
docs = loader.load()
score_text1 = " ".join([doc.page_content for doc in docs])

# curri_map
file_path_curri_map = "/home/ec2-user/environment/Chatbot/0616_tmp/assets/curriculum_map.csv"

loader = CSVLoader(file_path_curri_map)
docs = loader.load()
score_text2 = " ".join([doc.page_content for doc in docs])


my_question = input("질문: ")

question = f"""context: {score_text1}\n\n내가 방금 제공한 context는 사용자의 성적표를 담은 csv형식의 데이터야.
            \n그리고 아래에 컴퓨터공학과의 수업 커리큘럼을 담은 csv형식의 데이터를 줄게. \n커리큘럼: {score_text2}
            \n\n 그리고 다음은 컴퓨터공학과의 졸업 요건을 담은 csv형식의 데이터야. \n졸업요건: {graduate_regulation}
            \n\n세 파일 모두 첫 번째 줄은 다음의 각 행들에 대한 열 정보를 나타내고 있어. 이를 잘 참고해서 다음 질문에 대해 대답을 해줘.
            \n\n 질문에 간결하게 필요한 정보만 제공하고, 배경설명은 간략화시켜줘.
            \n\n{my_question}"""


question_prefix = "Human:\n"
question_suffix = "\n\nAssistant:"
question = question_prefix + question + question_suffix

# claude 파라미터 시그니처
body = json.dumps({
    "prompt": question,
    "max_tokens_to_sample":600,
    "temperature":0.05,
    "top_k":100,
    "top_p":0.3,
    "anthropic_version":"bedrock-2023-05-31"
    })


response = bedrock_runtime.invoke_model(body=body, modelId="anthropic.claude-v2:1")

response_body = json.loads(response.get("body").read())

print(response_body['completion'])
