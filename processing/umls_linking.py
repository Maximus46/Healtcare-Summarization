import time
import requests
import os
from dotenv import load_dotenv
from umls_api import API
from .translations import perform_translation

# Load environment variables from .env file
load_dotenv()

# Access the UMLS variables
API_KEY  = os.getenv("UMLS_API_KEY")

def link_umls(entity):
    entity_name = entity['word']
    # Translate the text
    translated_text = perform_translation(entity_name)

    # Initialize UMLS API
    api = API(api_key= API_KEY)
    
    # Retry up to 3 times
    max_retries = 3
    retry_delay = 1  # Delay in seconds between retries
    
    for retry in range(max_retries):
        try:
            # Make the UTS API request
            # Search for the translated text to retrieve the CUI
            request = 'https://uts-ws.nlm.nih.gov/rest/search/current?string='+translated_text
            results = api._get(request)['result']['results']
            
            # Process the results
            if len(results) > 0:
                resp = results[0]
                entity['word_translated'] = translated_text
                entity['concept_ui'] = resp['ui']
                entity['concept_name'] = resp['name']
                print(f"Entity_name: {entity_name}, Translated_entity: {translated_text}, Resp_UI: {resp['ui']}, Resp_name: {resp['name']}")

                return True
            else:
                print(f"No results found for entity: {entity_name}")
                return False
            
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            if retry < max_retries - 1:
                print(f"Retrying after {retry_delay} second(s)...")
                time.sleep(retry_delay)
            else:
                print("Maximum retries exceeded. Unable to link UMLS.")
                return False