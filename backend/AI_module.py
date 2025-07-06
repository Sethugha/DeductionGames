from langchain.chains import RetrievalQA
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI

# 1. Initialize embeddings
embedding_model = OpenAIEmbeddings()

# 2. Create or load a vector store
vector_store = FAISS.from_documents(documents, embedding_model)

# 3. Initialize an LLM
llm = OpenAI()

# 4. Build a RetrievalQA chain
qa_chain = RetrievalQA(llm=llm, retriever=vector_store.as_retriever())

# 5. Ask a question
result = qa_chain.run("What are the main findings of the 2022 annual report?")
print(result)
