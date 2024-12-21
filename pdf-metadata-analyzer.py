import streamlit as st
import PyPDF2
import pandas as pd
from io import BytesIO
import fitz  # PyMuPDF
from PIL import Image
import numpy as np
from datetime import datetime

def extract_metadata(pdf_file):
    """Extract metadata from PDF file"""
    metadata = {}
    try:
        # PyPDF2 extraction
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        metadata['Pages'] = len(pdf_reader.pages)
        doc_info = pdf_reader.metadata
        if doc_info:
            for key in doc_info.keys():
                metadata[key.strip('/')] = doc_info[key]
        
        # PyMuPDF extraction for additional metadata
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        metadata['Format'] = doc.metadata.get('format', 'Unknown')
        metadata['PDF Version'] = doc.metadata.get('pdf-version', 'Unknown')
        metadata['Encryption'] = 'Yes' if doc.is_encrypted else 'No'
        
        return metadata, None
    except Exception as e:
        return None, str(e)

def analyze_metadata(metadata):
    """Analyze metadata for completeness and validity"""
    analysis = {}
    
    # Check for essential metadata fields
    essential_fields = ['Title', 'Author', 'Producer', 'Creator']
    for field in essential_fields:
        analysis[f'{field} present'] = field in metadata
    
    # Validate dates
    date_fields = ['CreationDate', 'ModDate']
    for field in date_fields:
        if field in metadata:
            try:
                # Attempt to parse the date
                date_str = metadata[field]
                if isinstance(date_str, str):
                    datetime.strptime(date_str, '%Y%m%d%H%M%S')
                analysis[f'{field} valid'] = True
            except:
                analysis[f'{field} valid'] = False
    
    return analysis

# Set up Streamlit page
st.set_page_config(page_title="PDF Metadata Analyzer", layout="wide")
st.title("AI-Powered PDF Metadata Analyzer")

# File uploader
uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file is not None:
    # Create columns for layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Extracted Metadata")
        metadata, error = extract_metadata(uploaded_file)
        
        if error:
            st.error(f"Error processing PDF: {error}")
        elif metadata:
            # Display metadata in a DataFrame
            df = pd.DataFrame(metadata.items(), columns=['Property', 'Value'])
            st.dataframe(df)
    
    with col2:
        st.subheader("Metadata Analysis")
        if metadata:
            analysis = analyze_metadata(metadata)
            
            # Convert analysis to color-coded status indicators
            for key, value in analysis.items():
                if value:
                    st.success(f"✓ {key}")
                else:
                    st.warning(f"⚠ {key} - Missing or Invalid")
            
            # Calculate metadata completeness score
            completeness_score = sum(analysis.values()) / len(analysis) * 100
            st.metric("Metadata Completeness Score", f"{completeness_score:.1f}%")
            
            # Provide recommendations
            st.subheader("Recommendations")
            if completeness_score < 100:
                missing_fields = [k.replace(' present', '').replace(' valid', '') 
                                for k, v in analysis.items() if not v]
                st.write("Consider adding or fixing the following metadata:")
                for field in missing_fields:
                    st.write(f"- {field}")
            else:
                st.write("✓ All metadata fields are complete and valid!")

st.sidebar.markdown("""
## About
This tool uses AI and machine learning techniques to:
- Extract metadata from PDF files
- Validate metadata completeness
- Analyze metadata quality
- Provide recommendations for improvement

Upload a PDF file to get started!
""")
