import os
import streamlit as st
from together import Together
from dotenv import load_dotenv
from googletrans import Translator
from gtts import gTTS
import tempfile

# Load environment variables
load_dotenv()

# Set the API key for Together
api_key = os.getenv('TOGETHER_KEY')
client = Together(api_key=api_key)

# Translator for language conversion
translator = Translator()
languages = {
    'English': 'en',
    'Hindi': 'hi',
    'Marathi': 'mr',
    'Kannada': 'kn',
    'Urdu': 'ur', 
    'Gujarati': 'gu',
    'Spanish': 'es',
    'French': 'fr',
    'German': 'de',
    'Italian': 'it',
}

def synthesize_speech(content, language):
    speech = gTTS(text=content, lang=language, slow=False)
    
    # Use a temporary file that persists until manually deleted
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as audio_file:
        speech.save(audio_file.name)
        return audio_file.name

def get_paraphrase(input_text):
    paraphrase_prompt = f"Paraphrase the following sentence and directly provide the paraphrased sentence, dont add anything else : {input_text}"
    
    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
            messages=[{"role": "user", "content": paraphrase_prompt}],
            max_tokens=50,
            temperature=0.5,  # Adjust as necessary
        )
        paraphrased_text = response.choices[0].message.content.strip()
        return paraphrased_text
    except Exception as e:
        print(f"Error: {e}")
        return "Error occurred while paraphrasing."

def main():
    st.set_page_config(page_title='Text Processing App', 
                       initial_sidebar_state='collapsed', 
                       layout='wide',
                       page_icon='🔄')
    st.title('Text Processing App')
    
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

            # Automatically generate audio for the paraphrased text
            audio_file_path = synthesize_speech(paraphrased_text, 'en')
            st.audio(audio_file_path)

    elif option == 'Translate':
        input_text = st.text_area("Enter the text to translate:", height=200)
        language = st.selectbox('Select language for translation:', list(languages.keys()))
        selected_language = languages[language]

        if st.button('Translate'):
            if not input_text.strip():
                st.error('Please enter some text.')
                return

            translated_text = translator.translate(input_text, src='en', dest=selected_language).text
            st.subheader('Translated Text')
            st.write(translated_text)

            # Automatically generate audio for the translated text
            audio_file_path = synthesize_speech(translated_text, selected_language)
            st.audio(audio_file_path)

if __name__ == '__main__':
    main()