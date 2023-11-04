import sqlite3
import openai
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
from langchain.prompts.chat import ChatPromptTemplate
from rich.console import Console
from rich.table import Table
from utils import DB_SCHEMA

load_dotenv()
console = Console()
chat = ChatOpenAI(temperature=0, verbose=True)


# Function to translate English to SQL using GPT-4
def english_to_sql(english_input):
    sql_translate_string = f"""You are a helpful SQL assistant that translates Text written in conversational text to SQL. You must always have a column name, by Aliasing a column to something meaningful if needed. You MUST ONLY return the SQL with nothing else. 
    - This is a SQLite database, so use appropriate SQLite syntax.
    - Use your best judgement to include columns that are relevant to the question.

    >>> Here is the Database Schema:
    {DB_SCHEMA}

    >>> Here's the Text: {{input}}"""

    sql_translate_template = ChatPromptTemplate.from_template(sql_translate_string)
    sql_translate_messages = sql_translate_template.format_messages(input = english_input)
    
    # Use Langchain to send the prompt to GPT-4
    #llm = OpenAI(temperature=0, verbose=True)
    response = chat(sql_translate_messages)
    sql_query = response.content
    return sql_query


# Function to execute SQL against the Chinook database
def execute_sql(sql_query):
    # Connect to the Chinook database
    conn = sqlite3.connect("Chinook.db")
    cursor = conn.cursor()
    
    # Execute the query and fetch the results
    #res = cursor.execute(sql_query)
    cursor.execute(sql_query)
    results = cursor.fetchall()  # Fetch all results
    column_names = [description[0] for description in cursor.description]  # Get column names
    
    return results, column_names

# Main application loop
def main():
    while True:
        # Take user input
        user_input = input("\nEnter your English query (or type 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break
        
        # Translate to SQL
        try:
            sql_query = english_to_sql(user_input)
            print(f"SQL Query: {sql_query}")
            
            # Execute SQL and print results
            results, col_names = execute_sql(sql_query)
            table = Table(show_header=True, header_style="bold magenta")
            # Add columns to the table
            for column_name in col_names:
                table.add_column(column_name)

            for row in results:
                table.add_row(*[str(item) for item in row])
                #print(row)
            console.print(table)
            print()
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()