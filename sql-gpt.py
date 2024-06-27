import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from rich.console import Console
from rich.table import Table
import argparse
import os
from dotenv import load_dotenv
from openai import OpenAI
import requests
import logging

# Set up logging
logging.basicConfig(filename='app.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Connect to the SQLite database
conn = sqlite3.connect('Chinook.db')
cursor = conn.cursor()

# Initialize Rich console
console = Console()

def load_schema_from_file(file_path='schema.txt'):
    """Load the database schema from a file."""
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        logging.error(f"Schema file not found: {file_path}")
        return None

def generate_sql_query_openai(question, model="gpt-3.5-turbo", error_message=None):
    """Generate SQL query using OpenAI API."""
    schema = load_schema_from_file()
    if not schema:
        logging.error("Unable to load database schema.")
        return "Error: Unable to load database schema."

    prompt = f"""Given the following SQLite database schema:

    {schema}

    Generate a SQL query to answer the following question:
    {question}

    Provide only the SQL query without any explanation."""

    if error_message:
        prompt += f"\n\nThe previous query resulted in the following error: {error_message}\nPlease correct the query."

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates SQL queries."},
                {"role": "user", "content": prompt}
            ]
        )
        query = response.choices[0].message.content.strip()
        logging.info(f"Generated SQL query: {query}")
        return query
    except Exception as e:
        logging.error(f"Error generating SQL query: {str(e)}")
        return f"Error: {str(e)}"

def generate_sql_query_mistral(question, error_message=None):
    """Generate SQL query using local Mistral model via Ollama."""
    schema = load_schema_from_file()
    if not schema:
        logging.error("Unable to load database schema.")
        return "Error: Unable to load database schema."

    prompt = f"""Given the following SQLite database schema:
        {schema}

        Generate a SQL query to answer the following question:
        {question}

        Provide only the SQL query without any explanation."""

    if error_message:
        prompt += f"\n\nThe previous query resulted in the following error: {error_message}\nPlease correct the query."

    try:
        response = requests.post('http://localhost:11434/api/generate', 
                                 json={
                                     "model": "mistral",
                                     "prompt": prompt
                                 })
        query = response.json()['response'].strip()
        logging.info(f"Generated SQL query: {query}")
        return query
    except Exception as e:
        logging.error(f"Error generating SQL query with Mistral: {str(e)}")
        return f"Error: {str(e)}"

def execute_query(query):
    """Execute the SQL query and return the results as a pandas DataFrame."""
    try:
        df = pd.read_sql_query(query, conn)
        logging.info(f"Query executed successfully. Result shape: {df.shape}")
        return df
    except Exception as e:
        logging.error(f"Error executing query: {str(e)}")
        raise

def determine_output_format(question, df):
    """Determine the appropriate output format based on the question and results."""
    if df.empty:
        format = "text"
    elif "how many" in question.lower() or df.shape[0] == 1:
        format = "text"
    elif df.shape[1] <= 5 and df.shape[0] <= 20:
        format = "table"
    else:
        format = "graph"
    logging.info(f"Determined output format: {format}")
    return format

def display_result(question, df, output_format):
    """Display the result in the specified format."""
    logging.info(f"Displaying result in format: {output_format}")

    if output_format == "text":
        if df.empty:
            console.print("No results found.", style="bold red")
        else:
            result = df.iloc[0, 0] if df.shape == (1, 1) else df.to_string(index=False)
            console.print(result, style="bold green")
    elif output_format == "table":
        table = Table(title=question)
        for column in df.columns:
            table.add_column(column, style="cyan")
        for _, row in df.iterrows():
            table.add_row(*[str(val) for val in row])
        console.print(table)
    elif output_format == "graph":
        plt.figure(figsize=(10, 6))
        if df.shape[1] == 2:
            plt.bar(df.iloc[:, 0], df.iloc[:, 1])
            plt.xlabel(df.columns[0])
            plt.ylabel(df.columns[1])
        else:
            df.plot(kind='bar')
        plt.title(question)
        plt.tight_layout()
        plt.show()
    
    logging.info("Result displayed successfully")

def main():
    parser = argparse.ArgumentParser(description="LLM SQL Query Generator for Chinook Database")
    parser.add_argument("--model", choices=["gpt-3.5-turbo", "gpt-4", "mistral"], default="gpt-3.5-turbo",
                        help="Choose the LLM model to use (default: gpt-3.5-turbo)")
    parser.add_argument("--attempts", type=int, default=3,
                        help="Maximum number of attempts to generate a correct SQL query (default: 3)")
    args = parser.parse_args()

    logging.info(f"Application started with model: {args.model}, max attempts: {args.attempts}")

    while True:
        question = console.input("[bold cyan]Enter your question (type 'quit' or 'exit' to end): [/bold cyan]")
        
        if question.lower() in ["quit", "exit"]:
            logging.info("User requested to quit the application")
            break

        error_message = None
        for attempt in range(args.attempts):
            try:
                if args.model == "mistral":
                    sql_query = generate_sql_query_mistral(question, error_message)
                else:
                    sql_query = generate_sql_query_openai(question, model=args.model, error_message=error_message)
                
                console.print(f"\n[bold]SQL Query:[/bold] {sql_query}\n")
                
                df = execute_query(sql_query)
                output_format = determine_output_format(question, df)
                
                console.print("[bold]Results:[/bold]")
                display_result(question, df, output_format)
                logging.info(f"Query processed successfully on attempt {attempt + 1}")
                break
            except Exception as e:
                error_message = str(e)
                logging.error(f"Attempt {attempt + 1} failed. Error: {error_message}")
                if attempt == args.attempts - 1:
                    console.print(f"[bold red]Failed to generate a correct SQL query after {args.attempts} attempts. Last error: {error_message}[/bold red]")
                else:
                    console.print(f"[bold yellow]Attempt {attempt + 1} failed. Retrying...[/bold yellow]")
        
        console.print("\n" + "-"*50 + "\n")

if __name__ == "__main__":
    main()