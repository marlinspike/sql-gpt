import os
from abc import ABC, abstractmethod
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_fixed
import requests

# Load environment variables
load_dotenv()

# Import your OpenAIModel and GeminiModel classes here
# from your_module import OpenAIModel, GeminiModel

class AIModelFacade:
    def __init__(self, model_name: str = "openai"):
        if model_name == "openai":
            self.model = OpenAIModel()
        elif model_name == "gemini":
            self.model = GeminiModel()
        else:
            raise ValueError("Unsupported AI model")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def get_response(self, input_text):
        try:
            return self.model.generate_response(input_text)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                raise requests.exceptions.RetryError("Rate Limit Exceeded") from e
            raise
        except Exception as e:
            print(f"An error occurred: {e}")
            raise

# Example Usage
if __name__ == "__main__":
    facade = AIModelFacade(model_name="openai")  # Change to "gemini" to use GeminiModel
    response = facade.get_response("Example input text")
    print(response)
