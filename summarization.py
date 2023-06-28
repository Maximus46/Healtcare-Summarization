import openai
from database.mongo_db import MongoDB
import logging
import os
from dotenv import load_dotenv
from utility.utils import toFile
from datetime import datetime

# Constants
DATABASE = 'healthcareDB'
COLLECTION = 'patients'
SUMMARY_COLLECTION = 'patients_summarization'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_patients_to_summarize(mongo_db, source_collection, size_upper_bound=20000, limited=20):
    pipeline = [
        {"$addFields": {
            "bsonsize": {"$bsonSize": "$$ROOT"}
            }
        },
        {"$match": {"bsonsize": {"$lte": size_upper_bound}}},
        {"$sort":{"bsonsize":-1}},
        {"$project": {
            "_id": 0,
            "bsonsize": 0
            }
        },
        {"$limit": limited}
    ]
    
    # duplicate_collection(mongo_db, source_collection, dest_collection, pipeline)

    patients = mongo_db.perform_aggregation(source_collection, pipeline)
    
    return patients

def generate_prompt(text):
    
    prompt = "Genera una summarization di 300 parole della seguente cartella clinica in formato json, \
    rispettando l'ordine cronologico dei campi 'start_date' e 'exam_date'. \
    Menziona unicamente eventi importanti di patologie, diagnosi, farmaci e terapie presenti.\n\n"
    
    prompt1 = "Generate a 300-word summary of the following medical record in JSON format, \
    while maintaining the chronological order of start_date and exam_date fields. \
    Mention important events related to diseases and treatments.\n\n"
    
    full_text = prompt + text
    
    return full_text

def summarize_text(text, openai_api_key):
    openai.api_key = openai_api_key

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=generate_prompt(text),
        max_tokens=400,
        temperature=0.5,
        top_p=1.0,
        n=1,
        stop=None,
    )

    return response.choices[0].text.strip()

def process_patients(mongo_db, patients, openai_api_key):
    summarized_patients = []

    # Summarize each patient's document
    for patient in patients:
        patient_id = patient['patient_id']
        last_updated = patient['last_updated']
        
        document = is_updated(mongo_db, patient_id, last_updated)

        try:
            summary = ''
            if document:
                summary = document['summarization']
            else:
                summary = summarize_text(patient, openai_api_key)

            current_timestamp  = datetime.now()
            
            # Create a new summarized patient document
            summarized_patient = {
                'patient_id': patient_id,
                'last_updated': current_timestamp ,
                'summarization': summary,
            }
            logging.info(f"Summarized patient: {summarized_patient}")

            summarized_patients.append(summarized_patient)
        except Exception as e:
            logging.error(f"Error occurred while summarizing patient {patient_id}: {str(e)}")

    return summarized_patients

    summarized_patients = []

    # Summarize each patient's document
    for patient in patients:
        patient_id = patient['patient_id']
        last_updated = patient['last_updated']
        
        document = is_updated(mongo_db, patient_id, last_updated)

        try:
            summary = ''
            if document:
                summary = document['summarization']
            else:
                summary = summarize_text(patient, openai_api_key)

            current_timestamp  = datetime.now()
            
            # Create a new summarized patient document
            summarized_patient = {
                'patient_id': patient_id,
                'last_updated': current_timestamp ,
                'summarization': summary,
            }
            logging.info(f"Summarized patient: {summarized_patient}")

            summarized_patients.append(summarized_patient)
        except Exception as e:
            logging.error(f"Error occurred while summarizing patient {patient_id}: {str(e)}")

    return summarized_patients

def is_updated(mongo_db: MongoDB, patient_id, last_updated):
    query = {'patient_id': patient_id}
    
    summary = mongo_db.find_document(SUMMARY_COLLECTION, query)
    
    if summary and summary['last_updated'] >= last_updated:
        return summary
    
    return None
    
def insert_summarized_patients(mongo_db, collection, summarized_patients):
    
    # Check if there are documents to insert
    if summarized_patients:
        # Execute insert operations
        mongo_db.insert_documents(collection, summarized_patients)
        logging.info(f"Inserted {len(summarized_patients)} summarized patient documents into collection {collection}")
    else:
        logging.info("No summarized patient documents to insert")

def order_patients_data(patients):
    # Sort visits by start_date and exams within each visit by exam_date
    for patient_data in patients:
        sorted_visits = sorted(patient_data['visits'], key=lambda x: x['start_date'])
        for visit in sorted_visits:
            sorted_exams = sorted(visit['exams'], key=lambda x: x['exam_date'])
            visit['exams'] = sorted_exams
        patient_data['visits'] = sorted_visits  

def main():
    # Connect to MongoDB cluster with MongoClient
    mongo_db = MongoDB(DATABASE)
    
    # Load environment variables from .env file
    load_dotenv()
   
    # Read the OpenAI API key from environment variables
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    try:
        patients = extract_patients_to_summarize(mongo_db, COLLECTION)

        order_patients_data(patients)

        # toFile("patient_ordered.json", patients)
        
        summarized_patients = process_patients(mongo_db, patients, OPENAI_API_KEY)

        insert_summarized_patients(mongo_db, SUMMARY_COLLECTION, summarized_patients)
    except Exception as e:
        logging.error(f"Error occurred during main execution: {str(e)}")
            
if __name__ == "__main__":
    main()
