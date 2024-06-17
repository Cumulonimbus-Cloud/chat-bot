import torch
from langchain_community.document_loaders import CSVLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy

from langchain import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline



def run(question_from_client, model_id, tokenizer, model):
    # CSV 파일 로드
    csv_loader = CSVLoader(file_path="/home/Chatbot/LangChain/assets/curriculum_map.csv")
    csv_docs = csv_loader.load()

    # 로드된 문서 통합
    #docs = csv_docs + pdf_docs
    docs = csv_docs
    print(f"문서의 수: {len(docs)}")

    # 텍스트 분할
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    texts = text_splitter.split_documents(docs)

    # 임베딩 생성
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-m3",
        model_kwargs = {'device': 0},
        encode_kwargs = {'normalize_embeddings': True},
    )

    # Vector store 생성
    vectorstore = FAISS.from_documents(
        texts,
        embedding=embeddings,
        distance_strategy=DistanceStrategy.COSINE
    )
    # 로컬에 DB 저장
    MY_FAISS_INDEX = "MY_FAISS"
    vectorstore.save_local(MY_FAISS_INDEX)

    # # 필요한 모델과 파라미터 설정 -> server.py에 잇음
    # model_id = 'beomi/Llama-3-Open-Ko-8B'
    # tokenizer = AutoTokenizer.from_pretrained(model_id)
    # model = AutoModelForCausalLM.from_pretrained(model_id)

    # 텍스트 생성 파이프라인 설정
    text_gen_pipeline = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        device=0  # GPU 사용
    )

    # FAISS 벡터스토어 로드
    vectorstore = FAISS.load_local("MY_FAISS", embeddings, allow_dangerous_deserialization=True)
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})


    # 초기 context 설정
    context = ""


    question = ""
    if(question_from_client != None):
            question = question_from_client
    else:
        question = input("질문을 입력하세요 (종료하려면 'q'를 입력하세요): ")

    def generate_answer(question, context, max_new_tokens=50, temperature=0.1, repeat_penalty=1.2, eos_token_id=128001):
        # 텍스트 생성
        prompt = f"""호기심 많은 사용자와 인공지능 비서의 채팅.
        비서는 사용자의 질문에 도움이 되고 상세하며 정중한 답변을 제공해야 합니다.
        그리고 당신이 바로 인공지능 비서입니다.
        질문에 대한 답변은 다음의 Context를 참고해주세요.\n\n Context: {context}\n\nQuestion: {question}\n\nAnswer:"""

        input_ids = tokenizer.encode(prompt, return_tensors='pt').to(text_gen_pipeline.device)
        
        generated_ids = text_gen_pipeline.model.generate(
            input_ids,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            repetition_penalty=repeat_penalty,
            eos_token_id=eos_token_id,
            pad_token_id=tokenizer.eos_token_id
        )
        
        generated_text = tokenizer.decode(generated_ids[0], skip_special_tokens=True)
        answer = generated_text.split('Answer:')[-1].strip()
        
        return answer
    
    # if question.lower() == 'q':
    #     break

    # 문서 검색
    retrieved_docs = retriever.get_relevant_documents(question)
    retrieved_context = " ".join([doc.page_content for doc in retrieved_docs])
    
    # 검색된 context만 사용하여 답변 생성
    answer = generate_answer(question, retrieved_context)
    
    # 이전 질문과 답변을 context에 추가
    context += f"Question: {question}\nAnswer: {answer}\n"
    
    print(f"Question: {question}")
    print(f"Answer: {answer}\n")
    response_data = {
        "Question": question,
        "Answer": answer
    }
    return response_data
