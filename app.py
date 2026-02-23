import streamlit as st
import google.generativeai as genai
import re

st.set_page_config(page_title="Burmese AI Translator", page_icon="🇲🇲")
st.title("🇲🇲 Burmese AI Translator")

# Sidebar for config
with st.sidebar:
    api_key = st.text_input("Enter Gemini API Key", type="password")
    tone = st.selectbox("Tone", ["Action/Aggressive", "Formal/Drama", "Casual/Comedy", "Ancient/Wuxia"])
    batch_size = st.slider("Batch Size (Lines)", 10, 50, 30)

uploaded_file = st.file_uploader("Upload English SRT", type="srt")

def translate_batch(batch_text, tone_setting):
    """Sends a block of text to Gemini for contextual translation."""
    prompt = f"""
    You are a professional movie subtitler specializing in Burmese. 
    Translate the following English subtitle lines into {tone_setting} style Burmese.
    
    Rules:
    1. Keep the SRT numbering and timestamps exactly as they are.
    2. Use natural, spoken Burmese (not formal book language).
    3. Ensure pronouns match the {tone_setting} vibe.
    4. Return ONLY the translated SRT content.
    
    Text:
    {batch_text}
    """
    response = model.generate_content(prompt)
    return response.text

if uploaded_file and api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    if st.button("Start Translation"):
        raw_content = uploaded_file.getvalue().decode("utf-8")
        
        # Split by double newlines to keep SRT blocks together
        blocks = raw_content.split('\n\n')
        translated_blocks = []
        
        progress_bar = st.progress(0)
        
        # Process in batches
        for i in range(0, len(blocks), batch_size):
            batch = "\n\n".join(blocks[i:i + batch_size])
            try:
                translated_batch = translate_batch(batch, tone)
                translated_blocks.append(translated_batch)
            except Exception as e:
                st.error(f"Error at block {i}: {e}")
                translated_blocks.append(batch) # Fallback to original
            
            progress_bar.progress(min((i + batch_size) / len(blocks), 1.0))
        
        final_srt = "\n\n".join(translated_blocks)
        st.success("Done!")
        st.download_button("Download SRT", final_srt, file_name="Burmese_Sub.srt")
