import sqlite3
import sys
from abc import ABC, abstractmethod
from dotenv import load_dotenv
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
from rich.console import Console
from rich.table import Table
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from utils import DB_SCHEMA
import google.generativeai as genai
import os

AI_MODEL_NAME=""
load_dotenv()
console = Console()

# Abstract class for AI models
class AIModel(ABC):
    @abstractmethod
    def generate_response(self, input_text):
        pass

# Concrete implementation for OpenAI
class OpenAIModel(AIModel):
    def __init__(self):
        self.chat = ChatOpenAI(temperature=0, verbose=True)

    def generate_response(self, input_text):
        obj = self.chat(input_text)
        return obj.content

# Concrete implementation for Gemini
class GeminiModel(AIModel):
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel(model_name = "gemini-pro")
    
    def generate_response(self, input_text):
        obj = self.model.generate_content(input_text)
        val = obj.text.replace("```sql", "").replace("```","")
        return val

def print_model_banner(text: str):
    console = Console()
    text = Text(f"{text}", style="bold")
    text.justify = "center"  # Align the text

    # Create a Panel with the aligned text
    panel = Panel(text, width=40, expand=False)
    console.print(panel)

# Function to check if the string is a valid SQL query
def is_valid_sql(query):
    return "SELECT" in query or "INSERT" in query or "UPDATE" in query or "DELETE" in query

# Function to translate English to SQL using AI Model
def english_to_sql(english_input, ai_model):
    sql_translate_string = f"""You are a helpful SQL assistant that translates Text written in conversational text to SQL. You must always have a column name, by Aliasing a column to something meaningful if needed. You MUST ONLY return the SQL with nothing else. 
    - This is a SQLite database, so use appropriate SQLite syntax.
    - Use your best judgement to include columns that are relevant to the question.

    >>> Here is the Database Schema:
    {DB_SCHEMA}

    >>> Here's the Text: {{input}}"""

    if (AI_MODEL_NAME == "openai"):
        sql_translate_template = ChatPromptTemplate.from_template(sql_translate_string)
        sql_translate_messages = sql_translate_template.format_messages(input=english_input)
    elif (AI_MODEL_NAME == "gemini"):
        fmt = sql_translate_string.replace("{input}", english_input).replace("{DB_SCHEMA}", DB_SCHEMA)
        sql_translate_messages = fmt.replace("```","")


    response = ai_model.generate_response(sql_translate_messages)
    print(response)
    sql_query = response

    if is_valid_sql(sql_query):
        return sql_query, True
    else:
        return response, False #.content

# Function to execute SQL against the Chinook database
def execute_sql(sql_query):
    conn = sqlite3.connect("Chinook.db")
    cursor = conn.cursor()
    cursor.execute(sql_query)
    results = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    return results, column_names

# Main application loop
def main():
    global AI_MODEL_NAME
    AI_MODEL_NAME = sys.argv[1] if len(sys.argv) > 1 else "openai"
    if AI_MODEL_NAME == "openai":
        ai_model = OpenAIModel()
    elif AI_MODEL_NAME == "gemini":
        ai_model = GeminiModel()
    # Add more conditions for different AI models here
    else:
        raise ValueError("Unsupported AI model")

    print_model_banner(f"AI Model: {AI_MODEL_NAME}")

    while True:
        user_input = input(f"\n{AI_MODEL_NAME}: Enter your query (or type 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break

        sql_query, is_valid = english_to_sql(user_input, ai_model)
        if is_valid:
            try:
                results, col_names = execute_sql(sql_query)
                table = Table(show_header=True, header_style="bold magenta")
                for column_name in col_names:
                    table.add_column(column_name)
                for row in results:
                    table.add_row(*[str(item) for item in row])
                console.print(table)
            except Exception as e:
                print(f"An error occurred while executing SQL: {e}")
        else:
            print(f"Non-SQL Response: {sql_query}")

if __name__ == "__main__":
    main()
