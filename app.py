import streamlit as st
import pdfplumber
import google.generativeai as genai
import json

st.title("AI Medical Report Extractor 🏥")
st.write("Upload ANY lab report. The AI will find the values, regardless of the format!")

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # STOP GUESSING: Ask Google which models are actually available to your key
    valid_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    if not valid_models:
        st.error("Critical Error: Your API key cannot access any text-generation models.")
        st.stop()
        
    # Automatically pick the best available model
    target_model = valid_models[0] # Default to the first working one
    for m in valid_models:
        if "gemini-1.5-flash" in m:
            target_model = m
            break
            
    model = genai.GenerativeModel(target_model)
    st.info(f"Successfully connected to: {target_model}") # This will show you exactly what it found
    
except KeyError:
    st.error("API Key not found in Streamlit Secrets.")
    st.stop()
except Exception as e:
    st.error(f"API Connection Error: {e}")
    st.stop()

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    with st.spinner("AI is reading the report..."):
        try:
            # 1. Extract text
            with pdfplumber.open(uploaded_file) as pdf:
                text = ""
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
            
            # 2. Setup prompt
            prompt = f"""
            Extract ONLY the following three values: Haemoglobin, Vitamin B12, and Vitamin D.
            Return ONLY a raw JSON object with the keys "Haemoglobin", "Vitamin_B12", and "Vitamin_D".
            Include the units in the value (e.g., "11.9 g/dL").
            If a value is missing, output "Not Found". Do not include any markdown formatting.
            
            Text:
            {text}
            """
            
            # 3. Generate response
            response = model.generate_content(prompt)
            result_text = response.text.strip().removeprefix('```json').removesuffix('```').strip()
            data = json.loads(result_text)
            
            st.subheader("Extracted Values:")
            st.success(f"**Haemoglobin (HB):** {data.get('Haemoglobin', 'Not Found')}")
            st.success(f"**Vitamin B12:** {data.get('Vitamin_B12', 'Not Found')}")
            st.success(f"**Vitamin D:** {data.get('Vitamin_D', 'Not Found')}")
            
        except Exception as e:
            st.error(f"An error occurred during extraction: {e}")
