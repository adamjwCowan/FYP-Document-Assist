import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
from ai_model import get_document_answer
import tempfile

# 1) Enable wide mode up front
st.set_page_config(layout="wide", page_title="Document QA Assistant")

# 2) Init chat history
if "history" not in st.session_state:
    st.session_state.history = []

# 4) Two-column layout: chat (25%) | PDF (75%)
col_chat, col_pdf = st.columns([1, 3], gap="medium")

# Chat Interface
with col_chat:
    st.subheader("💬 Chat with Doc Assist")
    chat_box = st.container(height=700, border=True)
    with chat_box:
        for role, msg in st.session_state.history:
            st.chat_message(role)(msg)

    if user_input := st.chat_input("Ask a question…"):
        st.session_state.history.append(("user", user_input))
        pdf_path = st.session_state.get("pdf_path")
        answer = get_document_answer(pdf_path, user_input) if pdf_path else "Please upload a PDF to get started."
        st.session_state.history.append(("assistant", answer))
        with chat_box:
            st.chat_message("assistant")(answer)

# PDF Viewer
with col_pdf:
    # Attempt to get the saved PDF path
    pdf_path = st.session_state.get("pdf_path")

    def clear_pdf():
        """Callback to remove PDF from session state."""
        if "pdf_path" in st.session_state:
            del st.session_state["pdf_path"]  # Delete the key to clear the viewer :contentReference[oaicite:1]{index=1}

    pdf_path = st.session_state.get("pdf_path")

    if pdf_path:
        # Show the Clear button
        st.button("🗑 Clear PDF", on_click=clear_pdf)  # Use on_click callback :contentReference[oaicite:2]{index=2}

        # Render the PDF centered via CSS
        st.markdown(
            """
            <div style="margin: 0 auto; max-width: 90%; padding-top: 10px;">
            """,
            unsafe_allow_html=True
        )
        pdf_viewer(input=pdf_path, width="100%", height=800)
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        # When no PDF, show uploader in exactly the same spot
        uploaded = st.file_uploader(
            label="Drag & drop your PDF here",
            type="pdf",
            label_visibility="visible"
        )
        if uploaded:
            # Save to a temp file and store path in session state
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded.read())
                st.session_state.pdf_path = tmp.name