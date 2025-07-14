from dotenv import load_dotenv
load_dotenv()
from langchain_google_genai import ChatGoogleGenerativeAI
import os

class Gemini:
    def __init__(self, model_name="gemini-2.0-flash"):
        self.model_name = model_name
        self.llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            temperature=0.1,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            top_p=0.2,
            top_k=10,
            verbose=True,
        )
