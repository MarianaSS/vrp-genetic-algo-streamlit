"""
Entrada do Streamlit. Mantém apenas a função main e delega a UI para ui.streamlit_ui.
Rodar com: streamlit run main.py
"""
from ui.streamlit_ui import render_main_ui

def main():
    render_main_ui()

if __name__ == "__main__":
    main()