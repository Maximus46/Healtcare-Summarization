import pandas as pd
import os
import logging
import re
from pymongo import UpdateOne
from datetime import datetime
from database.mongo_db import MongoDB
from utility.utils import clean_data
from openpyxl.utils.exceptions import IllegalCharacterError


# Constants
DATABASE = 'healthcareDB'
COLLECTION = 'patients_test'
CSV_DIRECTORY = 'data'
DELIMITER = '\t'
    
def extract_exam_data(row, visit_date, file_name):
    # Extract exam data from the row
    exam_data = {}
    generic_exam_data = {}
    unstructured_data = {}
    generic_unstructured_data = {}
    
    for column_name, column_value in row.items():
        if column_name.startswith('Exam') and pd.notna(column_value):
            # Extract the exam index from the last character(s) of the column name
            exam_indexes = re.findall(r'\d+', column_name)
            exam_index = int(exam_indexes[-1]) if exam_indexes else None
            
            # Remove prefix and suffix from column name
            column_name = column_name[len('Exam'):]

            if exam_index is not None:
                if exam_index not in exam_data:
                    exam_data[exam_index] = {}
                exam_data[exam_index][column_name] = column_value
            else:
                generic_exam_data[column_name] = column_value
            
        elif column_name.startswith('Unstructured') and pd.notna(column_value):
            # Extract the exam index from the last character(s) of the column name
            unstructured_indexes = re.findall(r'\d+', column_name)
            unstructured_index = int(unstructured_indexes[-1]) if unstructured_indexes else None
            
            # Remove prefix and suffix from column name
            column_name = column_name[len('Unstructured'):]
            
            if unstructured_index is not None:
                if unstructured_index not in exam_data:
                    exam_data[unstructured_index] = {}
                if unstructured_index not in unstructured_data:
                    unstructured_data[unstructured_index] = {}
                unstructured_data[unstructured_index][column_name] = column_value
            else:
                generic_unstructured_data[column_name] = column_value
                
    # Add generic exam data to index 0
    exam_data[0] = {}
    exam_data[0].update(generic_exam_data)
    
    # Check if generic_unstructured_data is not empty
    if generic_unstructured_data:
        exam_data[0]['unstructured'] = generic_unstructured_data
        exam_data[0]['unstructured']['processed'] = False

    
    # Add generic_data to all exams
    for exam_index, exam in exam_data.items():
        exam['name'] = file_name.rstrip('.csv')
        if 'exam_date' not in exam:
            exam['exam_date'] = visit_date
            
        # Add associated unstructured data if it exists
        if exam_index in unstructured_data:
            exam['unstructured'] = unstructured_data[exam_index]
        
            # Add processed field to exam's unstructured data
            if exam['unstructured']:
                exam['unstructured']['processed'] = False
            
    # Sort the exam_data dictionary by index
    sorted_exam_data = {k: exam_data[k] for k in sorted(exam_data)}

    # Convert the sorted exam_data dictionary to a list
    exams = list(sorted_exam_data.values())
    
    return exams

def extract_surgery_data(row):
    surgery_data = {}
    generic_surgery_data = {}

    for column_name, column_value in row.items():
        if column_name.startswith('Surgery') and pd.notna(column_value):
            # Extract the surgery index from the last character(s) of the column name
            surgery_indexes = re.findall(r'\d+', column_name)
            surgery_index = int(surgery_indexes[-1]) if surgery_indexes else None
                      
            # Remove prefix and suffix from column name
            column_name = column_name.lstrip('Surgery')
                      
            if surgery_index is not None:
                if surgery_index not in surgery_data:
                    surgery_data[surgery_index] = {}
                surgery_data[surgery_index][column_name] = column_value
            else:
                generic_surgery_data[column_name] = column_value

    # Add generic_data to all surgeries
    for surgery in surgery_data.values():
        surgery.update(generic_surgery_data)
        
    # Sort the surgery_data dictionary by index
    sorted_surgery_data = {k: surgery_data[k] for k in sorted(surgery_data)}

    # Convert the sorted surgery_data dictionary to a list
    surgeries = list(sorted_surgery_data.values())

    return surgeries

def extract_therapy_data(row):
    therapy_data = {}
    generic_therapy_data = {}

    for column_name, column_value in row.items():
        if column_name.startswith('Therapy') and pd.notna(column_value):
            # Extract the therapy index from the last character(s) of the column name
            therapy_indexes = re.findall(r'\d+', column_name)
            therapy_index = int(therapy_indexes[-1]) if therapy_indexes else None  
            
            # Remove prefix and suffix from column name
            column_name = column_name.lstrip('Therapy')
                          
            if therapy_index is not None:
                if therapy_index not in therapy_data:
                    therapy_data[therapy_index] = {}
                therapy_data[therapy_index][column_name] = column_value
            else:
                generic_therapy_data[column_name] = column_value

    # Add generic exam data to index 0
    therapy_data[0] = {}
    therapy_data[0].update(generic_therapy_data)

    # Sort the therapy_data dictionary by index
    sorted_therapy_data = {k: therapy_data[k] for k in sorted(therapy_data)}

    # Convert the sorted therapy_data dictionary to a list
    therapies = list(sorted_therapy_data.values())

    return therapies

# Read operations data from CSV file and return a list of operation dictionaries
def read_from_csv(csv_file, delimiter, file_name):
    patients = []
    
    df = pd.read_csv(csv_file, delimiter=delimiter, low_memory=False)
    
    # Clean the data in all columns
    df = df.applymap(clean_data)

    print(df)
    
    for _, row in df.iterrows():
        codpaz = row['CODPAZ']

        # Extract patient data from the row
        pat_data = row.filter(like='Patient').dropna().to_dict()
        # Remove prefix and suffix from column names in visit_data
        pat_data = {column_name[len('Patient'):]: column_value for column_name, column_value in pat_data.items()}
     
        # Extract visit data from the row
        visit_data = row.filter(like='Visit').dropna().to_dict()
        exams = []
        
        # Extract the 'date' field from visit_data if it exists and then remove them.
        if visit_data:
            visit_date = visit_data.pop('VisitDATA_EVENTO', visit_data.pop('VisitDATA_ESAME', None))
            if visit_date:
                visit_date = visit_date.split()[0]
            # Remove prefix and suffix from column names in visit_data
            visit_data = {column_name[len('Visit'):]: column_value for column_name, column_value in visit_data.items()}
            
            # Extract exam data from the row
            exams = extract_exam_data(row, visit_date, file_name)
            
            # # Extract surgery data from the row
            # surgeries = extract_surgery_data(row)
            
            # # Extract therapy data from the row
            # therapies = extract_therapy_data(row)
                    
            
        # # Create a new patient document
        # patient_data = {
        #     'patient_id': codpaz,
        #     **pat_data,                   # Include all remaining patient_data fields
        #     'visits': [{
        #         'name': file_name.rstrip('.csv'),
        #         'start_date': visit_date,
        #         **visit_data,             # Include all remaining visit_data fields
        #         'exams': [{
        #             exam_index,
        #             exam_date,
        #             file_name,
        #             **exam_data           # Include all remaining exam_data fields
        #          }],
        #         'surgeries': surgeries,
        #         'therapies': therapies
        #     }],
        # }
        
        # Create a new patient document
        patient_data = {
            'patient_id': codpaz,
            **pat_data,  # Include all remaining patient_data fields
            'visits': [],
        }

        # Check if visit_date is available
        if visit_data or exams:
            # Create a new visit dictionary
            visit = {
                'name': file_name.rstrip('.csv'),
                'start_date': visit_date,
                **visit_data,  # Include all remaining visit_data fields
                'exams': exams
                # 'surgeries': surgeries,
                # 'therapies': therapies
            }

            # Add the visit to the patient's visits list
            patient_data['visits'].append(visit)

        patients.append(patient_data)

    return patients

# Check if any key-value pair in extracted_patient is missing in existing_patient
def check_for_new_info(extracted_patient, existing_patient):
    new_data = {'visits': []}

    # Check top-level fields
    new_fields = set(extracted_patient.keys()) - set(existing_patient.keys())
    new_data.update({field: extracted_patient[field] for field in new_fields})

    # Check visits
    extracted_visits = extracted_patient.get('visits', [])
    existing_patient_visits = existing_patient.get('visits', [])
    existing_visits = {(visit['name'], visit['start_date']): visit for visit in existing_patient_visits}

    for extracted_visit in extracted_visits:
        visit_name = extracted_visit['name']
        visit_start_date = extracted_visit['start_date']
        existing_visit = existing_visits.get((visit_name, visit_start_date))

        # Check if there is an existing visit with the same date and name
        if (visit_name, visit_start_date) not in existing_visits:
            new_data['visits'].append(extracted_visit)
        else:
            # Check visit-level fields
            new_visit_fields = set(extracted_visit.keys()) - {'exams'}
            if any(field not in existing_visit for field in new_visit_fields):
                new_data['visits'].append(extracted_visit)
                continue

            # Check exams
            extracted_exams = extracted_visit.get('exams', [])
            existing_exams = existing_visit.get('exams', [])
    
            for extracted_exam in extracted_exams:
                if not any(extracted_exam.keys() <= existing_exam.keys() for existing_exam in existing_exams):
                    new_data['visits'].append(extracted_visit)
                    break
    
    if not new_data['visits'] and not new_data.keys() - {'visits'}:  # If both 'visits' list and other top-level fields are empty
        return None
    else:
        return new_data

def update_existing_patient_info(existing_patient, new_patient):
    # Check if the patient data needs to be updated
    update_patient_data = {
        key: value for key, value in new_patient.items() if key not in existing_patient and key != 'visits'
    }
    if update_patient_data:
        existing_patient.update(update_patient_data)

def update_existing_visits(existing_patient, new_visits):
    for new_visit in new_visits:
        existing_visits = existing_patient['visits']
        matching_visit = next(
            (
                visit for visit in existing_visits
                if visit['name'] == new_visit['name'] and visit['start_date'] == new_visit['start_date']
            ),
            None
        )
        if matching_visit:
            # Replace the matching visit with the new visit
            existing_visits.remove(matching_visit)
            existing_visits.append(new_visit)
        else:
            existing_visits.append(new_visit)

def process_csv_file(csv_file, mongo_db, existing_patient_ids, existing_patients):
    csv_path = os.path.join(CSV_DIRECTORY, csv_file)
    logging.info(f"Processing '{csv_file}'...")

    try:
        # Read data from CSV files and populate patients
        patients = read_from_csv(csv_path, DELIMITER, csv_file)

        logging.info(f"Read {len(patients)} patients from '{csv_file}'.")
        
        # Patients to update
        updated_patients = {}
        
        for patient in patients:
            patient_id = patient['patient_id']
            
            # Check if the document for the patient already exists
            if patient_id in existing_patient_ids:
                existing_patient = existing_patients.get(patient_id) 
                
                if not existing_patient:
                    # Retrieve the patient from MongoDB if not already in the existing_patients dictionary
                    existing_patient = mongo_db.find_document(COLLECTION, {'patient_id': patient_id})
                
                # Check if the patient data needs to be updated
                new_data = check_for_new_info(patient, existing_patient)
                if new_data:
                    # Updates general patient's info
                    update_existing_patient_info(existing_patient, new_data)
                    
                    new_visits = new_data.get('visits', [])
                
                    # Updates patient's visits
                    update_existing_visits(existing_patient, new_visits)  
                                            
                    existing_patients[patient_id] = existing_patient
                    updated_patients[patient_id] = existing_patient
                    logging.info(f"Updated patient with ID '{patient_id}'.")
                else:
                    logging.info(f"Patient with ID '{patient_id}' doesn't require update.")

            else:                
                # Update the existing IDs list
                existing_patient_ids.add(patient_id)
                # Insert the patient document into the existing_patients list
                existing_patients[patient_id] = patient
                updated_patients[patient_id] = existing_patients[patient_id]
            
                logging.info(f"Inserted new patient with ID '{patient_id}'.")
                    
        logging.info(f"Finished processing '{csv_file}'.")
        
        return updated_patients
    
    except pd.errors.ParserError:
            logging.error(f"Error parsing '{csv_file}'. Skipping the file.")
    except IllegalCharacterError:
            logging.error(f"Illegal characters found in '{csv_file}'. Skipping the file.")
    except Exception as e:
        logging.error(f"Error processing '{csv_file}': {str(e)}")
                
def order_patients_data(patients):
    # Sort visits by start_date and exams within each visit by exam_date
    for patient_data in patients.values():
        sorted_visits = sorted(patient_data['visits'], key=lambda x: x['start_date'])
        for visit in sorted_visits:
            sorted_exams = sorted(visit['exams'], key=lambda x: x['exam_date'])
            visit['exams'] = sorted_exams
        patient_data['visits'] = sorted_visits
       
def update_patients_in_database(updated_patients, mongo_db):
    bulk_operations = []

    for patient_id, patient in updated_patients.items():
        patient["last_updated"] = datetime.now()
        operation = UpdateOne({"patient_id": patient_id}, {"$set": patient}, upsert=True)
        bulk_operations.append(operation)

    # Execute the bulk write operation
    result = mongo_db.bulk_write(COLLECTION, bulk_operations)

    logging.info("Documents updated: %d", result.modified_count)
    logging.info("Documents inserted: %d", result.upserted_count)
    logging.info("Finished loading patients on the database.")
 
def main():
    # Connect to MongoDB cluster with MongoClient
    mongo_db = MongoDB(DATABASE)

    # Create indexes here
    # mongo_db.create_index(COLLECTION, 'patient_id', unique=True)
    # mongo_db.create_index(COLLECTION, 'last_updated' )
   
    # Get a list of all CSV files in the directory
    csv_files = [file for file in os.listdir(CSV_DIRECTORY) if file.endswith('.csv')]

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    indexes = mongo_db.get_collection(COLLECTION).index_information()
    print(indexes)
    
    # Keep tracks of all the already existing patients
    existing_patient_ids = set()
    existing_patients = {}
    
    for csv_file in csv_files:
        # Retrieve existing patient IDs from the MongoDB collection
        existing_patient_ids.update(mongo_db.get_patient_ids(COLLECTION))
        logging.info(f"{len(existing_patient_ids)} existing IDs retrieved.")

        updated_patients = process_csv_file(csv_file, mongo_db, existing_patient_ids, existing_patients)
                        
        # Check if there are documents to insert      
        if len(updated_patients):
            # Order patient's visits and exams chronologically
            order_patients_data(updated_patients)

            # Update patients on MongoDB
            update_patients_in_database(updated_patients, mongo_db)

        else:
            logging.info("No updated patients to process in '%s'.", csv_file)
       
if __name__ == '__main__':
    main()
