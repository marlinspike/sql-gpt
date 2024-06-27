## SQL-GPT
This repository is a demo of using OpenAI GPT 3.5, 4o or a local Ollama Mistral LLM to reason over a SQLite database! Ask queries in English or any other langaage supported by the LLM and it generates the corresponding SQL and gets the results from the database.

Please see the [readme in this repo](https://github.com/marlinspike/gemini_chat_console) for instructions on how to get your Gemini API key if you want to try to extend this to use Gemini as well.

## Getting Started
Get an OpenAI API key, and create a file called **.env** with the following contents:
```
OPENAI_API_KEY="sk-..."
GEMINI_API_KEY="..."
```

Then install the dependencies:
```
pip install -r requirements.txt
```

Then run the following command:
```
python app.py openai
python app.py gemini
```

## Features

- Natural language to SQL query conversion using LLMs (OpenAI GPT or Mistral)
- Execution of generated SQL queries on a SQLite database (Chinook)
- Multiple output formats: text, table, and graphical representations
- Error handling and query regeneration
- Logging for debugging and analysis

## Options:
- `--model`: Choose the LLM model (gpt-3.5-turbo, gpt-4, or mistral)
- `--attempts`: Set the maximum number of query generation attempts

Once running, enter your questions in natural language. The application will generate SQL queries, execute them, and display the results.

Example queries:
1. "How many tracks are there in each genre?"
2. "What are the top 5 selling albums?"
3. "Show the total sales by year for the last 5 years"

## Technical Details

- LLM Integration: The application uses OpenAI's GPT models or the Mistral model via Ollama for natural language processing.
- Database Interaction: SQLite3 is used for database operations, with Pandas for data manipulation.
- Output Formatting: Rich library is used for console output and table formatting.
- Visualization: Matplotlib is employed for generating charts and graphs.

## Logging and Debugging

The application logs its operations to `app.log`. This file contains detailed information about query generation, execution, and any errors encountered, facilitating debugging and performance analysis.

## Extending the Application

To extend this demo:
1. Modify the `generate_sql_query_*` functions to support additional LLMs.
2. Enhance the `determine_output_format` function for more sophisticated output selection.
3. Expand the visualization options in `display_result` to support different chart types.

## Contributing

Contributions to improve the application are welcome. Please adhere to the following process:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Demo of a Legacy Application interacting with a Generative AI app
This demonstrates a legacy application interacting with a generative AI application. The legacy application is a simple web application that gets an XML payload from the driver app. The Generative AI driver app is a RESTful app, which speaks in JSON, but uses Generative AI to translate that JSON into XML for the Legacy App.

## Getting Started
Run the *legacyapp.py* Flask web application.

Then run the *genai-driver.py* application. Use the _--show-xml_ flag to see the XML that is being sent to the legacy app.
