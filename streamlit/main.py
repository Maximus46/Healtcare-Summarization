import streamlit as st
from streamlit_option_menu import option_menu
import patient as fs
import home as hm
import generic as ge
import analytics as an
import summarization as su
import exams as ex

def main():

    ge.imposta_sfondo()

    with st.sidebar:
        selected = option_menu("Healthcare", ["Home", 'Paziente','Summarization','Visite/Esami','Prenotazioni','Interventi','Ricevute','Analytics'], 
            icons=['house', 'exclamation-circle','plus','search','calendar','caret-down','file', 'question'], menu_icon="heart", default_index=0)
        

    # Controlla quale voce del menu è stata selezionata
    if selected == "Home":
        # Inserisci qui le funzionalità per la pagina Home
        hm.home()
    elif selected == "Paziente":
        # Inserisci qui le funzionalità per la pagina Paziente
        fs.info_patient()
    elif selected == "Summarization":
        # Inserisci qui le funzionalità per la pagina Dati generici
        su.summary_page()
    elif selected == "Visite/Esami":
        # Inserisci qui le funzionalità per la pagina Visite/Esami
        ex.list_exams_page()  
    elif selected == "Prenotazioni":
        # Inserisci qui le funzionalità per la pagina Prenotazioni
        st.text("Da fare...")
    elif selected == "Interventi":
        # Inserisci qui le funzionalità per la pagina Interventi
        st.text("Da fare...")
    elif selected == "Ricevute":
        # Inserisci qui le funzionalità per la pagina Ricevute
        st.text("Da fare...")
    elif selected == "Analytics":
        # Inserisci qui le funzionalità per la pagina Analytics
        an.analytics()

    expander = st.sidebar.expander("DESCRIZIONE DELLA DASHBOARD")


    # Aggiunta del testo lungo all'interno della sezione
    with expander:
        st.subheader(":blue[Home]")
        st.markdown("Questa sezione fornisce una panoramica generale dell'applicazione e offre un punto di partenza per la navigazione.")

        st.subheader(":blue[Paziente]")
        st.markdown("Questa sezione consente di visualizzare informazioni dettagliate sui pazienti, come nome, cognome, età e altri dati correlati.")

        st.subheader(":blue[Summarization]")
        st.markdown("Questa sezione consente di visualizzare una summarization del paziente di tutta la sua storia clinica.")

        st.subheader(":blue[Visite/Esami]")
        st.markdown("Questa sezione consente di accedere alla lista sulle visite e sugli esami effettuati dai pazienti.")

        st.subheader(":blue[Prenotazioni]")
        st.markdown("Questa sezione consente di gestire le prenotazioni dei pazienti.")

        st.subheader(":blue[Interventi]")
        st.markdown("Questa sezione consente di visualizzare informazioni sugli interventi medici effettuati sui pazienti, come ad esempio tipologia, data, risultati e altre informazioni correlate.")

        st.subheader(":blue[Ricevute]")
        st.markdown("Questa sezione permette di generare e visualizzare le ricevute delle prestazioni sanitarie fornite ai pazienti.")

        st.subheader(":blue[Analytics]")
        st.markdown("Questa sezione fornisce strumenti e visualizzazioni avanzate per l'analisi dei dati, consentendo agli utenti di ottenere risultati significativi.")


if __name__ == "__main__":
    main()