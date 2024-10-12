import os
import streamlit as st
from together import Together
from dotenv import load_dotenv
from googletrans import Translator
from gtts import gTTS
import tempfile
from PyPDF2 import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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

def translate_pdf(uploaded_file, selected_language):
    reader = PdfReader(uploaded_file)
    
    # Create a temporary file for the translated PDF
    translated_pdf_path = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    
    # Create a canvas to draw the translated text
    c = canvas.Canvas(translated_pdf_path.name, pagesize=letter)
    width, height = letter
    
    for page in reader.pages:
        text = page.extract_text()
        if text:
            # Translate the extracted text
            translated_text = translator.translate(text, dest=selected_language).text
            
            # Draw the translated text on the canvas
            text_lines = translated_text.split('\n')
            y_position = height - 72  # Start drawing from the top of the page

            for line in text_lines:
                c.drawString(72, y_position, line)
                y_position -= 12  # Move down for the next line
                if y_position < 72:  # Start a new page if we run out of space
                    c.showPage()
                    y_position = height - 72
            
            # End the page after drawing
            c.showPage()

    # Save the translated PDF
    c.save()
    
    return translated_pdf_path.name

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
        translation_type = st.radio("Select translation method:", ('Text', 'PDF'))
        
        language = st.selectbox('Select language for translation:', list(languages.keys()))
        selected_language = languages[language]

        if translation_type == 'Text':
            input_text = st.text_area("Enter the text to translate:", height=200)
            if st.button('Translate'):
                if not input_text.strip():
                    st.error('Please enter some text.')
                    return

                translated_text = translator.translate(input_text, dest=selected_language).text
                st.subheader('Translated Text')
                st.write(translated_text)

                # Automatically generate audio for the translated text
                audio_file_path = synthesize_speech(translated_text, selected_language)
                st.audio(audio_file_path)

        elif translation_type == 'PDF':
            uploaded_file = st.file_uploader("Upload a PDF file to translate", type=["pdf"])
            if st.button('Translate'):
                if uploaded_file is not None:
                    with st.spinner('Translating PDF...'):
                        translated_pdf_path = translate_pdf(uploaded_file, selected_language)
                    
                    # Provide download link for the translated PDF
                    with open(translated_pdf_path, 'rb') as f:
                        st.download_button("Download Translated PDF", f, file_name="translated.pdf", mime='application/pdf')
                else:
                    st.error('Please upload a PDF file.')

if __name__ == '__main__':
    main()
