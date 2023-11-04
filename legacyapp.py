from flask import Flask, request, Response
import xml.etree.ElementTree as ET

app = Flask(__name__)

@app.route('/person', methods=['POST'])
def person_endpoint():
    # Parse the XML from the request
    try:
        xml_data = ET.fromstring(request.data)
        # Process the XML data as needed, here we just print it
        print(ET.tostring(xml_data, encoding='utf8').decode('utf8'))
        
        # Create a response XML data
        response_data = ET.Element('Response')
        message = ET.SubElement(response_data, 'Message')
        message.text = 'Data received successfully'
        
        # Convert to a pretty XML string
        response_str = ET.tostring(response_data, encoding='utf8').decode('utf8')
        return Response(response_str, mimetype='application/xml')
    except ET.ParseError as e:
        error_response = ET.Element('Error')
        message = ET.SubElement(error_response, 'Message')
        message.text = f'Invalid XML: {e}'
        response_str = ET.tostring(error_response, encoding='utf8').decode('utf8')
        return Response(response_str, status=400, mimetype='application/xml')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
