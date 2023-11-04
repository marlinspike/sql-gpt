## SQL-GPT
This repository is a demo of using OpenAI GPT 3.5 to reason over a SQLite database. Ask queries in English or any other langaage supported by GPT-3 and it generates the corresponding SQL and gets the results from the database.

## Getting Started
Get an OpenAI API key, and create a file called **.env** with the following contents:
```
OPENAI_API_KEY="sk-..."
```

Then install the dependencies:
```
pip install -r requirements.txt
```

Then run the following command:
```
python app.py
```