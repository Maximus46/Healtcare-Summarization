import streamlit as st
import base64

def imposta_sfondo():
    # Imposta il percorso dell'immagine di sfondo
    background_image_path = r"C:\Users\ricca\Documents\Università\Big Data Engineering\Final_project\Healtcare - Summarization\streamlit\backg1.png"


    with open(background_image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .css-nzvw1x {{
        background-color: #FFFFFF !important;
        background-image: none !important;
    }}
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover
    }}

    </style>
    """,
    unsafe_allow_html=True
    )

def insert_newlines(text):
    n = 2
    new_text = ""
    count = 0
    for char in text:
        if char == ".":
            count += 1
            if count % n == 0:
                new_text += char + "\n\n"
            else:
                new_text += char
        else:
            new_text += char

    return new_text
