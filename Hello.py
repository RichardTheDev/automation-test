
import asyncio
import aiohttp
import streamlit as st
from PyPDF2 import PdfReader
import io

# Replace with your actual OpenAI API key
api_key = st.secrets["openaikey"]

async def process_text(text, prompt):
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                'model': 'gpt-3.5-turbo',
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
    st.title("Scann PDF Demo - AUDITEX")

    # Prompts selection
    prompt_options = {
        "Conserto":"Vous êtes un assistant qui va extraire des textes qu ont vous fournie qui sont des textes extraies de pdf , les infofrmatiosn suivantes: la date, le numero de fatcure,l'objet de la prestation,le Libelle, le total HT et le siren.Montre moi le resultat sous forme de json",
        # "Bulletins":"Vous êtes un assistant qui va extraire des textes qu ont vous fournie qui sont des textes extraies de pdf , les infofrmatiosn suivantes: Le salaire Brut Annuel du bulletin de salaire.Montre moi le resultat sous forme de json",
        # "Dotations": "Prompt for option 3"
    }
    selected_option = st.selectbox("Select the prompt option:", list(prompt_options.keys()))

    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])

    if st.button("Process PDF"):
        if uploaded_pdf:
            pdf_text = extract_text_from_pdf(uploaded_pdf)
            selected_prompt = prompt_options[selected_option]
            response_data = asyncio.run(process_text(pdf_text, selected_prompt))
            if response_data:
                st.json(response_data['choices'][0]['message']['content'])
            else:
                st.error("Failed to process the text.")
        else:
            st.warning("Please upload a PDF file.")

if __name__ == '__main__':
    display_data()
