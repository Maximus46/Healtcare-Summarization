import matplotlib.pyplot as plt

def query_4(collection):
    total_documents = collection.estimated_document_count()
    pipeline = [
        {
            '$match': {
                'visits': {
                    '$elemMatch': {
                        'name': 'ANAMNESI',
                        'ALCOOL': '1'
                    }
                }
            }
        },
        {
            '$group': {
                '_id': None,
                'count': {'$sum': 1}
            }
        },
        {
            '$project': {
                '_id': 0,
                'count': 1
            }
        }
    ]


    # Esegui la pipeline di aggregazione
    result = list(collection.aggregate(pipeline))

    if result:
        total_count = result[0]['count']
    else:
        total_count = 0

    # Calcola la percentuale
    percentuale = (total_count / total_documents) * 100

    # Crea il grafico a torta
    labels = ['Pazienti AFFETTI da alcol', 'Pazienti NON AFFETTI da alcol']
    sizes = [total_count, total_documents - total_count]
    colors = ['#59c795', '#607D8B']
    explode = (0.1, 0)

    fig, ax = plt.subplots(facecolor='None')
    fig.set_size_inches(5, 4)
    patches, text, autotext = ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, labeldistance=1.05)
    plt.setp(text, color='white')
    plt.setp(autotext, color='white')
    ax.axis('equal')

    return fig,percentuale,total_count