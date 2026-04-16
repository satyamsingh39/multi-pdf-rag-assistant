from __future__ import annotations

import html

import streamlit as st

from multipdf_chat.knowledge_base import get_knowledge_signature
from multipdf_chat.qa import ask_question
from multipdf_chat.styles import inject_styles
from multipdf_chat.ui import render_hero, render_latest_result, render_sidebar


def main():
    st.set_page_config(
        page_title="Multi-PDF Research Assistant",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    inject_styles()
    render_sidebar()
    render_hero()

    if "history" not in st.session_state:
        st.session_state.history = []

    left_col, right_col = st.columns([1.5, 1], gap="large")

    with left_col:
        st.markdown(
            """
            <div class="info-card">
                <div class="section-title">Ask a Question</div>
                <p class="section-copy">
                    Enter a question about the uploaded documents. The assistant will search
                    the indexed context and return a grounded answer from the PDF content.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("question_form", clear_on_submit=True):
            user_question = st.text_input(
                "Question",
                key="question_input",
                placeholder="Enter your question about the uploaded PDFs",
                label_visibility="collapsed",
            )
            st.markdown(
                '<div class="question-helper">Example: Summarize the placement guidelines, explain the debarring policy, or tell me what is written on page 3.</div>',
                unsafe_allow_html=True,
            )
            submitted = st.form_submit_button("Ask Assistant")

        if submitted:
            if not get_knowledge_signature():
                st.warning("Build the knowledge base first from the sidebar before asking questions.")
            elif not user_question.strip():
                st.warning("Enter a question before submitting.")
            else:
                with st.spinner("Analyzing documents..."):
                    try:
                        answer = ask_question(user_question)
                        st.session_state.history.append(
                            {"question": user_question, "answer": answer}
                        )
                    except Exception as exc:
                        st.error(f"Unable to answer the question: {exc}")

        if st.session_state.history:
            render_latest_result(st.session_state.history[-1])
            if len(st.session_state.history) > 1:
                with st.expander("Previous Answers", expanded=False):
                    for item in reversed(st.session_state.history[:-1]):
                        st.markdown(f"**Question:** {html.escape(item['question'])}")
                        st.markdown(item["answer"])
                        st.divider()
        else:
            st.markdown(
                """
                <div class="response-card">
                    <div class="response-label">Ready for Questions</div>
                    <div class="section-copy">
                        Upload PDFs, build the knowledge base, and ask your first question.
                        Results will appear here in a clean readable format.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with right_col:
        st.markdown(
            """
            <div class="info-card">
                <div class="section-title">What This Workspace Does</div>
                <p class="section-copy">
                    The app extracts text from multiple PDFs, stores embeddings in a FAISS
                    index, and answers questions by grounding the response in retrieved page-aware context.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="info-card" style="margin-top: 1rem;">
                <div class="section-title">Best Practices</div>
                <p class="section-copy">
                    Ask specific questions for the strongest results. If you need a particular
                    page, include the page number in your prompt. Rebuild the knowledge base
                    whenever you upload different PDFs.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
