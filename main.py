from langchain.utilities import SQLDatabase
from langchain.llms import OpenAI
from langchain_experimental.sql import SQLDatabaseChain
from langchain.chains import create_sql_query_chain
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
import sqlite3

load_dotenv()

db = SQLDatabase.from_uri("sqlite:///Chinook.db")
llm = OpenAI(temperature=0, verbose=True)
db.run("SELECT COUNT(*) FROM Employee")

def get_user_input():
    # Prompt the user for input
    user_input = input(
        """
            demo: Run a demo query \n
            sql: Run a sql query from plaintext \n
        """).strip().lower()

    # Check if the input starts with 'demo '
    if user_input.startswith('demo'):
        mode = 'demo'
        parameter = user_input[len('demo: '):]  # Extract the rest of the string as parameter
    # Check if the input starts with 'sql '
    elif user_input.startswith('sql'):
        mode = 'sql'
        parameter = user_input[len('sql:'):]  # Extract the rest of the string as parameter
    else:
        print("Invalid mode. Please start your command with 'demo' or 'sql'.")
        return None, None  # Return None to indicate an error

    # Return the mode and parameter
    return mode, parameter

mode, parameter = get_user_input()
print("Mode: ", mode)
print("Parameter: ", parameter)
print()

if mode == 'demo':
    print(f"Mode: {mode}, Parameter: {parameter}")
    db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)
    db_chain.run("How many employees are there?")
elif mode == 'sql':
    print("creating sql chain")
    chain = create_sql_query_chain(ChatOpenAI(temperature=0), db)
    response = chain.invoke({"question": "How many employees are there"})
    print(f"Generated SQL query: {response}")
    db.run(response)
    
    