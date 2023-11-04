import requests
from pydantic import BaseModel, Field
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
from xml.etree.ElementTree import Element, tostring, fromstring
import xml.dom.minidom
from dotenv import load_dotenv
load_dotenv()

# Example Pydantic model representing a person with various details
class Person(BaseModel):
    name: str = Field(...)
    address: str = Field(...)
    email: str = Field(...)
    alias: str = Field(...)
    vehicle: str = Field(...)
    license_plate: str = Field(...)

    # Method to serialize the model to XML
    def to_xml(self):
        person_element = Element('Person')
        
        for field, value in self:
            child = Element(field)
            child.text = value
            person_element.append(child)
        
        return xml.dom.minidom.parseString(tostring(person_element)).toprettyxml()

    # Static method to deserialize XML to the model
    @classmethod
    def from_xml(cls, xml_data):
        # ... XML parsing logic ...
        # Let's say the result of XML parsing is `parsed_dict`
        # Correct the keys to match the Pydantic model's field names
        kwargs = {
            'name': parsed_dict.get('Name'),
            'address': parsed_dict.get('Address'),
            'email': parsed_dict.get('Email'),
            'alias': parsed_dict.get('Alias'),
            'vehicle': parsed_dict.get('Vehicle'),
            'license_plate': parsed_dict.get('License_Plate'),
        }
        # Now kwargs should have the correct keys that the Person model expects
        return cls(**kwargs)


# Function to communicate with the external API
def communicate_with_legacy_api(xml_payload: str):
    headers = {'Content-Type': 'application/xml'}  # Assuming the API expects XML
    response = requests.post('http://127.0.0.1:5001/person', data=xml_payload, headers=headers)
    return response.content if response.ok else None

# Function to interact with LangChain (if necessary)
def langchain_interaction(string_input: str):
    # Initialize the LangChain Chat Model
    chat = ChatOpenAI(temperature=0.4, verbose=True)  # Adjust temperature as necessary
    
    xml_translate_str = f"""You are a helpful XML assistant that translates Text written in conversational text to XML. You MUST ONLY return the XML with nothing else. 

    >>> Here's the Text: {{input}}"""

    xml_translate_template = ChatPromptTemplate.from_template(xml_translate_str)
    xml_translate_messages = xml_translate_template.format_messages(input = string_input)
    
    # Use Langchain to send the prompt to GPT-4
    #llm = OpenAI(temperature=0, verbose=True)
    response = chat(xml_translate_messages)
    xml_response = response.content

    return xml_response

# Main function to run the application
def main():
    # Assuming user_input is a string of details in English
    user_input = "Name: John Doe, Address: 123 Main St, Email: johndoe@example.com, Alias: JD, Vehicle: Toyota, License Plate: XYZ 1234"
    xml_data = langchain_interaction(user_input)

    # Convert XML data back to a Person model
    person = Person.from_xml(xml_data)

    # Serialize the Person model to XML to communicate with the API
    xml_payload = person.to_xml()

    # Send the XML to the legacy application's API
    response_xml = communicate_with_legacy_api(xml_payload)
    if response_xml:
        print("Successfully communicated with the legacy API")
        # Optionally, convert the response XML back to a model
        response_person = Person.from_xml(response_xml)
        print(response_person)
    else:
        print("Failed to communicate with the legacy API")

if __name__ == "__main__":
    main()
