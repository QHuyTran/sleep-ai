from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
from llama_index.core.prompts import PromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()


def build_rag_engine():
    print("Loading embedding model... (first run takes 1-2 minutes)")

    # Use local embeddings - free, no API cost
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Use Groq for LLM inference - free tier
    Settings.llm = Groq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY")
    )

    print("Indexing documents...")
    documents = SimpleDirectoryReader("docs/").load_data()
    index = VectorStoreIndex.from_documents(documents)

    print("RAG engine ready")
    qa_prompt = PromptTemplate(
        "You are a sleep health assistant. Use ONLY the context below to answer.\n"
        "If the context does not contain enough information to answer confidently,\n"
        "say: 'I don't have enough information in my sources to answer this accurately.'\n"
        "Always cite which document supports your answer.\n\n"
        "Context:\n{context_str}\n\n"
        "Question: {query_str}\n"
        "Answer: "
    )
    return index.as_query_engine(
        similarity_top_k=3,
        text_qa_template=qa_prompt
    )


if __name__ == "__main__":
    engine = build_rag_engine()

    # Test query
    response = engine.query(
        "What are the most important things I can do to improve my deep sleep?"
    )
    print("\nTest Query Response:")
    print(str(response))
