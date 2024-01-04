## SQL-GPT
This repository is a demo of using OpenAI GPT 3.5 to reason over a SQLite database -- And now adding Google Gemini as well! Ask queries in English or any other langaage supported by GPT-3 and it generates the corresponding SQL and gets the results from the database.

Please see the [readme in this repo](https://github.com/marlinspike/gemini_chat_console) for instructions on how to get your Gemini API key if you want to try it out.

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


## Demo of a Legacy Application interacting with a Generative AI app
This demonstrates a legacy application interacting with a generative AI application. The legacy application is a simple web application that gets an XML payload from the driver app. The Generative AI driver app is a RESTful app, which speaks in JSON, but uses Generative AI to translate that JSON into XML for the Legacy App.

## Getting Started
Run the *legacyapp.py* Flask web application.

Then run the *genai-driver.py* application. Use the _--show-xml_ flag to see the XML that is being sent to the legacy app.