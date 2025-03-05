from flask_babel import _
from app import app
import requests, uuid, json

def translate(text, source_language, dest_language):

    if 'MS_TRANSLATOR_KEY' not in app.config or not app.config['MS_TRANSLATOR_KEY']:
        return _('Error: the translation service is not configured.')

    # Add your key and endpoint
    key = app.config['MS_TRANSLATOR_KEY']
    endpoint = "https://api.cognitive.microsofttranslator.com"

    # location, also known as region.
    # required if you're using a multi-service or regional (not global) resource. It can be found in the Azure portal on the Keys and Endpoint page.
    location = "westus2"

    path = '/translate'
    constructed_url = endpoint + path

    params = {
        'api-version': '3.0',
        'from': source_language,
        'to': dest_language
    }

    headers = {
        'Ocp-Apim-Subscription-Key': key,
        # location required if you're using a multi-service or regional (not global) resource.
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    # You can pass more than one object in body.
    body = [{
        'text': text
    }]

    request = requests.post(constructed_url, params=params, headers=headers, json=body)

    if request.status_code != 200:
        return _('Error: the translation service failed.')

    response = request.json()
    # return the actual translation as a string
    return response[0]['translations'][0]['text']