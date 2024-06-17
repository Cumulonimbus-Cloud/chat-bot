from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("../assets/4-4-0-0.pdf")
pages = loader.load()

print(f'type : {type(pages)} / len : {len(pages)} / pages : {pages}')