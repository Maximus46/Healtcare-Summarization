import streamlit as st
from pymongo import MongoClient
import certifi

def list_exams_page():
    # Connessione al database MongoDB
    ca = certifi.where()
    client = MongoClient('mongodb+srv://Pasquale:cJ0RhXpFoKRPsmxt@cluster0.k9yxetn.mongodb.net/', tlsCAFile=ca)
    db = client.healthcareDB

    collection = db.patients_20
    # Ottieni tutti i documenti dalla collezione
    documents = list(collection.find())

    # Lista dei titoli dei documenti
    document_titles = [doc['patient_id'] for doc in documents]

    st.title(":red[ESAMI DEL PAZIENTE]")
    st.subheader("Questa sezione permette di accedere rapidamente alle informazioni essenziali relative agli esami effettuati dal paziente, consentendoti di avere una panoramica completa della sua storia medica.")
    st.markdown("----", unsafe_allow_html=True)
    # Sidebar per la selezione del documento
    selected_doc_index = st.selectbox("SELEZIONARE L'ID DEL PAZIENTE:", sorted(document_titles))
    st.markdown("----", unsafe_allow_html=True)
    # Trova il documento selezionato
    selected_doc = next((doc for doc in documents if doc['patient_id'] == selected_doc_index), None)
    
    if selected_doc:
        for visit in reversed(selected_doc.get('visits', [])):
            visit_exams = visit.get('exams', [])
            for exam in reversed(visit_exams):
                exam_name = exam.get('name', "")
                exam_date = exam.get('exam_date', "")  
                
                if exam_name and exam_date:
                    unstructured_data = exam.get('unstructured', {})
                    filtered_data = [(key, str(value).lower()) for key, value in unstructured_data.items() if key not in ['name', 'exam_date'] and value and len(str(value)) > 35]
                    
                    if filtered_data:
                        col1, col2, col3 = st.columns(3)
                        col1.markdown(f"<h5 style='white-space: nowrap;'><span style='color:#4897ff'>ESAME:</span> <span style='color:#ffffff'>{exam_name}</span></h5>", unsafe_allow_html=True)
                        col3.markdown(f"<h5 style='white-space: nowrap;'><span style='color:#4897ff'>DATA ESAME:</span> <span style='color:#ffffff'>{exam_date}</span></h5>", unsafe_allow_html=True)
                      
                        for key, value in filtered_data:
                            st.markdown(f":green[**{key}:**] {value}", unsafe_allow_html=True)
                        st.markdown("---")
