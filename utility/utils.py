import re
from pyspark.sql.functions import *
import bson.json_util as json_util
        
def clean_data(value):
    if isinstance(value, (str, bytes)):
        cleaned_value = re.sub(r'[^ -~]', '', value)
        return cleaned_value.strip() or None
    else:
        return value
    
def compare_documents(doc1, doc2):
    # Check if the documents are dictionaries
    if isinstance(doc1, dict) and isinstance(doc2, dict):
        # Check if the keys in doc1 are the same as in doc2
        if doc1.keys() != doc2.keys():
            return False

        # Compare the values for each key in doc1 and doc2
        for key in doc1.keys():
            if not compare_documents(doc1[key], doc2[key]):
                return False

        # If all keys and values are equal, the documents are the same
        return True

    # Check if the documents are lists
    elif isinstance(doc1, list) and isinstance(doc2, list):
        # Check if the lengths of the lists are the same
        if len(doc1) != len(doc2):
            return False

        # Compare each element in the lists
        for elem1, elem2 in zip(doc1, doc2):
            if not compare_documents(elem1, elem2):
                return False

        # If all elements are equal, the documents are the same
        return True

    # Compare the values of other types directly
    else:
        return doc1 == doc2

def duplicate_collection(mongo_db, source_collection, dest_collection, pipeline=[{"$match": {}}]):
    print(f"Duplicating collection {source_collection}...")

    pipeline.append({"$out": dest_collection})
    
    mongo_db.perform_aggregation(source_collection, pipeline)
    
    print(f"Collection {source_collection} duplication complete.")

def toFile(file_name, documents):
    with open(file_name, "w") as outfile:
        outfile.write(json_util.dumps(documents))

    print(f"All documents have been saved to {file_name}")