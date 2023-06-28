import streamlit as st
from pymongo import MongoClient
import certifi
import generic

def summary_page():
    # Connessione al database MongoDB
    ca = certifi.where()
    client = MongoClient('mongodb+srv://Pasquale:cJ0RhXpFoKRPsmxt@cluster0.k9yxetn.mongodb.net/', tlsCAFile=ca)
    db = client.healthcareDB
    collection = db.patients_summ

    st.title(":red[SUMMARIZATION]")
    st.subheader("Questa sezione permette di accedere rapidamente alle informazione generiche del paziente tramite una summarization protdatto dall'AI.")

    st.markdown("---")

    documents = list(collection.find())

    # Lista dei titoli dei documenti
    patient_ids  = [doc['patient_id'] for doc in documents]

    selected_patient_id = st.selectbox("SELEZIONARE L'ID DEL PAZIENTE:", sorted(patient_ids ))
    st.markdown("----", unsafe_allow_html=True)
    

    st.markdown(f"<div style='background-color: #26252d; padding: 10px;'><h4 style='color: #4897ff;'>SUMMARIZATION DEL PAZIENTE</h4></div>", unsafe_allow_html=True)

    # Trova il documento corrispondente al patient_id selezionato
    selected_document = next((doc for doc in documents if doc["patient_id"] == selected_patient_id), None)


    # Visualizza il campo "summarization" del documento selezionato
    if selected_document:
        summarization = selected_document.get("summarization", "")
        result=generic.insert_newlines(summarization)
        ##Sostituisce \n con <br> perche si passa da una stringa ad una stringa html, ci permette di mantenere le caratteristiche di markdown
        result_with_line_breaks = result.replace('\n\n', '<br><br>')
        st.markdown(f"<div style='background-color: #26252d; padding: 10px;'><h5>{result_with_line_breaks}</h5></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<h5>Summarization non disponibile.</h5>", unsafe_allow_html=True)
