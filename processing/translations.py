from models.huggingface import load_marian_model

# Load the translation model and tokenizer
MODEL_NAME = "Helsinki-NLP/opus-mt-it-en"

model, tokenizer = load_marian_model(MODEL_NAME)

def perform_translation(text):
    # Tokenize the text
    tokenized_input = tokenizer.encode(text, return_tensors="pt")

    # Translate the text
    translated_output = model.generate(tokenized_input, max_length=200, num_beams=5, early_stopping=True)

    # Decode the translated output
    translated_text = tokenizer.decode(translated_output[0], skip_special_tokens=True)

    return translated_text