from langchain.chains import RetrievalQA
from langchain.llms import Ollama

# Set up LLM
llm = Ollama(model="gemma:2b")

# Create QA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever()
)

# Query your knowledge base
response = qa_chain.run("your question here")
