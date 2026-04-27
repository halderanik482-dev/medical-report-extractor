import streamlit as st
import pdfplumber
import re

st.title("Medical Report Extractor 🏥")
st.write("Upload a Healthians PDF report to extract key values.")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    with pdfplumber.open(uploaded_file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"

    # Regex patterns to find the specific values
    hb_pattern = r"Haemoglobin \(HB\).*?(\d+\.\d+)"
    b12_pattern = r"VITAMIN B12.*?(\d+)\s*pg/mL"
    vitd_pattern = r"VITAMIN D \(25 - OH VITAMIN D\).*?(\d+\.\d+)"

    hb_match = re.search(hb_pattern, text, re.IGNORECASE)
    b12_match = re.search(b12_pattern, text, re.IGNORECASE)
    vitd_match = re.search(vitd_pattern, text, re.IGNORECASE)

    st.subheader("Extracted Values:")
    
    if hb_match:
        st.success(f"**Haemoglobin (HB):** {hb_match.group(1)} g/dL")
    else:
        st.warning("Haemoglobin (HB) not found.")

    if b12_match:
        st.success(f"**Vitamin B12:** {b12_match.group(1)} pg/mL")
    else:
        st.warning("Vitamin B12 not found.")

    if vitd_match:
        st.success(f"**Vitamin D:** {vitd_match.group(1)} ng/ml")
    else:
        st.warning("Vitamin D not found.")
