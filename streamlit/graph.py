import streamlit as st
import re
import logging
from streamlit_agraph import agraph, Node, Edge, Config
from queries.neo4j_queries import get_patient_data

# Import MongoDB and Neo4jConnector classes
from database.mongo_db import MongoDB
from database.neo4j_db import Neo4jConnector


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---- CONFIGURAZIONE PER AGRAPH
config = Config(
    width=2000,
    height=600,
    directed=True,
    physics={
        "barnesHut": {
            "gravitationalConstant": -14000,
            "centralGravity": 0.3,
            "springLength": 300,
            "springConstant": 0.02,
            "damping": 0.09,
            "avoidOverlap": 1
        }
    },
    hierarchical=True
)

ENTITY_COLORS = {
    "MedicalProblem": "green",
    "Test": "purple",
    "Treatment": "orange"
}

# Process the retrieved patient data to create nodes and edges for the graph visualization.
def create_graph_data(records):
    nodes = []
    edges = []
    ids = set()
    has_data = False

    for record in records:
        has_data = True

        # Access nodes and relationships using Neo4j Graph Objects
        patient_node = record["p"]
        entity_node = record["e"]
        concept_node = record["c"]
        relationship1 = record["r1"]
        relationship2 = record["r2"]

        patient_id = patient_node["patient_id"]
        entity_label = list(entity_node.labels)[0]
        entity_text = entity_node["text_EN"]
        concept_name = concept_node["concept_name"]
        
        # Add patient node
        patient_id = int(re.findall(r"\d+$", patient_node.element_id)[0])
        if patient_id not in ids:
            ids.add(patient_id)
            nodes.append(Node(id=patient_id, label=str(patient_id), size=30, color="red"))

        #  Add entity node
        entity_id = int(re.findall(r"\d+$", entity_node.element_id)[0])
        if entity_id not in ids:
            ids.add(entity_id)
            color = ENTITY_COLORS.get(entity_label, "gray")
            nodes.append(Node(id=entity_id, label=entity_text, size=25, color=color))

        # Add concept node
        concept_id = int(re.findall(r"\d+$", concept_node.element_id)[0])
        if concept_id not in ids:
            ids.add(concept_id)
            nodes.append(Node(id=concept_id, label=str(concept_name), size=20, color="blue"))

        # Add edges
        edges.append(Edge(source=patient_id, label=relationship1.type, target=entity_id, color="white"))
        edges.append(Edge(source=entity_id, label=relationship2.type, target=concept_id, color="white"))

    return nodes, edges, has_data

# Visualize patient data using the agraph function from streamlit_agraph.
def visualize_patient_data(nodes, edges, has_data: bool, config: Config):
    with st.expander("__The diseases associated with each patient's clinical note__", expanded=True):
        if has_data:
            st.markdown(
            "<div style='font-weight: bold; display: inline-block;'>LEGEND COLOR: </div>"
            "<div style='display: inline-block; color: red;'> PATIENTS -</div>"
            "<div style='display: inline-block; color: green;'>MEDICAL_PROBLEM -</div>"
            "<div style='display: inline-block; color: purple;'>TEST -</div>"
            "<div style='display: inline-block; color: orange;'>TREATMENT -</div>"
            "<div style='display: inline-block; color: blue;'>CONCEPT</div>",
            unsafe_allow_html=True
            )
            st.write(" ")  # Add spacing for better aesthetics
            agraph(nodes=nodes, edges=edges, config=config)
        else:
            st.caption("There are no diseases associated with this patient.")

def retrieve_patient_ids(mongo_db: MongoDB, collection: str):
    
    # Retrieve only the necessary fields from the patients collection
    filter_query = {}
    projection_query = {'patient_id': 1}
    patients_cursor = mongo_db.find_documents(collection, filter_query, projection_query)
    
    # Get the list of patient IDs
    patient_ids = [patient['patient_id'] for patient in patients_cursor]

    return patient_ids

def configure_streamlit_page (page_title, page_icon, layout):
    # Set page configuration
    st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
    
    # Set app title
    st.title(page_title + " " + page_icon)
    st.caption("Analyze patient's health data through interactive graph visualizations for comprehensive insights: ") 

# Constants
DATABASE = "healthcareDB"
COLLECTION = "patients_20"
PAGE_TITLE = "Neo4j Graph"
PAGE_ICON = "🩺"
LAYOUT = "wide"

def display_graph():
    # Call the configure_streamlit_app function at the beginning of your main script
    # configure_streamlit_page (PAGE_TITLE, PAGE_ICON, LAYOUT)
    
    # Connect to MongoDB cluster with MongoClient
    mongo_db = MongoDB(DATABASE)
    
    patient_ids = retrieve_patient_ids(mongo_db, COLLECTION)
    
    print("IDS: ", patient_ids)
    
    # Connects to Neo4j
    neo4j_connector = Neo4jConnector()
    logger.info("Connected to Neo4j")

    # Create a selectbox to choose the patient_id
    selected_patient = st.selectbox('Pick a patient_id to retrieve the graph', patient_ids, help='This is help')
    
    patient_data = get_patient_data(neo4j_connector, selected_patient)
    logger.info("Retrieved patient data from Neo4j")

    nodes, edges, has_data = create_graph_data(patient_data)
    logger.info("Created graph data")
    
    visualize_patient_data(nodes, edges, has_data, config)
    
    
