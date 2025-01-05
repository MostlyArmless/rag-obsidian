import os
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever
from get_vector_db import get_vector_db
from typing import Tuple

LLM_MODEL = os.getenv('LLM_MODEL', 'llama3.1:latest')

# Function to get the prompt templates for generating alternative questions and answering based on context
def get_prompt_templates() -> Tuple[PromptTemplate, ChatPromptTemplate]:
    question_expansion_prompt = PromptTemplate(
        input_variables=["question"],
        template="""You are an AI language model assistant. Your task is to generate five
        different versions of the given user question to retrieve relevant documents from
        a vector database. By generating multiple perspectives on the user question, your
        goal is to help the user overcome some of the limitations of the distance-based
        similarity search. Provide these alternative questions separated by newlines.
        Original question: {question}""",
    )

    answer_generation_prompt = ChatPromptTemplate.from_template(
        """Answer the question based ONLY on the following context:
        {context}
        Question: {question}
        """
    )

    return question_expansion_prompt, answer_generation_prompt

# Main function to handle the query process
def query(input):
    if input:
        # Initialize the language model with the specified model name
        llm = ChatOllama(model=LLM_MODEL)
        # Get the vector database instance
        db = get_vector_db()
        # Get the prompt templates
        QUERY_PROMPT, prompt = get_prompt_templates()

        # Set up the retriever to generate multiple queries using the language model and the query prompt
        retriever = MultiQueryRetriever.from_llm(
            db.as_retriever(), 
            llm,
            prompt=QUERY_PROMPT
        )

        # Define the processing chain to retrieve context, generate the answer, and parse the output
        chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        response = chain.invoke(input)
        
        return response

    return None

if __name__ == '__main__':
    import sys
    import time
    input = sys.argv[1] if len(sys.argv) > 1 else None
    start_time = time.time()
    response = query(input)
    end_time = time.time()

    execution_time = end_time - start_time
    print(f"Execution time: {execution_time:.4f} seconds")
    print(response)