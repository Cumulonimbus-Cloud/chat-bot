# 단계 1: 문서 로드(Load Documents)
from langchain_community.document_loaders import CSVLoader

# 단계 2: 문서 분할(Split Documents)
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 단계 3: 임베딩 & 벡터스토어 생성(Create Vectorstore)
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# 단계 4: 검색(Search)
# from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever

# 단계 5: 프롬프트 생성(Create Prompt)

# 단계 6: 언어모델 생성(Create LLM)
from langchain_community.chat_models import ChatOllama

# 단계 7: 체인 생성(Create Chain)
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# 단계 8: 체인 실행(Run Chain)

# 단계 9: 결과 출력





# 단계 1: 문서 로드(Load Documents)
# 참조할 문서 내용을 로드하고, 청크로 나누고, 인덱싱합니다.
csv_filepath = "/home/Chatbot/LangChain/assets/curriculum_map.csv"

# default seperator = ","
loader = CSVLoader(file_path = csv_filepath)
docs = loader.load()




# 단계 2: 문서 분할(Split Documents)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)

splits = text_splitter.split_documents(docs)


# 단계 3: 임베딩 & 벡터스토어 생성(Create Vectorstore)
# 임베딩 모델 선택

# 3- (가) - llama3로 임베딩
# embeddings = OllamaEmbeddings( model = "Llama-3-Open-Ko-8B-FP16:latest")

# 3- (나) - BAAI로 임베딩
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
    model_kwargs = {'device': 'cuda'}, # 모델이 CPU에서 실행되도록 설정. GPU를 사용할 수 있는 환경이라면 'cuda'로 설정할 수도 있음
    encode_kwargs = {'normalize_embeddings': True}, # 임베딩 정규화. 모든 벡터가 같은 범위의 값을 갖도록 함. 유사도 계산 시 일관성을 높여줌
)

# 벡터스토어 생성
faiss_vectorstore = FAISS.from_documents(splits,
                                   embedding = embeddings
                                  )


# 단계 4: 검색(Search)
# 문서 포함되어 있는 정보를 검색하고 생성합니다.
# 리트리버는 구조화되지 않은 쿼리가 주어지면 문서를 반환하는 인터페이스입니다.
# initialize the bm25 retriever and faiss retriever

bm25_retriever = BM25Retriever.from_documents(splits)
bm25_retriever.k = 10
faiss_retriever = faiss_vectorstore.as_retriever(search_kwargs={"k": 10})

# initialize the ensemble retriever
retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, faiss_retriever], weights=[0.5, 0.5]
)
# def format_docs(docs):
#     # 검색한 문서 결과를 하나의 문단으로 합쳐줍니다.
#     return "\n\n".join(doc.page_content for doc in docs)

# 단계 5: 프롬프트 생성(Create Prompt)
# 프롬프트를 생성합니다.


# 단계 6: 언어모델 생성(Create LLM)
# 모델(LLM) 을 생성합니다.
llm = ChatOllama(model="Llama-3-Open-Ko-8B-FP16:latest")




# 단계 7: 체인 생성(Create Chain)
## 7-1: 프롬프트 임의 생성
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful, professional assistant named 효봇."),
    ("user", "{question}")
])

## 7-2: rag chain 생성

rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

print("rag_chain: ", rag_chain)

# 단계 8: 체인 실행(Run Chain)
# 문서에 대한 질의를 입력하고, 답변을 출력합니다.
question = "컴퓨터보안 과목은 몇 학년 몇학기에 들으면 좋을까?"


print()
print()

response = rag_chain.invoke(question)


# 결과 출력
print(f"source: {csv_filepath}")
print(f"문서의 수: {len(docs)}")
print("===" * 20)
print(f"[HUMAN]\n{question}\n")
print(f"[AI]\n{response}")