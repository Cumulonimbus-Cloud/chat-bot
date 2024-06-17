from langchain_community.embeddings import OllamaEmbeddings

embeddings = OllamaEmbeddings(model="llama3:8b-instruct-q4_0")
embed = embeddings.embed_documents(
    [
        "Hello, Glory",
        "The East Sea and Mt. Baekdu",
        "Until they are worn out and dry",
        "May God protect us",
        "Long live our country"
    ]
)
print(len(embed))
print(len(embed[0]))
print(len(embed[1]))
print(embed)