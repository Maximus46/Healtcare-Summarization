import logging
import re
from database.neo4j_db import Neo4jConnector
from database.mongo_db import MongoDB

# Constants
MONGO_DATABASE = 'healthcareDB'
PATIENTS_COLLECTION = 'patients_20'
ENTITIES_COLLECTION = 'patients_entities'

# Mapping of entity types to relationship types
ENTITY_RELATIONSHIPS = {
    "MedicalProblem": "HAS_MEDICAL_PROBLEM",
    "Treatment": "RECEIVED_TREATMENT",
    "Test": "DONE_TEST"
}

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def process_patient_entities(neo4j_connector, document):
    patient_id = document["patient_id"]
    entities = document.get("entities", [])

    patient_node_id = create_patient_node(neo4j_connector, patient_id)
    logger.info("Created patient node with ID: %s", patient_node_id)

    # Iterate over each entity
    for entity in entities:
        cui = entity["CUI"]
        text = entity["text"]
        text_en = entity["text_EN"]
        entity_type = entity["type"]
        concept_name = entity["concept_name"]

        if not all([cui, text, text_en, entity_type, concept_name]):
                    logger.warning("Skipping entity due to missing required fields.")
                    continue
        try:
            entity_node_id = create_entity_node(neo4j_connector, entity_type, text, text_en)
            logger.info("Created entity node with ID: %s", entity_node_id)

            # Create a relationship between the patient and the entity
            relationship_type = ENTITY_RELATIONSHIPS.get(entity_type)
            if relationship_type is None:
                raise ValueError(f"Invalid entity_type: {entity_type}")
            neo4j_connector.create_relationship(patient_node_id, entity_node_id, relationship_type)

            # Create a node for the concept
            concept_node_id = create_concept_node(neo4j_connector, cui, concept_name)
            logger.info("Created concept node with ID: %s", concept_node_id)

            # Create a relationship between the entity and the concept
            neo4j_connector.create_relationship(entity_node_id, concept_node_id, "HAS_CONCEPT")
        except Exception as e:
            logger.error("Error occurred while processing entity (Patient ID: %s, Entity ID: %s): %s", patient_id, entity_node_id, str(e))
            
def create_patient_node(neo4j_connector, patient_id):
    patient_query = """
        MERGE (n:Patient {patient_id: $patient_id_param})
        ON CREATE SET n.created = timestamp()
        ON MATCH SET n.updated = timestamp()
        RETURN ID(n) as node_id
    """
    patient_properties = {"patient_id_param": patient_id}
    return neo4j_connector.create_node(patient_query, patient_properties)

def create_entity_node(neo4j_connector, entity_type, text, text_en):
    entity_query = f"""
        MERGE (n:{entity_type} {{text: $text_param, text_EN: $text_EN_param}})
        ON CREATE SET n.created = timestamp()
        ON MATCH SET n.updated = timestamp()
        RETURN ID(n) as node_id
    """
    entity_properties = {"text_param": text, "text_EN_param": text_en}
    return neo4j_connector.create_node(entity_query, entity_properties)    

def create_concept_node(neo4j_connector, cui, concept_name):
    concept_query = """
        MERGE (n:Concept {cui: $cui_param, concept_name: $concept_name_param})
        ON CREATE SET n.created = timestamp()
        ON MATCH SET n.updated = timestamp()
        RETURN ID(n) as node_id
    """
    concept_properties = {"cui_param": cui, "concept_name_param": concept_name}
    return neo4j_connector.create_node(concept_query, concept_properties)

def populate_neo4j():
    try:
        # Create Neo4j connector
        neo4j_connector = Neo4jConnector()
        
        # Connect to MongoDB
        mongo_db = MongoDB(MONGO_DATABASE)
        
        # Retrieve patient entities from MongoDB
        patients_entities = mongo_db.find_documents(ENTITIES_COLLECTION)

        # Create constraints
        neo4j_connector.create_constraint("Patient", "patient_id")
        neo4j_connector.create_constraint("Concept", "cui")
        
        logger.info("Starting Neo4j population...")

        # Iterate over each document in patients_entities
        for document in patients_entities:
            logger.info("Processing document: %s", document["patient_id"])
            process_patient_entities(neo4j_connector, document)
            
        logger.info("Neo4j population completed successfully.")
    except Exception as e:
        logger.error("An error occurred during Neo4j population: %s", str(e))
        raise
    
    finally:
        # Close the connection to Neo4j
        neo4j_connector.close()

        # Close the connection to MongoDB
        mongo_db.close_connection()

if __name__ == "__main__":
    populate_neo4j()
