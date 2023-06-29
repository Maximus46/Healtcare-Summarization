import streamlit as st
import pandas as pd
from database.mongo_db import MongoDB
import plotly.express as px
from queries.query1 import query_1 as q1
from queries.query2 import query_2 as q2
from queries.query3 import query_3
from queries.query4 import query_4 as q4

# Constants
DATABASE = "healthcareDB"
COLLECTION = "patients"

@st.cache_data
def plot_exam_distribution(_mongo_db: MongoDB, collection: str):
    data = _mongo_db.perform_aggregation(collection, query_3())

    df = pd.DataFrame(data)
    print("DATAFRAME: ", df)
    # Visualization - Exam Distribution

    # Check if exam_distribution_selected dataframe is empty
    if df.empty:
        st.warning("No data available for the selected patient.")

    else:
        # Create the bar plot
        fig = px.bar(df, x='exam_name', y='count',
                    color='count', hover_data={'count': ':.2f'})
        
        # Update the layout to make the plot vertical and adjust the width
        fig.update_layout(xaxis_title='Exam Type', yaxis_title='Occurrencies',
                        title='Exam Distribution Across All Patients.')
        fig.update_traces(#marker_color='rgba(50, 171, 96, 0.6)', marker_line_color='rgb(0, 0, 0)',
                        marker_line_width=1.5, opacity=0.8)
        fig.update_layout(height=800, width=1200)

        # Show the plot using st.plotly_chart
        st.plotly_chart(fig, use_container_width=True)

@st.cache_data()
def analytics():  
    # Connessione al database MongoDB
    mongo_db = MongoDB(DATABASE)
    #Prelevare solo tramite id
    collection=mongo_db.get_collection(COLLECTION)

    #Intro della pagina
    st.title(":red[ANALYTICS]")
    st.subheader("Questa sezione fornisce strumenti e visualizzazioni avanzate per l'analisi dei dati, consentendo agli utenti di ottenere risultati significativi.")
    st.markdown("---")

    col1, col2 = st.columns(2)
    #Query 1
    graph1, percentuale, total_count = q1(collection)
    col1.header(":blue[Analytic1]")
    col1.markdown("<h5>Questa query calcola la percentuale di pazienti con familiari ipertesi rispetto al totale dei pazienti presenti nel database. Per il calcolo utilizza l'esito positivo di almeno uno dei seguenti campi, 'FRATELLIIPERTESI', 'MADREIPERTESA' e 'PADREIPERTESO'.", unsafe_allow_html=True)
    col1.pyplot(graph1)
    col1.subheader(":red[Risultati:]")
    col1.text(f"Percentuale: {round(percentuale,1)} %")
    col1.text(f"Conteggio totale: {total_count}")

    #Query 2
    graph2, pamax_mean, pamax_std, pamin_mean, pamin_std = q2(collection)   
    col2.header(":blue[Analytic2]")
    col2.markdown("<h5>Questa query calcola l'andamento della normale dei parametri pamax e pamin dobbiamo scrivere bene sta cosa", unsafe_allow_html=True)
    col2.pyplot(graph2)
    # Stampa dei risultati
    col2.subheader(":red[Risultati:]")
    col11, col22 = col2.columns(2)
    col11.caption(":blue[PAMAX_BEFORETERAPIA]")
    col11.text(f"Media: {round(pamax_mean,2)}")
    col11.text(f"Dev: {round(pamax_std,2)}")
    col22.caption(":blue[PAMIN_BEFORETERAPIA]")
    col22.text(f"Media: {round(pamin_mean,2)}")
    col22.text(f"Dev: {round(pamin_std,2)}")
    st.markdown("---")


    #Query 3
    st.header(":blue[Analytic3]")
    st.markdown("<h5>Questa query calcola il numero totali di esami e visite effettutate dai pazienti.", unsafe_allow_html=True)
    plot_exam_distribution(mongo_db, COLLECTION)
    st.markdown("---")
    
    #Query 4
    col1, col2 = st.columns(2)
    col1.header(":blue[Analytic4]")
    col1.markdown("<h5>Questa query calcola la percentuale di pazienti affetti da alcol", unsafe_allow_html=True)
    graph4, percentuale4, total_count4 = q4(collection)
    col1.pyplot(graph4)
    col1.subheader(":red[Risultati:]")
    col1.text(f"Percentuale: {round(percentuale4,2)} %")
    col1.text(f"Conteggio totale: {total_count4}")