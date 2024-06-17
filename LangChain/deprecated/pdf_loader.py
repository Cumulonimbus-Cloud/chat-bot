from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# # pdf load
# loader = PyPDFLoader("/home/Chatbot/LangChain/assets/4-4-0-0.pdf")

# pages = loader.load_and_split()
# # pages = loader.load()
# print(pages)



# # pypdf
# pdf_filepath = '/home/Chatbot/LangChain/assets/000660_SK_2023.pdf'
pdf_filepath = "/home/Chatbot/LangChain/assets/컴퓨터공학과_2024학년도 대학안내.pdf"

loader = PyPDFLoader(pdf_filepath)
docs = loader.load()

print(len(docs))
print(docs)


# 단계 2: 문서 분할(Split Documents)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)

splits = text_splitter.split_documents(docs)
print(splits)
print(len(splits))