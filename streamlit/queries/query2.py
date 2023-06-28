import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

def query_2(collection):
    # Query per prelevare i campi "PAMAX_BEFORETERAPIA" e "PAMIN_BEFORETERAPIA" per tutti i documenti
    documents = collection.find({}, {"visits.PAMAX_BEFORETERAPIA": 1, "visits.PAMIN_BEFORETERAPIA": 1})

    # Liste per i valori non nulli
    pamax_values = []
    pamin_values = []

    # Iterazione sui documenti e aggiunta dei valori non nulli alle liste
    for document in documents:
        visits = document.get("visits", [])
        #print(document)
        for visit in visits:
            pamax_beforeterapia = visit.get("PAMAX_BEFORETERAPIA")
            pamin_beforeterapia = visit.get("PAMIN_BEFORETERAPIA")
            if pamax_beforeterapia is not None and pamax_beforeterapia != 0:
                pamax_values.append(pamax_beforeterapia)
            if pamin_beforeterapia is not None and pamin_beforeterapia != 0:
                pamin_values.append(pamin_beforeterapia)
                break

    # Calcolo dei parametri per la distribuzione gaussiana
    pamax_mean = np.mean(pamax_values)
    pamax_std = np.std(pamax_values)
    pamin_mean = np.mean(pamin_values)
    pamin_std = np.std(pamin_values)

    # Generazione dei dati per le curve della gaussiana
    x = np.linspace(min(pamax_mean - 3 * pamax_std, pamin_mean - 3 * pamin_std),
                    max(pamax_mean + 3 * pamax_std, pamin_mean + 3 * pamin_std), 100)
    y_pamax = 1 / (pamax_std * np.sqrt(2 * np.pi)) * np.exp(-(x - pamax_mean) ** 2 / (2 * pamax_std ** 2))
    y_pamin = 1 / (pamin_std * np.sqrt(2 * np.pi)) * np.exp(-(x - pamin_mean) ** 2 / (2 * pamin_std ** 2))

    # Creazione del grafico
    fig, ax = plt.subplots(facecolor='None')
    ax.set_facecolor('none')
    fig.set_size_inches(5, 4)

    # Tracciamento della curva della gaussiana per "PAMAX_BEFORETERAPIA"
    ax.plot(x, y_pamax, label="PAMAX_BEFORETERAPIA")


    # Tracciamento della curva della gaussiana per "PAMIN_BEFORETERAPIA"
    ax.plot(x, y_pamin, label="PAMIN_BEFORETERAPIA", color="red")

    # Configurazione del grafico
    ax.set_xlabel("Valori").set_color("white")
    ax.set_ylabel("Densità").set_color("white")
    ax.set_title("Gaussiana").set_color("white")
    ax.legend(framealpha=0.0)
    ax.tick_params(axis="x", colors="white")
    ax.tick_params(axis="y", colors="white")
    return fig, pamax_mean, pamax_std, pamin_mean, pamin_std
