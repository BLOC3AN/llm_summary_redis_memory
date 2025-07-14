from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.utils.logger import Logger

logger = Logger(__name__)

class LLMOpenAI:
    def __init__(self, llm_model_name: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(
            model=llm_model_name,  # Sửa từ 'name' thành 'model'
            temperature=0,
            top_p=0.2,
            verbose=True,
        )
        self.name = llm_model_name

    def invoke(self,prompt):
        """Invoke the LLM with a prompt and return the response"""
        try:
            response = self.llm.invoke(input=prompt)
            logger.info(f"LLM invoked successfully with model: {self.name}")
            return response
        except Exception as e:
            logger.error(f"Error invoking LLM: {e}")
            raise