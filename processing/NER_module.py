import string
import re
from nltk.tokenize import word_tokenize

def merge_tokens(ner):
    merged_ner = []
    prev_word = None
    prev_end = None

    for entity in ner:
        if prev_word and entity['word'][:2] == "##":
            prev_word += entity['word'][2:]
            prev_end = entity['end']
        elif prev_word and entity['entity_group'][0] == 'I':
            prev_word += ' ' + entity['word']
            prev_end = entity['end']
        else:
            if prev_word:
                merged_ner.append({
                    'entity_group': entity['entity_group'],
                    'score': entity['score'],
                    'word': prev_word,
                    'start': entity['start'] - len(prev_word) + 1,
                    'end': prev_end
                })
            prev_word = entity['word']
            prev_end = entity['end']

    if prev_word:
        merged_ner.append({
            'entity_group': ner[-1]['entity_group'],
            'score': ner[-1]['score'],
            'word': prev_word,
            'start': ner[-1]['start'],
            'end': prev_end
        })

    return merged_ner

def preprocess_text(text):
    # print("TEXT: ", text)
    
    # Clean and normalize the text if needed
    text = text.lower()
    
    # nltk_stopwords = set(stopwords.words("italian"))

    # Remove punctuation
    text = text.translate(str.maketrans("", "", string.punctuation))

    # Tokenize the text
    tokens = word_tokenize(text, language='italian')

    # Remove stopwords
    # tokens = [token for token in tokens if token not in nltk_stopwords]

    # Remove numbers and short tokens
    pattern = re.compile(r"\d+")
    tokens = [pattern.sub("", token) for token in tokens]
    
    # Remove extra whitespaces
    tokens = [token.strip() for token in tokens]
    
    # Join tokens back to text with normalized whitespace
    preprocessed_text = " ".join(tokens)
    
    return preprocessed_text

def perform_ner(pipeline, text):
    ner = pipeline(text)
    
    return ner

def perform_ac(pipeline, ner_prediction, text):
    print("TEXT: ", text)
    for entity in ner_prediction:
        txt = text[:entity['end']] + ' </e>' + text[entity['end']:]
        txt = txt[:entity['start']] + '<e> ' + txt[entity['start']:]
        ac_prediction = pipeline(txt)
        if len(ac_prediction) > 0:
            assertion = ac_prediction[0]['label']
            entity['assertion'] = assertion