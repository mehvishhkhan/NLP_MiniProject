import streamlit as st
from together import Together
import os
from dotenv import load_dotenv

load_dotenv()

model_id = "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo"
client = Together(api_key=os.getenv('TOGETHER_KEY'))

def get_paraphrase(text):
    paraphrase_prompt = f"""
    You are a text paraphraser. Your task is to rephrase the input text to improve its clarity and readability while retaining the original meaning. 
    Return only the paraphrased text.
    The following is the text you need to paraphrase:
    {text}
    """
    response = client.chat.completions.create(
        model=model_id,
        messages=[{"role": "user", "content": paraphrase_prompt}],
        max_tokens=512,
        temperature=0.3,
        top_p=0.95,
        top_k=50,
        repetition_penalty=1,
        stop=["<|eot_id|>", "<|eom_id|>"],
    )
    return response.choices[0].message.content.strip()
