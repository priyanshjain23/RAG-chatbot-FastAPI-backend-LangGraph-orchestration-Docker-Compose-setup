from llama_index.llms.groq import Groq as LlamaGroq
from langchain_groq import ChatGroq
from llama_index.core import Settings
from app.config import MODEL_NAME, GROQ_API_KEY

# Used internally by LlamaIndex's query engine
Settings.llm = LlamaGroq(model=MODEL_NAME, api_key=GROQ_API_KEY)

# Used directly for plain chat (no retrieval) turns
chat_llm = ChatGroq(model=MODEL_NAME, temperature=0)
