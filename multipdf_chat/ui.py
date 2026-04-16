from __future__ import annotations

import html

import streamlit as st

from multipdf_chat.config import ROBOT_IMAGE_PATH
from multipdf_chat.knowledge_base import (
    build_knowledge_base,
    extract_pdf_pages,
    get_knowledge_signature,
    is_google_api_key_configured,
    load_manifest,
)


def render_hero():
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-badge">AI-powered knowledge workspace</div>
            <div class="hero-title">Multi-PDF Research Assistant</div>
            <p class="hero-copy">
                Upload one or more PDF files, build a searchable knowledge base, and ask
                focused questions against the indexed content. Designed for study, analysis,
                and document review workflows.
            </p>
            <div class="stats-grid">
                <div class="stat-chip">
                    <span class="stat-label">Retrieval</span>
                    <span class="stat-value">Page-aware semantic search</span>
                </div>
                <div class="stat-chip">
                    <span class="stat-label">Model Stack</span>
                    <span class="stat-value">Gemini chat and embeddings</span>
                </div>
                <div class="stat-chip">
                    <span class="stat-label">Use Case</span>
                    <span class="stat-value">Research, review, and Q&A</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar():
    with st.sidebar:
        if ROBOT_IMAGE_PATH.exists():
            st.image(str(ROBOT_IMAGE_PATH), use_container_width=True)

        st.markdown(
            """
            <div class="sidebar-card">
                <div class="sidebar-title">Document Processing</div>
                <p class="sidebar-copy">
                    Upload your PDF files, create the vector index, and then ask questions
                    from the main workspace.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        pdf_docs = st.file_uploader(
            "Upload PDF files",
            type=["pdf"],
            accept_multiple_files=True,
        )

        if st.button("Build Knowledge Base"):
            if not pdf_docs:
                st.warning("Upload at least one PDF file before processing.")
            else:
                with st.spinner("Indexing documents..."):
                    try:
                        pages = extract_pdf_pages(pdf_docs)
                        if not pages:
                            st.error("No extractable text was found in the uploaded PDFs.")
                        else:
                            result = build_knowledge_base(pages)
                            if result["retrieval_mode"] == "semantic":
                                st.success(
                                    f"Knowledge base created successfully for {len(pdf_docs)} file(s), "
                                    f"{result['page_count']} page(s), and {result['chunk_count']} chunk(s). "
                                    "Gemini semantic search is ready."
                                )
                            else:
                                st.warning(
                                    f"Knowledge base created in local keyword mode for {len(pdf_docs)} file(s), "
                                    f"{result['page_count']} page(s), and {result['chunk_count']} chunk(s). "
                                    "The app will still answer questions, but semantic search is unavailable."
                                )
                                if result["build_warning"]:
                                    st.caption(result["build_warning"])
                    except Exception as exc:
                        st.error(f"Processing failed: {exc}")

        signature = get_knowledge_signature()
        if signature:
            manifest = load_manifest(signature)
            mode = manifest.get("retrieval_mode", "keyword")
            mode_title = "Semantic Search Active" if mode == "semantic" else "Local Keyword Mode"
            mode_copy = (
                "Gemini embeddings and semantic retrieval are available for higher-quality matching."
                if mode == "semantic"
                else "The app is using a local keyword index. It stays usable even when Gemini or the network is unavailable."
            )
            st.markdown(
                f"""
                <div class="sidebar-card" style="margin-top: 1rem;">
                    <div class="sidebar-title">{mode_title}</div>
                    <p class="sidebar-copy">{mode_copy}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if manifest.get("build_warning"):
                st.caption(manifest["build_warning"])
        elif not is_google_api_key_configured():
            st.info(
                "Add GOOGLE_API_KEY to enable Gemini-powered semantic search. "
                "Without it, the app can still run in local keyword mode."
            )

        st.markdown(
            """
            <div class="sidebar-card" style="margin-top: 1rem;">
                <div class="sidebar-title">Recommended Workflow</div>
                <ul class="sidebar-list">
                    <li>Upload PDFs and build the knowledge base.</li>
                    <li>Ask precise questions in the main panel.</li>
                    <li>Use page numbers for the most accurate answers.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_latest_result(item):
    st.markdown(
        f"""
        <div class="result-shell">
            <div class="result-kicker">Latest Result</div>
            <p class="result-question">{html.escape(item["question"])}</p>
            <div class="result-meta">Grounded in the indexed PDF content</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(item["answer"])
