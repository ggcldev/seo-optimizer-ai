"""
Renders the gap analysis metrics table in Streamlit.
"""
import streamlit as st
import pandas as pd


def render_gap_table(your_analysis: dict, gaps: dict, audit: dict):
    """Display a color-coded metrics table comparing your page vs SERP."""

    metrics = audit.get("metrics", {})
    wc = metrics.get("word_count", {})
    kd = metrics.get("keyword_density", {})
    hd = metrics.get("heading_coverage", {})

    rows = [
        {
            "Metric": "Word Count",
            "Your Page": your_analysis.get("word_count", 0),
            "SERP Avg": gaps.get("serp_avg_word_count", wc.get("serp_avg", "—")),
            "SERP Top": gaps.get("serp_top_word_count", wc.get("serp_top", "—")),
            "Gap": gaps.get("word_count_gap", "—"),
            "Status": wc.get("status", "—"),
        },
        {
            "Metric": "Keyword Density (%)",
            "Your Page": your_analysis.get("keyword_density", 0),
            "SERP Avg": kd.get("serp_avg", "—"),
            "SERP Top": "—",
            "Gap": gaps.get("keyword_density_gap", "—"),
            "Status": kd.get("status", "—"),
        },
        {
            "Metric": "H2 Headings Count",
            "Your Page": hd.get("yours", "—"),
            "SERP Avg": hd.get("serp_avg", "—"),
            "SERP Top": "—",
            "Gap": "—",
            "Status": hd.get("status", "—"),
        },
        {
            "Metric": "Missing Entities",
            "Your Page": "—",
            "SERP Avg": "—",
            "SERP Top": "—",
            "Gap": len(gaps.get("missing_entities", [])),
            "Status": "gaps" if gaps.get("missing_entities") else "ok",
        },
        {
            "Metric": "Missing Keywords",
            "Your Page": "—",
            "SERP Avg": "—",
            "SERP Top": "—",
            "Gap": len(gaps.get("missing_keywords", [])),
            "Status": "gaps" if gaps.get("missing_keywords") else "ok",
        },
    ]

    df = pd.DataFrame(rows)

    def color_status(val):
        if val == "ok":
            return "background-color: #d4edda; color: #155724"
        if val in ("low", "very_low", "high", "gaps"):
            return "background-color: #f8d7da; color: #721c24"
        return ""

    styled = df.style.applymap(color_status, subset=["Status"])
    st.dataframe(styled, use_container_width=True)

    # Missing keywords & entities as expandable lists
    col1, col2 = st.columns(2)
    with col1:
        with st.expander(f"Missing Keywords ({len(gaps.get('missing_keywords', []))})"):
            for kw in gaps.get("missing_keywords", [])[:20]:
                st.markdown(f"- `{kw}`")
    with col2:
        with st.expander(f"Missing Entities ({len(gaps.get('missing_entities', []))})"):
            for ent in gaps.get("missing_entities", [])[:20]:
                st.markdown(f"- `{ent}`")
