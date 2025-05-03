import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
from ai_model import get_document_answer
import tempfile

# Streamlit Wide Mode
st.set_page_config(layout="wide", page_title="Document QA Assistant")

# Session State Initialization
if "history" not in st.session_state:
    st.session_state.history = []

# Two-Column Layout: Chat (25%) | PDF (75%)
col_chat, col_pdf = st.columns([1, 3], gap="medium")

with col_chat:
    st.subheader("💬 Chat with Doc Assist")

    chat_box = st.container(height=700, border=True)
    with chat_box:
        for role, msg in st.session_state.history:
            with st.chat_message(role):
                st.write(msg)

    if prompt := st.chat_input("Ask a question…"):
        st.session_state.history.append(("user", prompt))
        with st.chat_message("user"):
            st.write(prompt)

        pdf_path = st.session_state.get("pdf_path")
        if pdf_path:
            answer = get_document_answer(pdf_path, prompt)
        else:
            answer = "Please upload a PDF to get started."

        st.session_state.history.append(("assistant", answer))
        with st.chat_message("assistant"):
            st.write(answer)

# PDF Viewer & Upload
with col_pdf:
    st.subheader("📄 Document Viewer")

    def clear_pdf():
        """Remove the PDF path from session state."""
        st.session_state.pop("pdf_path", None)

    pdf_path = st.session_state.get("pdf_path")

    if pdf_path:
        st.button("🗑 Clear PDF", on_click=clear_pdf)
        st.markdown(
            "<div style='margin:0 auto; max-width:90%; padding-top:10px;'>",
            unsafe_allow_html=True,
        )
        pdf_viewer(input=pdf_path, width="100%", height=800)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        uploaded = st.file_uploader(
            "Drag & drop your PDF here",
            type="pdf",
            label_visibility="visible"
        )
        if uploaded:
            # Persist the uploaded PDF as a temp file and store its path
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded.read())
                st.session_state.pdf_path = tmp.name