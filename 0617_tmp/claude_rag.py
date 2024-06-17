import json, pymupdf4llm

import boto3
from langchain_community.document_loaders import CSVLoader, PyPDFLoader
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

faiss_index_path = '/home/ec2-user/environment/chatbot/src/faiss_index'

def storeVectors():
    # graduate_regulation
    file_path_user_score = '/home/ec2-user/environment/chatbot/src/2024_graduated_regulation.csv'
    loader = CSVLoader(file_path_user_score)
    docs1 = loader.load()
    
    # curri_map
    file_path_curri_map = "/home/ec2-user/environment/chatbot/src/curriculum_map.csv"
    loader = CSVLoader(file_path_curri_map)
    docs2 = loader.load()
    
    #split texts
    docs = docs1 + docs2
    text_splitter = CharacterTextSplitter(chunk_size=66, chunk_overlap= 1)
    texts = text_splitter.split_documents(docs)
    
    # Vector store 생성
    vectorstore = FAISS.from_documents(
        documents = texts,
        embedding = HuggingFaceEmbeddings()
    )
    
    vectorstore.save_local(faiss_index_path)

def printJson(dataObj):
    print(json.dumps(dataObj, sort_keys=True, indent=4))

def app():
    bedrock = boto3.client(service_name="bedrock", region_name="us-east-1")
    
    bedrock_runtime = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")
    
    
    loaded_vec = FAISS.load_local(faiss_index_path, embedding=HuggingFaceEmbeddings())
    retriever = loaded_vec.as_retriever(search_type="similarity")
    
    my_question = input("질문: ")
    
    # Query Retrieval
    retrieved_docs = retriever.get_relevant_documents(my_question)
    retrieved_content = " ".join([doc.page_content for doc in retrieved_docs])
    
    # user_score
    file_path_user_score = '/home/ec2-user/environment/chatbot/src/contents_score_Hwang.csv'
    
    loader = CSVLoader(file_path_user_score)
    docs = loader.load()
    score_text = " ".join([doc.page_content for doc in docs])
    
    # Combine user score with retrieved documents for context
    full_context = f"""{score_text}\n\nAdditional Info:\n{retrieved_content}"""
    
    question = f"""
    context: {full_context}
    질문에 간결하게 필요한 정보만 제공하고, 배경 설명은 간략화시켜 줘.
    이를 잘 참고해서 다음 질문에 대해 대답을 해줘.
    {my_question}
    """
    
    
    question_prefix = "Human:\n"
    question_suffix = "\n\nAssistant:"
    full_prompt = question_prefix + question + question_suffix
    
    # claude 파라미터 시그니처
    body = json.dumps({
        "prompt": full_prompt,
        "max_tokens_to_sample":700,
        "temperature":0.05,
        "top_k":100,
        "top_p":0.25,
        "anthropic_version":"bedrock-2023-05-31"
        })
    
    
    response = bedrock_runtime.invoke_model(body=body, modelId="anthropic.claude-v2:1")
    
    response_body = json.loads(response.get("body").read())
    
    print(response_body['completion'])

if __name__ == "__main__":
    storeVectors()