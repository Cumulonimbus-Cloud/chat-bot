from langchain_community.retrievers import AmazonKnowledgeBasesRetriever

# retriever 선언
retriever = AmazonKnowledgeBasesRetriever(
    knowledge_base_id="여기에 입력하세요", # 입력 필요
    retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 4}},
    region_name="us-east-1"
)

# 질문 설정 후, retriever에 전달해 적합한 데이터를 가져오는 지 테스트
question = "길을 가다가 심한 욕을 들어서 명예훼손으로 신고하고싶은데, 가능할까?"
query = question
retriever.get_relevant_documents(query=query)