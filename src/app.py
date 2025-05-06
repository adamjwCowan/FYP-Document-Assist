import streamlit as st
import tempfile
from pdf2image import convert_from_path
from streamlit_float import float_init, float_css_helper
from ai_model import get_document_answer
from streamlit_pdf_viewer import pdf_viewer # redundancy if necessary

# 1) Page config & float init
st.set_page_config(layout="wide", page_title="Document QA Assistant")
float_init()

# 2) Chat state & callback
if "history" not in st.session_state:
    st.session_state.history = []

def chat_content():
    user_msg = st.session_state.content
    st.session_state.history.append(("user", user_msg))
    pdf_path = st.session_state.get("pdf_path")
    answer = get_document_answer(pdf_path, user_msg) if pdf_path else "Upload a PDF first."
    st.session_state.history.append(("assistant", answer))

# 3) Create two columns
col_chat, col_pdf = st.columns([1, 2], gap="medium")

# 4) Chat column
with col_chat:
    st.subheader("💬 Chat with Doc Assist")

    # Scrollable history box
    with st.container(height=600, border=True):
        for role, msg in st.session_state.history:
            with st.chat_message(role):
                st.write(msg)

    # Floating input at bottom of chat column
    input_ctr = st.container()
    with input_ctr:
        st.chat_input(key="content", on_submit=chat_content)

# Float chat column

css = float_css_helper(
    top="4rem",          # leave room for any Streamlit header(s)
    left="1rem",         # small margin from the left
    width="32%",         # roughly 1 / (1+2) of the page width
    height="calc(100vh - 4rem)",  # full viewport height minus header
    custom_css="""z-index: 9999;
    pointer-events: auto;
    """
)
col_chat.float(css=css)

col_chat, col_pdf = st.columns([1, 2], gap="medium")
with col_pdf:


    # Only show uploader when no PDF is loaded
    if "pdf_pages" not in st.session_state:
        uploaded = st.file_uploader(
            "Drag & drop your Document (PDF) here",
            type="pdf",
            key="pdf_uploader"     # <<< unique key here
        )
        if uploaded:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded.read())
                st.session_state.pdf_path = tmp.name
            st.session_state.pdf_pages = convert_from_path(
                st.session_state.pdf_path
            )
            st.session_state.page_index = 0

    pages = st.session_state.get("pdf_pages", [])
    if pages:
        idx = st.session_state.page_index

        # Navigation layout with Clear PDF in the middle
        prev_col, clear_col, next_col = st.columns([1, 1, 1], gap="small")

        with prev_col:
            if st.button("← Previous") and idx >= 2:
                st.session_state.page_index -= 2

        with clear_col:
            if st.button("🗑 Clear PDF"):
                for k in ("pdf_path", "pdf_pages", "page_index"):
                    st.session_state.pop(k, None)
                st.rerun()

        with next_col:
            if st.button("Next →") and idx + 2 < len(pages):
                st.session_state.page_index += 2

        # Display two pages side by side
        p1 = pages[idx]
        p2 = pages[idx + 1] if idx + 1 < len(pages) else None

        left, right = st.columns([1, 1], gap="small")
        with left:
            st.image(p1, use_container_width=True)
        with right:
            if p2:
                st.image(p2, use_container_width=True)
            else:
                st.write("")  # empty if odd page

# ─── Float both columns so they stay fixed below header ────────────────────
css_chat = float_css_helper(
    top="2rem",
    left="1rem",
    width="32%",
    height="calc(100vh - 4rem)",
    z_index="2" #Chat column floats on top of pdf rendering
)
col_chat.float(css=css_chat)

css_pdf = float_css_helper(
    top="4rem",
    left="35%",
    width="62%",
    height="calc(100vh - 4rem)",
    z_index="1"
)
col_pdf.float(css=css_pdf)