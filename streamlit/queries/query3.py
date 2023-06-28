import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import RendererAgg

def query_3(collection):

    pipeline = [
        {
            '$unwind': '$visits'
        },
        {
            '$match': {
                'visits.exams': {'$exists': True},
                'visits.name': {'$nin': ['EMERGENZA', 'DAY_HOSPITAL', 'ANAMNESI']}
            }
        },
        {
            '$group': {
                '_id': '$patient_id',
                'exams': {'$addToSet': '$visits.exams.name'}
            }
        },
        {
            '$unwind': '$exams'
        },
        {
            '$group': {
                '_id': '$exams',
                'count': {'$sum': 1}
            }
        },
        {
            '$project': {
                '_id': 0,
                'exam_name': '$_id',
                'count': 1
            }
        },
        {
            '$match': {
                'exam_name': {'$ne': None, '$ne': ''}
            }
        }
    ]

    _lock = RendererAgg.lock

    # Esegui la pipeline di aggregazione
    result = list(collection.aggregate(pipeline))

    # Estrai i dati dal risultato della pipeline
    exam_names = [str(doc['exam_name'][0]) for doc in result]
    exam_counts = [doc['count'] for doc in result]

    # Crea il grafico a barre
    fig, ax = plt.subplots(figsize=(8, 3),facecolor='None')
    ax.set_facecolor('none')

    with _lock:
        ax.bar(exam_names, exam_counts)
        ax.set_xlabel('Esami').set_color("white")
        ax.set_ylabel('Conteggio').set_color("white")
        ax.set_title('Conteggio Esami').set_color("white")
        ax.tick_params(axis='x', rotation=90, labelsize=6)
        ax.tick_params(axis="x", colors="white")
        ax.tick_params(axis="y", colors="white")

    # Mostra il grafico utilizzando Streamlit
    #st.pyplot(fig)

    # # Stampa il conteggio per ogni esame
    # for doc in result:
    #     print("Esame:", doc['exam_name'])
    #     print("Conteggio:", doc['count'])
    #     print("---")
    return fig