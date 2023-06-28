import streamlit as st
import certifi
import math
import pandas as pd
from queries.neo4j_queries import get_patient_entities
from pymongo import MongoClient
from database.neo4j_db import Neo4jConnector

def info_patient():
    # Connessione al database MongoDB
    ca = certifi.where()
    client = MongoClient('mongodb+srv://Pasquale:cJ0RhXpFoKRPsmxt@cluster0.k9yxetn.mongodb.net/', tlsCAFile=ca)
    db = client.healthcareDB

    # Prelevare solo tramite id
    collection_id=db.patients_20
    documents = list(collection_id.find())

    # Create Neo4j connector
    neo4j_connector = Neo4jConnector()
    
    descrizione()

    selected_patient=select_box(documents)

    if selected_patient:
        dati_personali()
        dati_clinici(selected_patient)
        anamnesi(selected_patient)
        display_patient_entities(neo4j_connector, selected_patient['patient_id'])
    else:
        st.write("Paziente non trovato.")

##################FUNZIONI##################
def descrizione():
    st.title(":red[PAZIENTE]")
    st.subheader("Questa sezione permette di accedere rapidamente alle informazione generiche del paziente.")
    st.markdown("----", unsafe_allow_html=True)

def dati_personali():
    st.subheader(":red[DATI ANAGRAFICI]")
    col1, col2, col3, col4 = st.columns(4)

    chiave = ["NOME", "COGNOME", "PROV.", "DATA DI NASCITA", "SESSO", "CODICE FISCALE",
              "INDIRIZZO RESIDENZA", "INDIRIZZO RESIDENZA", "CITTA'", "TELEFONO", "NAZIONALITA'", "ASL"]
    valore = ["MARIO", "ROSSI", "NA", "01\\01\\88", "M", "XXXXXXXXXXXXXXXX",
              "VIA CLAUDIO, 1", "80013", "NAPOLI", "(+39) 3333333333", "ITALIA", "NAPOLI"]

    metà = math.ceil(len(chiave) / 2)

    for i in range(metà):
        col1.markdown(f":blue[**{chiave[i]}:**] <br>", unsafe_allow_html=True)
        col2.markdown(f"{valore[i]}<br>", unsafe_allow_html=True)

    for i in range(metà, len(chiave)):
        col3.markdown(f":blue[**{chiave[i]}:**] <br>", unsafe_allow_html=True)
        col4.markdown(f"{valore[i]}<br>", unsafe_allow_html=True)

    st.markdown("----", unsafe_allow_html=True)

def dati_clinici(selected_patient):
    #Codice per il conteggio esami e visite dei dati clinici
    # Conteggio dei campi 'name' in 'visits' del paziente
    visits = selected_patient['visits']
    esami_count = 0
    visite_count = 0

    for visit in visits:
        if 'name' in visit and isinstance(visit['name'], str):
            if visit['name'].startswith("ESAM"):
                esami_count += 1
            elif visit['name'].startswith("VISIT"):
                visite_count += 1

    st.subheader(":red[DATI CLINICI]")
    col1, col2 = st.columns(2)
    
    col1.markdown(":blue[**REPARTO:**] <br>", unsafe_allow_html=True)
    col1.markdown(":blue[**PATIENT_ID:**] <br>", unsafe_allow_html=True)
    col1.markdown(":blue[**DECEDUTO:**] <br>", unsafe_allow_html=True)
    col1.markdown(":blue[**NUMERO DELLE VISITE:**] <br>", unsafe_allow_html=True)
    col1.markdown(":blue[**NUMERO DEGLI ESAMI:**] <br>", unsafe_allow_html=True)

    col2.markdown("CARDIOLOGIA <br>", unsafe_allow_html=True)
    col2.markdown(f"{selected_patient['patient_id']} <br>", unsafe_allow_html=True)
    col2.markdown(f"{selected_patient['_DECEDUTO']} <br>", unsafe_allow_html=True)
    col2.markdown(f"{esami_count} <br>", unsafe_allow_html=True)
    col2.markdown(f"{visite_count} <br>", unsafe_allow_html=True)
    st.markdown("----", unsafe_allow_html=True)

def anamnesi(selected_patient):
    st.subheader(":red[ANAMNESI]")
    col1, col2 = st.columns(2)
    car=":"
    visits = selected_patient['visits']
    for visit in visits:
        if 'name' in visit and visit['name'] == "ANAMNESI":
            visit.pop('exams', None)
            visit.pop('start_date', None)
            visit.pop('name', None)
            # Sostituisci i valori "0" con "NO" e "1" con "SI"
            visit = {key: "NO" if value == "0" else "SI" if value == "1" else value for key, value in visit.items()}
            for key, value in visit.items():
                col1.markdown(f"<span style='white-space: nowrap; color:#4897ff'><b>{key}</b><b>{car}</b></span>", unsafe_allow_html=True)
                col2.markdown(f"{value} <br>", unsafe_allow_html=True)

def display_patient_entities(neo4j_connector, patient_id):
    st.subheader(':red[**List of MedicalProblems, Test and Treatment**]')

    if not patient_id:
        st.warning("Please enter a Patient ID")
        return

    # Retrieve patient data from Neo4j
    patient_data = get_patient_entities(neo4j_connector, patient_id)

    if not patient_data:
        st.warning("No data found for the given Patient ID")
        return
    
    data = {
        "Medical Problem": patient_data.get("MedicalProblems", []),
        "Test": patient_data.get("Tests", []),
        "Treatment": patient_data.get("Treatments", []),
    }    
    
    num_columns = len(data)
    columns = st.columns(num_columns)

    for i, (category, values) in enumerate(data.items()):
        with columns[i]:
            # st.markdown(f"**{category}s**")
            if values:
                df = pd.DataFrame({category: values})
                st.dataframe(df, hide_index=True, use_container_width=True)           
            else:
                st.info(f"No {category.lower()}s found.")

def select_box(documents):
    # Creazione della select box per selezionare il patient_id
    patient_ids = [doc['patient_id'] for doc in documents]
    selected_patient_id = st.selectbox("Seleziona il patient_id", patient_ids)
    st.markdown("----", unsafe_allow_html=True)
    selected_patient = next((doc for doc in documents if doc['patient_id'] == selected_patient_id), None)
    return selected_patient