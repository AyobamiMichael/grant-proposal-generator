"""
app.py
Hugging Face Spaces entry point for Multi-Agent Grant Proposal Generator
"""

import os
import gradio as gr

# Set HF-specific environment
os.environ['HF_HOME'] = '/tmp/huggingface'
os.environ['TRANSFORMERS_CACHE'] = '/tmp/transformers'

# Import your app
from app_gradio import GradioApp

def main():
    """Launch Gradio app for Hugging Face Spaces"""
    
    print("="*70)
    print("🚀 Starting Grant Proposal Generator on Hugging Face Spaces")
    print("="*70)
    print()
    
    # Check for API key
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("⚠️  WARNING: GROQ_API_KEY not set!")
        print("   Please add it in Space settings → Repository secrets")
        print("   Name: GROQ_API_KEY")
        print("   Value: Your Groq API key from https://console.groq.com/keys")
        print()
    else:
        print("✅ GROQ_API_KEY found")
        print()
    
    # Create and launch app
    try:
        app_instance = GradioApp()
        app = app_instance.create_interface()
        
        # Launch with HF-specific settings
        app.launch(
            server_name="0.0.0.0",  # Required for HF Spaces
            server_port=7860,
            share=False,  # Don't need share link on HF
            show_error=True,
            show_api=False
        )
        
    except Exception as e:
        print(f"❌ Error launching app: {e}")
        import traceback
        traceback.print_exc()
        
        # Show error in Gradio UI
        error_app = gr.Interface(
            fn=lambda: f"❌ Error: {str(e)}\n\nPlease check logs and ensure GROQ_API_KEY is set.",
            inputs=None,
            outputs=gr.Textbox(label="Error"),
            title="🚨 Launch Error"
        )
        error_app.launch(server_name="0.0.0.0", server_port=7860)


if __name__ == "__main__":
    main()