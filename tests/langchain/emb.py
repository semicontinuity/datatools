from langchain_ollama import OllamaEmbeddings

embeddings = OllamaEmbeddings(
    model="deepseek-r1:8b",
)

# Create a vector store with a sample text
from langchain_core.vectorstores import InMemoryVectorStore

text = "langchain is the framework for building context-aware reasoning applications"
ttt = [
    text,
    "World peace",
    "World peace 7",
    "AI app"
]
vectorstore = InMemoryVectorStore.from_texts(
    ttt,
    embedding=embeddings,
)

# Use the vectorstore as a retriever
retriever = vectorstore.as_retriever()

# Retrieve the most similar text
retrieved_documents = retriever.invoke("LangChain")

# show the retrieved document's content
content = retrieved_documents[0].page_content

print(content)


single_vector = embeddings.embed_query(text)
print(str(single_vector)[:100])  # Show the first 100 characters of the vector

two_vectors = embeddings.embed_documents(ttt)
for vector in two_vectors:
    print(str(vector)[:100])  # Show the first 100 characters of the vector