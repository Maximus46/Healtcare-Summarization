from collections import defaultdict
import logging
import traceback
from pymongo import UpdateOne
from database.mongo_db import MongoDB
from models.huggingface import load_model, load_pipeline
from processing.NER_module import preprocess_text, perform_ner, perform_ac
from processing.umls_linking import link_umls
from tqdm.auto import tqdm
from datetime import datetime

# Constants
DATABASE = 'healthcareDB'
PATIENTS_COLLECTION = 'patients_20'
ENTITIES_COLLECTION = 'patients_entities'
CSV_DIRECTORY = 'data'
DELIMITER = '\t'
ALIASES_FILE = 'ALIASES.txt'             # path al file di aliases forniti da esperti di dominio utili ad effettuare lo string-matching
NER_MODEL_PATH = "models/NER/model"      # path al modello NER
AC_MODEL_PATH = "models/AC/model"        # path al modello di Assertion Classification (AC)

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def update_patient_process_field(mongo_db, patient_id):
    # Update all 'processed' fields to True
    patients_collection = mongo_db.get_collection(PATIENTS_COLLECTION)
    query = {'patient_id': patient_id}
    update = {'$set': {'visits.$[].exams.$[exam].unstructured.processed': True}}
    array_filters = [{'exam.unstructured.processed': False}]
    patients_collection.update_one(filter= query, update=update, array_filters=array_filters)

def save_entities_to_database(mongo_db, entities, patient_id):
    # Prepare the bulk write operations
    bulk_operations = []

    # Extend existing patient_entities documents or insert new documents
    for patient_id, patient_entities  in entities.items():
        transformed_entities = transform_entities(patient_entities )

        bulk_operation = UpdateOne(
            {'patient_id': patient_id},
            {'$set': {'last_update': datetime.now()}, '$addToSet': {'entities': {'$each': transformed_entities}}},
            upsert=True
        )
        bulk_operations.append(bulk_operation)

    # Perform bulk write operations
    if bulk_operations:
        # Execute the bulk write operation
        result = mongo_db.bulk_write(ENTITIES_COLLECTION, bulk_operations)

        logging.info("Documents updated: %d", result.modified_count)
        logging.info("Documents inserted: %d", result.upserted_count)
        logging.info("Finished loading entities on the database.")
    else:
        logging.info(f"No updated texts to process for patient {patient_id}.")
        
def transform_entities(ner_entities):
    return [{
        'CUI': entity['concept_ui'],
        'text': entity['word'],
        'text_EN': entity['word_translated'],
        'type': entity['entity_group'],
        'concept_name': entity['concept_name']
    } for entity in ner_entities if entity['assertion'] == 'Present']

def process_entity_linking(ner_entities):
    linked_entities = []
    for entity in ner_entities:
        
        if entity['assertion'] == 'Present':
            # Link entity to UMLS
            is_linked = link_umls(entity)

            # Check if UMLS linking was successful
            if is_linked:
                # Store the entity and UMLS results
                linked_entities.append(entity)
    return linked_entities

def process_text(patient_id, text_snippet, ner_pipeline, ac_pipeline):
    try:
        # Measure the execution time of preprocess_text
        preprocessed_text = preprocess_text(text_snippet)

        # If filtered text is not empty, perform NER on it
        if preprocessed_text:
            # Measure the execution time of perform_ner
            ner_entities = perform_ner(ner_pipeline, preprocessed_text)
            logger.info(f"NER processed for patient {patient_id}, for text {text_snippet}")

            # If NER produced any entity on text, do Assertion Classification
            if ner_entities:
                # Measure the execution time of perform_ac
                try:
                    perform_ac(ac_pipeline, ner_entities, preprocessed_text)
                    logger.info(f"AC processed for patient {patient_id}")
                    
                    linked_entities = process_entity_linking(ner_entities)
                    logger.info(f"ML+EL processed for patient {patient_id}")

                    # Return ner_predictions only if available
                    return linked_entities 
                except Exception as e:
                    logger.error(f"Error processing AC for patient {patient_id}: {e}")  
                          
        logger.info(f"NER processed for patient {patient_id}")
    except Exception as e:
        logger.error(f"Error processing NER for patient {patient_id}: {e}")

def process_patients_documents(mongo_db: MongoDB, ner_pipeline, ac_pipeline, cursor):
    
    # Perform NER on unstructured data in patient documents
    for document in tqdm(cursor, desc="Processing Patient Documents"):
        # Dictionary to store entities for each patient
        patient_entities = defaultdict(list)
        
        # Check if the document has been updated
        patient_id = document['patient_id']
        visits = document.get('visits', [])
        
        logger.info(f"Processing TEXTS for patient {patient_id}")
        
        for visit in visits:
            exams = visit.get('exams', [])
            
            for exam in exams:
                unstructured_data = exam.get('unstructured', {})
                processed = unstructured_data.get('processed', False)

                if not processed:
                    # Extract the text snippets
                    text_snippets = list(unstructured_data.values())
                    
                    for text_snippet in text_snippets:
                        if text_snippet:
                            # Process the text
                            # - NER
                            # - Assertion Classification
                            # - ML IT-EN
                            # - Entity_linking to UMLS concepts                       
                            linked_entities = process_text(patient_id, text_snippet, ner_pipeline, ac_pipeline)
                            
                            # Add ner_entities to the list only if available
                            if linked_entities is not None and len(linked_entities) > 0:
                                patient_entities[patient_id].extend(linked_entities)
        
        logger.info(f"Saving entities to the database for patient {patient_id}")
        save_entities_to_database(mongo_db, patient_entities, patient_id)
        
        logger.info(f"Updating 'processed' fields for patient {patient_id}")
        update_patient_process_field(mongo_db, patient_id)

def load_models():
    ner_id2label = {0: 'O', 1: 'B-MedicalProblem', 2: 'I-MedicalProblem', 3: 'B-Treatment', 4: 'I-Treatment', 
                    5: 'B-Test', 6: 'I-Test'}
    ner_label2id = {v:k for k,v in ner_id2label.items()}
    ner_task = "ner"
    ner_model_architecture = "token_classification"
    
    # Load HuggingFace NER model
    try:
        ner_model, ner_tokenizer = load_model(NER_MODEL_PATH, ner_model_architecture, num_labels=len(ner_id2label), 
                                              id2label=ner_id2label, label2id=ner_label2id)
        ner_pipeline = load_pipeline(task=ner_task, model=ner_model, tokenizer=ner_tokenizer, 
                                     model_architecture=ner_model_architecture)
    except Exception as e:
        logger.error(f"Error loading HuggingFace NER model: {e}\n{traceback.format_exc()}")
        return
    
    ac_id2label = {0: 'Present', 1: 'Absent'}
    ac_label2id = {v:k for k,v in ac_id2label.items()}
    ac_task = "text-classification"
    ac_model_architecture = "sequence_classification"
    
    # Load HuggingFace Assertion model
    try:
        ac_model, ac_tokenizer = load_model(AC_MODEL_PATH,ac_model_architecture, num_labels=len(ac_id2label), 
                                            id2label=ac_id2label, label2id=ac_label2id)
        ac_pipeline = load_pipeline(task=ac_task, tokenizer=ac_tokenizer, model=ac_model, 
                                    model_architecture=ac_model_architecture)
    except Exception as e:
        logger.error(f"Error loading HuggingFace Assertion model: {e}\n{traceback.format_exc()}")
        return

    return ner_pipeline, ac_pipeline

def get_patients_to_process(mongo_db: MongoDB):
    
    # Retrieve only the necessary fields from the patients collection
    filter_query = {}
    projection_query = {'patient_id': 1, 'last_updated': 1}
    patients_cursor = mongo_db.find_documents(PATIENTS_COLLECTION, filter_query, projection_query)
    
    # Get the list of patient IDs and last_updated values
    patient_info = {patient['patient_id']: patient['last_updated'] for patient in patients_cursor}

     # Fetch the entities collection for the corresponding patient IDs
    entity_query = {'patient_id': {'$in': list(patient_info.keys())}}
    entities_cursor = mongo_db.find_documents(ENTITIES_COLLECTION, entity_query, projection_query)
    
    # Get the list of entity's IDs and last_updated values
    entity_info = {entity['patient_id']: entity['last_updated'] for entity in entities_cursor}

    # Compare the last_updated values between the patients and entities collections
    patient_ids = []
    for patient_id, patient_last_updated in patient_info.items():
        entity = entity_info.get(patient_id)
        if entity is None or patient_last_updated > entity:
            patient_ids.append(patient_id)
            
    
    # Fetch the entities collection for the corresponding patient IDs
    patient_query = {'patient_id': {'$in': patient_ids}}
    patients_to_process = mongo_db.find_documents(PATIENTS_COLLECTION, patient_query)    
    return patients_to_process

def main():
    logger.info("Starting NER Generation script...")
    
    try:
        logger.info("Loading NER and Assertion models...")
        ner_pipeline, ac_pipeline = load_models()
        
        if not ner_pipeline or not ac_pipeline:
                logger.error("Failed to load NER or Assertion models. Exiting...")
                return
        
        logger.info("Connecting to MongoDB...")
        mongo_db = MongoDB(DATABASE)
        
        logger.info("Retrieving patients to process...")
        patients_to_process = get_patients_to_process(mongo_db)

        logger.info("Processing patients' documents...")
        process_patients_documents(mongo_db, ner_pipeline, ac_pipeline, patients_to_process)

        logger.info("NER Generation script completed successfully!")
    except Exception as e:
        logger.error(f"Error running NER Generation script: {e}\n{traceback.format_exc()}")

if __name__ == '__main__':
    main()