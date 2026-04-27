import streamlit as st
import pdfplumber
import google.generativeai as genai
import json

st.title("AI Medical Report Extractor 🏥")
st.write("Upload ANY lab report. The AI will find the values, regardless of the format!")

# Securely load the API key from Streamlit's secrets
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except KeyError:
    st.error("API Key not found. Please add it to the Streamlit Secrets.")
    st.stop()

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    with st.spinner("AI is reading the report..."):
        # 1. Extract the messy text from the PDF
        with pdfplumber.open(uploaded_file) as pdf:
            text = ""
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        
        # 2. Tell the AI exactly what to find and how to format it
        prompt = f"""
        You are an expert medical data extractor. Look at the messy medical report text below. 
        Extract ONLY the following three values: Haemoglobin, Vitamin B12, and Vitamin D.
        Return ONLY a raw JSON object with the keys "Haemoglobin", "Vitamin_B12", and "Vitamin_D".
        Include the units in the value (e.g., "11.9 g/dL").
        If a value is missing, output "Not Found". Do not include any markdown formatting.
        
        Text:
        {text}
        """
        
        # 3. Ask the AI and display the results
        try:
            response = model.generate_content(prompt)
            
            # Clean up the AI's response to ensure it's pure JSON
            result_text = response.text.strip().removeprefix('```json').removesuffix('```').strip()
            data = json.loads(result_text)
            
            st.subheader("Extracted Values:")
            st.success(f"**Haemoglobin (HB):** {data.get('Haemoglobin', 'Not Found')}")
            st.success(f"**Vitamin B12:** {data.get('Vitamin_B12', 'Not Found')}")
            st.success(f"**Vitamin D:** {data.get('Vitamin_D', 'Not Found')}")
            
        except Exception as e:
            st.error(f"An error occurred while processing the data: {e}")
