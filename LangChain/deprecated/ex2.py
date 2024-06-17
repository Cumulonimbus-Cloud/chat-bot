import bs4
from langchain import hub
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma, FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from typing import List
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import ChatPromptTemplate




# 단계 1: 문서 로드(Load Documents)
# 뉴스기사 내용을 로드하고, 청크로 나누고, 인덱싱합니다.

## URL 문서 load
# url = "https://n.news.naver.com/article/437/0000378416"
# loader = WebBaseLoader(
#     web_paths=(url,),
#     bs_kwargs=dict(
#         parse_only=bs4.SoupStrainer(
#             "div",
#             attrs={"class": ["newsct_article _article_body", "media_end_head_title"]},
#         )
#     ),
# )
# docs = loader.load()
# source = url

pdf_filepath = "/home/Chatbot/LangChain/assets/컴퓨터공학과_2024학년도 대학안내.pdf"
source = pdf_filepath

loader = PyPDFLoader(pdf_filepath)
docs = loader.load()

# # 개행문자 '\n' 를 ' ' 로 대체
# def replace_newlines_with_spaces(documents: List[Document]) -> List[Document]:
#     for doc in documents:
#         doc.page_content = doc.page_content.replace('\n', ' ')
#     return documents

# # Apply the function to the data
# docs = replace_newlines_with_spaces(docs)

####################
# PDF를 그대로 RAG하는 것보다 마크다운 형식으로 변환 후 RAG하면 성능이 더 좋음
# import pymupdf4llm
# md_text = pymupdf4llm.to_markdown("input.pdf")
####################


# 단계 2: 문서 분할(Split Documents)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=50)

splits = text_splitter.split_documents(docs)


# 단계 3: 임베딩 & 벡터스토어 생성(Create Vectorstore)
# 벡터스토어를 생성합니다.

# embeddings = HuggingFaceEmbeddings(
#     model_name="BAAI/bge-m3",
#     model_kwargs = {'device': 'cuda'}, # 모델이 CPU에서 실행되도록 설정. GPU를 사용할 수 있는 환경이라면 'cuda'로 설정할 수도 있음
#     encode_kwargs = {'normalize_embeddings': True}, # 임베딩 정규화. 모든 벡터가 같은 범위의 값을 갖도록 함. 유사도 계산 시 일관성을 높여줌
# )

embeddings = OllamaEmbeddings( model = "Llama-3-Open-Ko-8B-FP16:latest")

vectorstore = FAISS.from_documents(splits,
                                   embedding = embeddings
                                  )

# # 임베딩 결과값을 로컬에 DB 저장
# MY_FAISS_INDEX = "MY_FAISS_INDEX"
# vectorstore.save_local(MY_FAISS_INDEX)

# 단계 4: 검색(Search)
# 뉴스에 포함되어 있는 정보를 검색하고 생성합니다.
# 리트리버는 구조화되지 않은 쿼리가 주어지면 문서를 반환하는 인터페이스입니다.
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 8})


# 단계 5: 프롬프트 생성(Create Prompt)
# 프롬프트를 생성합니다.
# prompt = hub.pull("rlm/rag-prompt")
# print(type(prompt))

# 단계 6: 언어모델 생성(Create LLM)
# 모델(LLM) 을 생성합니다.
llm = ChatOllama(model="Llama-3-Open-Ko-8B-FP16:latest")




def format_docs(docs):
    # 검색한 문서 결과를 하나의 문단으로 합쳐줍니다.
    return "\n\n".join(doc.page_content for doc in docs)


# 단계 7: 체인 생성(Create Chain)

## 7-1: 프롬프트 임의 생성
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful, professional assistant named 효봇. Introduce yourself first, and answer the questions."),
    ("user", "{question}")
])


## 7-2: rag chain 생성
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 단계 8: 체인 실행(Run Chain)
# 문서에 대한 질의를 입력하고, 답변을 출력합니다.
question = "컴퓨터및 기초학문 교육에 대해 알려줘."

print("rag_chain: ", rag_chain)


response = rag_chain.invoke(question)



# 결과 출력
print(f"source: {source}")
print(f"문서의 수: {len(docs)}")
print("===" * 20)
print(f"[HUMAN]\n{question}\n")
print(f"[AI]\n{response}")