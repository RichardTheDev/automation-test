from PIL import Image
import PyPDF2
import asyncio
import aiohttp
import streamlit as st
from PyPDF2 import PdfReader
import io
import pandas as pd
import json

# Replace with your actual OpenAI API key
api_key = st.secrets["openaikey"]

async def process_text(text, prompt):
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                'model': 'gpt-3.5-turbo',
                "temperature": 0,
                'messages': [
                    {'role': 'system', 'content': prompt},
                    {'role': 'user', 'content': text}
                ],
            }

            headers = {'Authorization': f'Bearer {api_key}'}
            async with session.post('https://api.openai.com/v1/chat/completions', json=payload, headers=headers) as response:
                response_data = await response.json()
                return response_data
    except Exception as error:
        print("Error processing chat:", error)
        return None

def extract_text_from_pdf(uploaded_pdf):
    pdf_reader = PdfReader(io.BytesIO(uploaded_pdf.read()))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def display_data():
    st.title("Scann PDF Demo - Laziz tech & AUDITEX")

    # Prompts selection
    prompt_options = {
        "Factures": "Vous êtes un assistant qui va extraire des textes qu ont vous fournie qui sont des textes extraies de pdf , les infofrmatiosn suivantes: la date, le numero de fatcure,l'objet de la prestation,le Libelle(le libelle doit etre ecris exactment comme sur le pdf), le total HT et le siren.Montre moi le resultat sous forme de json.montre que le json",
        "CV": "Vous êtes un assistant qui va extraire des textes qu ont vous fournie qui sont des textes extraies de pdf qui represente un CV , les informations suivantes uniquement: 1- Le plus haut diplome (Ex master ou bsc), 2 - le nom de l'ecole 3 - l'annee dobtention  .Montre moi le resultat sous forme de json uniquement sinon ca va pas marcher",
        "Bulletin": "Vous êtes un assistant qui va extraire des textes qu ont vous fournie qui sont des textes extraies de pdf qui represente un BUlletin de paie , les informations suivantes uniquement: 1- Nom prenom, 2- Emploie ,3- Cadre ,4- Salaire Brut .Montre moi le resultat sous forme de json uniquement sinon ca va pas marcher",
    }

    selected_option = st.selectbox("Select the pdf option:", list(prompt_options.keys()))
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])

    if st.button("Process PDF"):
        if uploaded_pdf:
            pdf_text = extract_text_from_pdf(uploaded_pdf)
            selected_prompt = prompt_options[selected_option]
            response_data = asyncio.run(process_text(pdf_text, selected_prompt))
            print(response_data)

            if response_data:
                # Extracting the content from the response
                data = response_data['choices'][0]['message']['content']

                try:
                    # Try to parse the data string as JSON
                    json_data = json.loads(data)

                    # Check if json_data is a dictionary and convert it to a DataFrame
                    if isinstance(json_data, dict):
                        df = pd.DataFrame([json_data])  # Create a DataFrame from a single dictionary
                    elif isinstance(json_data, list) and all(isinstance(item, dict) for item in json_data):
                        df = pd.DataFrame(json_data)  # Create a DataFrame from a list of dictionaries
                    else:
                        st.error("The returned data is not in a valid JSON format for DataFrame conversion.")
                        return  # Exit the function

                    # Display and export the DataFrame
                    st.dataframe(df)
                    st.download_button(label="Export to Excel",
                                       data=df.to_csv(index=False).encode('utf-8'),
                                       file_name='data.csv',
                                       mime='text/csv')

                except json.JSONDecodeError:
                    # Handle the exception if the data is not valid JSON
                    st.error("Failed to parse the text as JSON.")
            else:
                st.error("Failed to process the text.")

        else:
            st.warning("Please upload a PDF file.")

if __name__ == '__main__':
    display_data()
