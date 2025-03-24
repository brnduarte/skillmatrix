import streamlit as st
import os

def load_custom_css():
    """Load custom CSS to apply Lato font and color scheme across all pages"""
    streamlit_dir = '.streamlit'
    css_path = os.path.join(streamlit_dir, 'style.css')
    
    if not os.path.exists(streamlit_dir):
        os.makedirs(streamlit_dir)
        
    if not os.path.exists(css_path):
        with open(css_path, 'w') as f:
            f.write('/* Default Streamlit styles */\n')
            
    with open(css_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)