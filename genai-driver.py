import requests
from pydantic import BaseModel, Field
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
import json
from dotenv import load_dotenv
load_dotenv()
from pydantic.json import pydantic_encoder
import sys
from rich import print_json
from rich.console import Console
from rich.syntax import Syntax

console = Console()

class Person(BaseModel):
    name: str = Field(...)
    address: str = Field(...)
    email: str = Field(...)
    alias: str = Field(...)
    vehicle: str = Field(...)
    license_plate: str = Field(...)

    class Config:
        json_encoders = {
            # Your custom encoders if needed, for example:
            # datetime: lambda v: v.isoformat(),
        }

    def to_json(self):
        # Use model_dump() to get the model's data as a dict
        model_dict = self.model_dump(by_alias=True)
        # Use json.dumps() to convert the dict to a JSON string
        return json.dumps(model_dict)
        #return self.json()

    @classmethod
    def from_json(cls, json_data):
        return cls(**json.loads(json_data))

def communicate_with_legacy_api(json_payload: str, show_xml=False):
    headers = {'Content-Type': 'application/xml'}
    xml_payload = json_to_xml_with_llm(json_payload)
    if show_xml:
        print("XML Response Payload:")
        syntax = Syntax(xml_payload, "xml", theme="monokai", line_numbers=True)
        console.print(syntax)  # Optionally print the XML payload
    response = requests.post('http://127.0.0.1:5001/person', data=xml_payload, headers=headers)
    return xml_to_json_with_llm(response.content) if response.ok else None

def json_to_xml_with_llm(json_payload: str):
    chat = ChatOpenAI(temperature=0.0, model_name="gpt-3.5-turbo-0301")
    xml_translate_str = """You are an XML and JSON conversion bot. Convert this JSON to XML. JSON: {json_input}"""

    xml_translate_template = ChatPromptTemplate.from_template(xml_translate_str)
    xml_translate_messages = xml_translate_template.format_messages(json_input=json_payload)
    response = chat(xml_translate_messages)
    return response.content

def xml_to_json_with_llm(xml_content: str):
    chat = ChatOpenAI(temperature=0.4)
    json_translate_str = """You are a JSON assistant. Convert this XML to JSON. XML: {xml_input}"""

    json_translate_template = ChatPromptTemplate.from_template(json_translate_str)
    json_translate_messages = json_translate_template.format_messages(xml_input=xml_content)
    response = chat(json_translate_messages)
    return response.content

def main():
    show_xml = '--show-xml' in sys.argv  # Check if --show-xml is in the command line arguments
    user_input_json = {
        "name": "John Doe",
        "address": "123 Main St",
        "email": "johndoe@example.com",
        "alias": "JD",
        "vehicle": "Toyota",
        "license_plate": "XYZ 1234"
    }
    print("Input JSON:")
    print_json(json.dumps(user_input_json))
    print()

    person = Person.from_json(json.dumps(user_input_json))
    response_json = communicate_with_legacy_api(person.to_json(), show_xml=show_xml)
    response_dict = json.loads(response_json)

    if response_json:
        print("Successfully communicated with the legacy API")
        #response_person = Person.from_json(response_json)
        print(response_dict['Response'])
    else:
        print("Failed to communicate with the legacy API")

if __name__ == "__main__":
    main()
