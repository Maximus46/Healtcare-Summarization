import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load config from .env file
load_dotenv()

class MongoDB:
    _instance = None

    def __new__(cls, database_name):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = None
            cls._instance.database = None
            cls._instance.initialize(database_name)
        return cls._instance

    def initialize(self, database_name):
        if self.client is None:
            mongodb_uri = os.environ["MONGODB_URI"]
            self.client = MongoClient(mongodb_uri)
            self.database = self.client[database_name]

    def close_connection(self):
        self.client.close()

    def get_collection(self, collection_name):
        return self.database[collection_name]

   
    def insert_document(self, collection_name, document):
        try:
            collection = self.get_collection(collection_name)
            result = collection.insert_one(document)
            return result.inserted_id
        except Exception as e:
            # Handle the exception or log the error
            print(f"Error inserting document: {e}")
            return None

    def insert_documents(self, collection_name, documents):
        try:
            collection = self.get_collection(collection_name)
            result = collection.insert_many(documents)
            return result.inserted_ids
        except Exception as e:
            # Handle the exception or log the error
            print(f"Error inserting documents: {e}")
            return None

    def find_document(self, collection_name, filter=None, projection=None):
        try:
            collection = self.get_collection(collection_name)
            return collection.find_one(filter, projection)
        except Exception as e:
            # Handle the exception or log the error
            print(f"Error finding document: {e}")
            return None

    def find_documents(self, collection_name, filter=None, projection=None):
        try:
            collection = self.get_collection(collection_name)
            return collection.find(filter, projection)
        except Exception as e:
            # Handle the exception or log the error
            print(f"Error finding documents: {e}")
            return None

    def update_document(self, collection_name, query, document):
        try:
            collection = self.get_collection(collection_name)
            result = collection.update_one(query, {"$set": document})
            return result.modified_count
        except Exception as e:
            # Handle the exception or log the error
            print(f"Error updating document: {e}")
            return 0

    def update_documents(self, collection_name, query, update, upsert=False):
        try:
            collection = self.get_collection(collection_name)
            result = collection.update_many(query, update, upsert=upsert)
            return result.modified_count
        except Exception as e:
            # Handle the exception or log the error
            print(f"Error updating documents: {e}")
            return 0

    def delete_documents(self, collection_name, query):
        try:
            collection = self.get_collection(collection_name)
            result = collection.delete_many(query)
            return result.deleted_count
        except Exception as e:
            # Handle the exception or log the error
            print(f"Error deleting documents: {e}")
            return 0

    def perform_aggregation(self, collection_name, pipeline):
        try:
            collection = self.get_collection(collection_name)
            return list(collection.aggregate(pipeline))
        except Exception as e:
            # Handle the exception or log the error
            print(f"Error performing aggregation: {e}")
            return []
    
    def create_index(self, collection_name, index, unique=False):
        try:
            collection = self.get_collection(collection_name)
            index_name = index + '_index'
            index_key = [(index, 1)]
            index_options = {'unique': unique}
            collection.create_index(index_key, name=index_name, **index_options)
            return True
        except Exception as e:
            # Handle the exception or log the error
            print(f"Error creating index: {e}")
            return False
        
    def get_patient_ids(self, collection_name):
        try:
            collection = self.get_collection(collection_name)
            cursor = collection.find({}, {'patient_id': 1}).hint('patient_id_index')
            patient_ids = [doc['patient_id'] for doc in cursor]
            return patient_ids
        except Exception as e:
            # Handle the exception or log the error
            print(f"Error getting patient IDs: {e}")
            return []

    def bulk_write(self, collection_name, operations):
        try:
            collection = self.get_collection(collection_name)
            result = collection.bulk_write(operations)
            return result
        except Exception as e:
            print(f"Error performing bulk write: {e}")
            return None