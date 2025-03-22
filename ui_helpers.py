import streamlit as st
import os

def load_custom_css():
    """Load custom CSS to apply Lato font and color scheme across all pages"""
    css_path = os.path.join('.streamlit', 'style.css')
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    # Add custom classes for message styling
    st.markdown("""
    <style>
    /* These helper classes can be used in st.markdown for custom styling */
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 6px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    
    .error-box {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 6px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    
    .info-box {
        background-color: #cce5ff;
        color: #004085;
        padding: 1rem;
        border-radius: 6px;
        border-left: 4px solid #0d6efd;
        margin: 1rem 0;
    }
    
    .warning-box {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 6px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    
    .highlight-text {
        color: #d13c35;
        font-weight: 700;
    }
    
    .section-divider {
        border-top: 2px solid #f2bc54;
        margin: 2rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

def success_message(text):
    """Display a success message with custom styling"""
    st.markdown(f'<div class="success-box">{text}</div>', unsafe_allow_html=True)

def error_message(text):
    """Display an error message with custom styling"""
    st.markdown(f'<div class="error-box">{text}</div>', unsafe_allow_html=True)

def info_message(text):
    """Display an info message with custom styling"""
    st.markdown(f'<div class="info-box">{text}</div>', unsafe_allow_html=True)

def warning_message(text):
    """Display a warning message with custom styling"""
    st.markdown(f'<div class="warning-box">{text}</div>', unsafe_allow_html=True)

def section_divider():
    """Add a horizontal divider between sections"""
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)