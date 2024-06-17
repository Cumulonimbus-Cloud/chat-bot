from langchain_community.chat_models import ChatOllama
from langchain_core.messages.base import BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser # 스트림 형식으로 출력하기 위해



msg = BaseMessage # 입력받을 메세지 클래스

llm = ChatOllama(model="llama3:8b-instruct-q4_0", verbose = True) # ollama를 이용한 llm 선언

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful, professional assistant named 효봇. Introduce yourself first, and answer the questions. answer me in english no matter what. "),
    ("user", "{input}")
])

# chain = prompt | llm | StrOutputParser()
# m = chain.invoke({"input": "What is stock?"})
# print(m)

chain = prompt | llm
msg = chain.invoke({"input": "What is stock?"})

# msg = llm.invoke("What is stock?") # input

msg.pretty_print()


# # retriever 선언
# retriever = AmazonKnowledgeBasesRetriever(
#     knowledge_base_id="여기에 입력하세요", # 입력 필요
#     retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 4}},
#     region_name="us-east-1"
# )

# # 질문 설정 후, retriever에 전달해 적합한 데이터를 가져오는 지 테스트
# question = "길을 가다가 심한 욕을 들어서 명예훼손으로 신고하고싶은데, 가능할까?"
# query = question
# retriever.get_relevant_documents(query=query)