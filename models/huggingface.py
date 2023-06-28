from transformers import AutoModelForTokenClassification, AutoModelForSequenceClassification, MarianMTModel, MarianTokenizer, AutoTokenizer, pipeline as Pipeline
from optimum.bettertransformer import BetterTransformer

def load_model(model_name, model_architecture, num_labels=None, id2label=None, label2id=None):
    if model_architecture == "token_classification":
        model = AutoModelForTokenClassification.from_pretrained(model_name, num_labels=num_labels, id2label=id2label, label2id=label2id)
    elif model_architecture == "sequence_classification":
        model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=num_labels, id2label=id2label, label2id=label2id)
    else:
        raise ValueError("Invalid model architecture specified.")

    model_bt = BetterTransformer.transform(model)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    return model_bt, tokenizer
def load_marian_model(model_name):
    model = MarianMTModel.from_pretrained(model_name)
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    
    return model, tokenizer
    
def load_pipeline(task, model, tokenizer, model_architecture):
    if model_architecture == "token_classification":
        pipeline = Pipeline(task, tokenizer=tokenizer, model=model, aggregation_strategy='first')
    elif model_architecture == "sequence_classification":
        pipeline = Pipeline(task, tokenizer=tokenizer, model=model)
    else:
        raise ValueError("Invalid model architecture specified.")

    return pipeline
