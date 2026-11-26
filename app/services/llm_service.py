
from langchain_openai import ChatOpenAI
from app.config import OPENAI_API_KEY, OPENAI_MODEL


# Initialize the LLM
llm = ChatOpenAI(
    model=OPENAI_MODEL,
    api_key=OPENAI_API_KEY,
    temperature=0
)


def get_llm():
    return llm
