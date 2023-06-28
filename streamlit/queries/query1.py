import matplotlib.pyplot as plt

def query_1(collection):
    # Calcola il conteggio approssimativo dei documenti nella collezione
    total_documents = collection.estimated_document_count()

    # Crea la pipeline di aggregazione
    pipeline = [
        {
            '$project': {
                '_id': 0,
                'ANAMNESI': {
                    '$filter': {
                        'input': '$visits',
                        'cond': {'$eq': ['$$this.name', 'ANAMNESI']}
                    }
                }
            }
        },
        {
            '$project': {
                'FRATELLIIPERTESI': '$ANAMNESI.FRATELLIIPERTESI',
                'MADREIPERTESA': '$ANAMNESI.MADREIPERTESA',
                'PADREIPERTESO': '$ANAMNESI.PADREIPERTESO'
            }
        },
        {
            '$match': {
                '$or': [
                    {'FRATELLIIPERTESI': '1'},
                    {'MADREIPERTESA': '1'},
                    {'PADREIPERTESO': '1'}
                ]
            }
        },
        {
            '$count': 'total'
        }
    ]

    # Esegui la pipeline di aggregazione
    result = list(collection.aggregate(pipeline))

    # Verifica se la lista dei risultati è vuota
    if result:
        total_count = result[0]['total']
    else:
        total_count = 0

    # Calcola la percentuale
    percentuale = (total_count / total_documents) * 100

    ##DEBUG
    # # Stampa il conteggio totale
    # print("Conteggio totale:", total_count)

    # # Stampa la percentuale
    # print("Percentuale:", percentuale)

    # Crea il grafico a torta
    labels = ['Pazienti con familiari ipertesi', 'Non selezionati']
    sizes = [total_count, total_documents - total_count]
    colors = ['#E52B50', '#607D8B']
    explode = (0.1, 0)

    fig, ax = plt.subplots(facecolor='None')
    fig.set_size_inches(5, 4)
    patches, text, autotext = ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, labeldistance=1.05)
    plt.setp(text, color='white')
    plt.setp(autotext, color='white')
    ax.axis('equal')
    return fig,percentuale,total_count