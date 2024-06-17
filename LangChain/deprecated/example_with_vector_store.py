from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_community.embeddings import OllamaEmbeddings

import bs4
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain import hub
from langchain_core.runnables import RunnablePassthrough
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser

# Document Loader
from langchain_community.document_loaders import PyPDFLoader


# web base load
# BeautifulSoup : HTML 및 XML 문서를 파싱하고 구문 분석하는 데 사용되는 파이썬 라이브러리. 주로 웹 스크레이핑(웹 페이지에서 데이터 추출) 작업에서 사용되며, 웹 페이지의 구조를 이해하고 필요한 정보를 추출하는 데 유용
loader = WebBaseLoader(
    web_paths=("https://www.aitimes.com/news/articleView.html?idxno=159102"
               , "https://www.aitimes.com/news/articleView.html?idxno=159072"
               , "https://www.aitimes.com/news/articleView.html?idxno=158943"
               ),
    bs_kwargs=dict(
        parse_only=bs4.SoupStrainer(
            "article", # 태그
            attrs={"id": ["article-view-content-div"]}, # 태그의 ID 값들
        )
    ),
)
data = loader.load()
print(data[0])
print(type(data[0]))
print()

# # pdf load
# loader = PyPDFLoader("/home/Chatbot/LangChain/assets/4-1-0-14.pdf")
# data = data + loader.load()

# print(f'type : {type(data)} / len : {len(data)}')
# print(f'data : {data}')

# for d in data:
#     print(f'page_content : {d.page_content}')





text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
splits = text_splitter.split_documents(data)
print()
print(type(splits))
print()

print(f'len(splits[0].page_content) : {len(splits[0].page_content)}')
# for sp in splits : print(sp)

vectorstore = FAISS.from_documents(splits,
                                   embedding = OllamaEmbeddings(model="Llama-3-Open-Ko-8B-Q8_0:latest"),
                                   distance_strategy = DistanceStrategy.COSINE # 코사인 유사도 측정. 값이 클수록 더 유사함을 의미
                                  )

# 로컬에 DB 저장
MY_FAISS_INDEX = "MY_FAISS_INDEX"
vectorstore.save_local(MY_FAISS_INDEX)


## 검색 (Retriever) - 유사도 높은 5문장 추출
# 로컬 DB 불러오기
vectorstore = FAISS.load_local(MY_FAISS_INDEX, OllamaEmbeddings(model="Llama-3-Open-Ko-8B-Q8_0:latest"), allow_dangerous_deserialization=True)

retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5}) # 유사도 높은 5문장 추출
retrieved_docs = retriever.invoke("Llama3")
print(retrieved_docs)


## 검색
print()
print("검색 기능")
print()

# from langchain import hub
# from langchain_core.runnables import RunnablePassthrough

prompt = hub.pull("rlm/rag-prompt") # https://smith.langchain.com/hub/rlm/rag-prompt


llm = ChatOllama(model="Llama-3-Open-Ko-8B-Q8_0:latest")
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
print(chain.invoke('퍼플렉시티의 투자에 참여한 새로운 인물들을 한글로 알려줘.'))
