import os
import streamlit as st
import spacy
from dotenv import load_dotenv
from paraphraser import get_paraphrase  # Import the paraphrasing function from paraphraser.py

# Load environment variables
load_dotenv()

# Translator for language conversion
translator = Translator()
languages = {
    'English': 'en',
    'Hindi': 'hi',
    'Gujarati': 'gu',
    'Kannada': 'kn',
    'Urdu': 'ur', 
    'Sindhi': 'sd',
    'Marathi': 'mr',
    'Spanish': 'es',
    'French': 'fr',
    'German': 'de',
    'Italian': 'it',
}

def main():
    st.set_page_config(page_title='Text Paraphraser', 
                       initial_sidebar_state='collapsed', 
                       layout='wide',
                       page_icon='🔄')
    st.title('Text Paraphraser')
    
    option = st.radio("What do you wish to do?", ('Translate', 'Paraphrase'))

    if option == 'Paraphrase':
        input_text = st.text_area('Enter text to paraphrase', height=200)
        if st.button('Paraphrase'):
            if not input_text.strip():
                st.error('Please enter some text.')
                return

            with st.spinner('Paraphrasing...'):
                paraphrased_text = get_paraphrase(input_text)
                st.session_state.paraphrased_text = paraphrased_text

            st.subheader('Paraphrased Text')
            st.write(paraphrased_text)

            if st.button("🔊 Generate Audio"):
                audio_file_path = synthesize_speech(paraphrased_text, 'en')
                st.audio(audio_file_path)

    elif option == 'Translate':
        text_input = st.text_area("Enter the text to translate:")
        language = st.selectbox('Select language for translation:', list(languages.keys()))
        selected_language = languages[language]
        
        if st.button('Translate'):
            if text_input.strip() == "":
                st.error('Please enter some text.')
                return

            translated_text = translator.translate(text_input, src='en', dest=selected_language).text
            st.subheader('Translated Text')
            st.write(translated_text)

            # Read aloud the translated text
            audio_file_path = synthesize_speech(translated_text, selected_language)
            st.audio(audio_file_path)

if __name__ == '__main__':
    main()
