from langchain_community.document_loaders import TextLoader

loader = TextLoader('../assets/news.txt')
data = loader.load()

print(f'type : {type(data)} / len : {len(data)}')
print(f'data : {data}')
print(f'page_content : {data[0].page_content}')