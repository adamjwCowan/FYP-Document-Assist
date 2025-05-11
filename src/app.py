import streamlit as st
import tempfile
import os
import contextlib
import io
from pdf2image import convert_from_path
from ai_model import get_document_answer_with_highlight, standardize_images
from streamlit_float import float_init, float_css_helper
from PIL import Image  # ensure PIL is in requirements

# 1) Page config & float init
st.set_page_config(layout="wide", page_title="Document QA Assistant")
float_init()

# 2) Session state initialization
if "history" not in st.session_state:
    st.session_state.history = []
if "page_index" not in st.session_state:
    st.session_state.page_index = 0
if "display_pages" not in st.session_state:
    st.session_state.display_pages = []
if "std_pages" not in st.session_state:
    st.session_state.std_pages = []
if "highlighted_pages" not in st.session_state:
    st.session_state.highlighted_pages = []

MAX_FILE_SIZE_MB = 10

def is_file_size_valid(uploaded_file) -> bool:
    uploaded_file.seek(0, os.SEEK_END)
    size = uploaded_file.tell()
    uploaded_file.seek(0)
    return size <= MAX_FILE_SIZE_MB * 1024 * 1024

def is_pdf_file(uploaded_file) -> bool:
    return uploaded_file.name.lower().endswith(".pdf")

def safe_convert(pdf_path: str, dpi: int):
    """Convert PDF pages to PIL images without printing logs."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        pages = convert_from_path(pdf_path, dpi=dpi)
    return pages

# 3) Two-column layout: chat | PDF uploader & display
col_chat, col_pdf = st.columns([1, 2], gap="medium")

with col_pdf:
    # only on initial load / after clear
    if not st.session_state.display_pages:
        uploaded = st.file_uploader("Drag & drop your PDF here", type="pdf")
        if uploaded:
            if not is_file_size_valid(uploaded):
                st.error(f"File exceeds {MAX_FILE_SIZE_MB} MB")
            elif not is_pdf_file(uploaded):
                st.error("Please upload a valid PDF")
            else:
                # save tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded.read())
                    path = tmp.name
                st.session_state.pdf_path = path

                # preload original pages
                st.session_state.display_pages = safe_convert(path, dpi=200)
                # preload standardized pages for model
                raw_pages = safe_convert(path, dpi=300)
                st.session_state.std_pages = standardize_images(raw_pages)

                # reset
                st.session_state.page_index = 0
                st.session_state.history = []
                st.session_state.highlighted_pages = []

# 4) Chat callback
def chat_content():
    user_q = st.session_state.content
    st.session_state.history.append(("user", user_q))

    if not st.session_state.std_pages:
        st.session_state.history.append(("assistant", "Please upload a PDF first."))
        return

    answer, highlights, _ = get_document_answer_with_highlight(
        pdf_path=st.session_state.pdf_path,
        question=user_q,
        std_pages=st.session_state.std_pages,
        orig_pages=st.session_state.display_pages,
        force_code=st.session_state.get("force_code", False),
        simplify_layman=st.session_state.get("simplify_layman", True)
    )

    st.session_state.history.append(("assistant", answer))
    st.session_state.highlighted_pages = highlights

# 5) Chat column
with col_chat:
    st.subheader("💬 Chat with Doc Assist")
    with st.container(height=600, border=True):
        for role, msg in st.session_state.history:
            with st.chat_message(role):
                st.write(msg)

    st.chat_input(key="content", on_submit=chat_content)
    st.checkbox("🔀 Explain in Layman Terms",
                key="simplify_layman", value=True,
                help="Rephrase into simpler language.")
    st.checkbox("🔀 Force Code Summarisation",
                key="force_code", value=False,
                help="Summarise as code when relevant.")

    css_chat = float_css_helper(
        top="4rem", left="1rem", width="32%",
        height="calc(100vh - 4rem)",
        custom_css="z-index:9999; pointer-events:auto;"
    )
    col_chat.float(css=css_chat)

# 6) PDF display + navigation
with col_pdf:
    pages = st.session_state.display_pages
    idx = st.session_state.page_index

    if pages:
        prev_c, clear_c, next_c = st.columns([1,1,1], gap="small")
        with prev_c:
            if st.button("← Previous") and idx >= 2:
                st.session_state.page_index -= 2
        with clear_c:
            if st.button("🗑 Clear PDF"):
                for k in ("pdf_path","display_pages","std_pages","highlighted_pages","page_index","history"):
                    st.session_state.pop(k, None)
        with next_c:
            if st.button("Next →") and idx+2 < len(pages):
                st.session_state.page_index += 2

        left, right = st.columns([1,1], gap="small")
        with left:
            st.image(pages[idx], use_container_width=True)
        with right:
            if idx+1 < len(pages):
                st.image(pages[idx+1], use_container_width=True)

    css_pdf = float_css_helper(
        top="4rem", left="35%", width="62%",
        height="calc(100vh - 4rem)",
        custom_css="z-index:1;"
    )
    col_pdf.float(css=css_pdf)