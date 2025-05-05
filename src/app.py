import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
from ai_model import get_document_answer
import tempfile
from streamlit_float import float_init, float_css_helper

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

# ─── 4) Chat column ─────────────────────────────────────────────────────────
with col_chat:
    st.subheader("💬 Chat with Doc Assist")

    # 4.1) Scrollable history box
    with st.container(height=600, border=True):
        for role, msg in st.session_state.history:
            with st.chat_message(role):
                st.write(msg)

    # 4.2) Floating input at bottom of chat column
    input_ctr = st.container()
    with input_ctr:
        st.chat_input(key="content", on_submit=chat_content)

# 4.3) Float the entire chat column
#    - top: offset below header (adjust as needed)
#    - left: offset from left edge (aligns with col position)
#    - width: match the column’s relative width (here ~33%)
css = float_css_helper(
    top="4rem",          # leave room for any Streamlit header(s)
    left="1rem",         # small margin from the left
    width="32%",         # roughly 1 / (1+2) of the page width
    height="calc(100vh - 4rem)",  # full viewport height minus header
)
col_chat.float(css=css)

# ─── 5) PDF column ──────────────────────────────────────────────────────────
with col_pdf:
    st.subheader("📄 Document Viewer")

    def clear_pdf():
        st.session_state.pop("pdf_path", None)

    pdf_path = st.session_state.get("pdf_path")
    if pdf_path:
        st.button("🗑 Clear PDF", on_click=clear_pdf)
        st.markdown(
            "<div style='margin:0 auto; max-width:100%; padding-top:10px;'>",
            unsafe_allow_html=True,
        )
        pdf_viewer(input=pdf_path, width="100%", height=800)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        uploaded = st.file_uploader("Drag & drop your PDF here", type="pdf")
        if uploaded:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded.read())
                st.session_state.pdf_path = tmp.name

# 7) Float the PDF column to the same vertical offset
css_pdf = float_css_helper(
    top="4rem",
    left="35%",
    width="66%",
    height="calc(100vh - 4rem)"
)
col_pdf.float(css=css_pdf)