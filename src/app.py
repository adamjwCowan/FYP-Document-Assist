import streamlit as st
import tempfile
import os
from pdf2image import convert_from_path
from ai_model import get_document_answer_with_highlight
from streamlit_pdf_viewer import pdf_viewer
from streamlit_float import float_init, float_css_helper

# 1) Page config & float init
st.set_page_config(layout="wide", page_title="Document QA Assistant")
float_init()

# 2) Session state & callback
if "history" not in st.session_state:
    st.session_state.history = []
if "page_index" not in st.session_state:
    st.session_state.page_index = 0

MAX_FILE_SIZE_MB = 10  # Maximum file size in megabytes

def is_file_size_valid(uploaded_file) -> bool:
    uploaded_file.seek(0, os.SEEK_END)
    size = uploaded_file.tell()
    uploaded_file.seek(0)
    return size <= MAX_FILE_SIZE_MB * 1024 * 1024

def is_pdf_file(uploaded_file) -> bool:
    return uploaded_file.name.lower().endswith('.pdf')

def chat_content():
    user_q = st.session_state.content
    st.session_state.history.append(("user", user_q))
    pdf = st.session_state.get("pdf_path")
    if not pdf:
        st.session_state.history.append(("assistant", "Please upload a PDF first."))
        return

    with st.spinner("Thinking…"):
        answer, pages = get_document_answer_with_highlight(
            pdf,
            user_q,
            force_code=st.session_state.get("force_code", False),
            simplify_layman=st.session_state.get("simplify_layman", True)
        )

    st.session_state.history.append(("assistant", answer))
    st.session_state.highlighted_pages = pages

# 3) Two-column layout: chat | PDF
col_chat, col_pdf = st.columns([1, 2], gap="medium")

# 4) Chat column
with col_chat:
    st.subheader("💬 Chat with Doc Assist")

    # History box
    with st.container(height=600, border=True):
        for r, m in st.session_state.history:
            with st.chat_message(r):
                st.write(m)

    # Chat input
    inp_ctr = st.container()
    with inp_ctr:
        st.chat_input(key="content", on_submit=chat_content)

    # Toggle to allow user to turn on/off layman simplification
    st.checkbox(
        "🔀 Explain in Layman Terms",
        key="simplify_layman",
        value=True,
        help="When checked, answers will be rephrased into simpler, non-technical language."
    )

    st.checkbox(
        "🔀 Force Code Summarisation",
        key="force_code",
        value=True,
        help="When checked, answers will be interpreted as code snippets/examples with a summarisation of said code's function."
    )

# Float chat column
css_chat = float_css_helper(
    top="4rem", left="1rem", width="32%",
    height="calc(100vh - 4rem)",
    custom_css="z-index:9999; pointer-events:auto;"
)
col_chat.float(css=css_chat)

# 5) PDF column
with col_pdf:
    # File uploader / Clear PDF
    if "highlighted_pages" not in st.session_state:
        uploaded = st.file_uploader("Drag & drop your PDF here", type="pdf", key="pdf_uploader")
        if uploaded:
            if not is_file_size_valid(uploaded):
                st.error(f"File size exceeds {MAX_FILE_SIZE_MB} MB limit.")
            elif not is_pdf_file(uploaded):
                st.error("Invalid file type. Please upload a PDF file.")
            else:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded.read())
                    tmp_path = tmp.name
                st.session_state.pdf_path = tmp_path
                # Preload pages
                st.session_state.highlighted_pages = convert_from_path(st.session_state.pdf_path, dpi=200)
                st.session_state.page_index = 0

    pages = st.session_state.get("highlighted_pages", [])
    if pages:
        idx = st.session_state.page_index

        prev_c, clear_c, next_c = st.columns([1,1,1], gap="small")
        with prev_c:
            if st.button("← Previous") and idx >= 2:
                st.session_state.page_index -= 2
        with clear_c:
            if st.button("🗑 Clear PDF"):
                for k in ("pdf_path","highlighted_pages","page_index"):
                    st.session_state.pop(k, None)
        with next_c:
            if st.button("Next →") and idx+2 < len(pages):
                st.session_state.page_index += 2

        # Two-page view
        left, right = st.columns([1,1], gap="small")
        with left:
            st.image(pages[idx], use_container_width=True)
        with right:
            if idx+1 < len(pages):
                st.image(pages[idx+1], use_container_width=True)

# Float PDF column
css_pdf = float_css_helper(
    top="4rem", left="35%", width="62%",
    height="calc(100vh - 4rem)",
    custom_css="z-index:1;"
)
col_pdf.float(css=css_pdf)