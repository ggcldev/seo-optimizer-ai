"""
SEOptimizer AI — Main Streamlit app.

Workflow:
  1. User inputs URL + keyword + location
  2. Scrape your page + SERP top-10 competitor pages
  3. Keyword / entity gap analysis (spaCy + YAKE + KeyBERT)
  4. 3-agent LangChain pipeline:
       Agent 1 (Auditor)     → structured audit JSON
       Agent 2 (Gap Analyzer) → prioritized edit list
       Agent 3 (Editor)       → optimized full text
  5. Display: Gap table | Edit recommendations | Diff view | Export
"""
import streamlit as st

from config import get_llm
from tools.serp import get_serp_urls
from tools.scraper import fetch_page, fetch_pages_parallel
from tools.analyzer import analyze_content, compute_gaps
from agents.auditor import run_audit
from agents.gap_analyzer import run_gap_analysis
from agents.editor import run_edit
from ui.gap_table import render_gap_table
from ui.diff_view import render_diff
from ui.export import download_markdown_button, export_to_gsheet

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SEOptimizer AI",
    page_icon="🔍",
    layout="wide",
)

st.title("SEOptimizer AI")
st.caption("AI-powered SEO content gap analysis & optimization · Powered by Groq + LangChain")

# ─── Sidebar inputs ───────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Analysis Settings")

    your_url = st.text_input(
        "Your Page URL",
        placeholder="https://yoursite.com/page-to-optimize",
    )
    keyword = st.text_input(
        "Target Keyword",
        placeholder="seo tools philippines",
    )
    location = st.selectbox(
        "Location / SERP Region",
        options=["ph", "us", "uk", "au", "global"],
        format_func=lambda x: {
            "ph": "Philippines (PH)",
            "us": "United States (US)",
            "uk": "United Kingdom (UK)",
            "au": "Australia (AU)",
            "global": "Global",
        }[x],
    )
    n_competitors = st.slider("Competitors to analyze", min_value=3, max_value=10, value=5)

    run_btn = st.button("Run Analysis", type="primary", use_container_width=True)

    st.divider()
    st.caption("LLM: Groq llama3-70b · Switch to Claude in `config.py`")


# ─── Main content ─────────────────────────────────────────────────────────────
if not run_btn:
    st.info("Enter your page URL and target keyword in the sidebar, then click **Run Analysis**.")
    st.stop()

if not your_url or not keyword:
    st.error("Please fill in both the URL and the target keyword.")
    st.stop()

# ── Step 1: SERP ──────────────────────────────────────────────────────────────
with st.status("Fetching SERP results...", expanded=False) as status:
    serp_urls = get_serp_urls(keyword, location=location, n=n_competitors + 2)
    # Exclude the user's own URL from competitors
    serp_urls = [u for u in serp_urls if your_url not in u][:n_competitors]
    status.update(label=f"Found {len(serp_urls)} competitor URLs", state="complete")

# ── Step 2: Scrape ────────────────────────────────────────────────────────────
with st.status("Scraping pages...", expanded=False) as status:
    your_page_raw = fetch_page(your_url)
    competitor_pages_raw = fetch_pages_parallel(serp_urls)
    status.update(
        label=f"Scraped your page + {len(competitor_pages_raw)} competitors",
        state="complete",
    )

    if your_page_raw.get("error"):
        st.warning(f"Could not fully scrape your page: {your_page_raw['error']}")

# ── Step 3: Analysis ──────────────────────────────────────────────────────────
with st.status("Running keyword analysis...", expanded=False) as status:
    your_analysis = {
        **your_page_raw,
        **analyze_content(your_page_raw.get("body_text", ""), keyword),
    }
    serp_analyses = []
    for raw in competitor_pages_raw:
        analysis = {**raw, **analyze_content(raw.get("body_text", ""), keyword)}
        serp_analyses.append(analysis)

    gaps = compute_gaps(your_analysis, serp_analyses)
    status.update(label="Keyword analysis complete", state="complete")

# ── Step 4: Agents ────────────────────────────────────────────────────────────
llm = get_llm()

with st.status("Agent 1 — Auditing content...", expanded=False) as status:
    audit = run_audit(llm, keyword, your_analysis, serp_analyses, gaps)
    status.update(label="Content audit complete", state="complete")

with st.status("Agent 2 — Analyzing gaps...", expanded=False) as status:
    edits_result = run_gap_analysis(llm, keyword, audit, gaps)
    status.update(label="Gap analysis complete", state="complete")

with st.status("Agent 3 — Applying edits...", expanded=False) as status:
    optimized_text = run_edit(llm, keyword, your_page_raw.get("body_text", ""), edits_result)
    status.update(label="Content edits applied", state="complete")

# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "Gap Analysis",
    "Recommended Edits",
    "Diff View",
    "Export",
])

# ── Tab 1: Gap Analysis ───────────────────────────────────────────────────────
with tab1:
    score = audit.get("overall_score")
    if score is not None:
        col_score, col_empty = st.columns([1, 3])
        with col_score:
            color = "green" if score >= 70 else ("orange" if score >= 40 else "red")
            st.metric("Overall SEO Score", f"{score}/100")

    st.subheader("Metrics vs SERP")
    render_gap_table(your_analysis, gaps, audit)

    if audit.get("strengths"):
        st.subheader("Page Strengths")
        for s in audit["strengths"]:
            st.success(s)

    if audit.get("gaps"):
        st.subheader("Identified Gaps")
        for g in audit["gaps"]:
            st.warning(g)

# ── Tab 2: Recommended Edits ──────────────────────────────────────────────────
with tab2:
    edits = edits_result.get("edits", [])
    if edits_result.get("parse_error"):
        st.warning("Agent output could not be parsed as JSON. Raw output:")
        st.code(edits_result.get("raw_output", ""))
    elif not edits:
        st.info("No specific edits recommended.")
    else:
        st.subheader(f"{len(edits)} Recommended Edits")
        for edit in sorted(edits, key=lambda x: x.get("priority", 99)):
            with st.expander(f"#{edit['priority']} · {edit.get('type','').replace('_',' ').title()} — {edit.get('action','')[:80]}"):
                st.markdown(f"**Location:** {edit.get('location','')}")
                st.markdown(f"**Action:** {edit.get('action','')}")
                st.markdown(f"**Why:** {edit.get('rationale','')}")

# ── Tab 3: Diff View ──────────────────────────────────────────────────────────
with tab3:
    original = your_page_raw.get("body_text", "")
    if not original:
        st.warning("Original page text could not be extracted.")
    elif not optimized_text or optimized_text == original:
        st.info("No changes were applied — optimized text is identical to original.")
    else:
        st.subheader("Before vs After")
        render_diff(original, optimized_text)

# ── Tab 4: Export ─────────────────────────────────────────────────────────────
with tab4:
    st.subheader("Export Results")

    col_md, col_gs = st.columns(2)

    with col_md:
        st.markdown("**Download Optimized Content**")
        if optimized_text:
            download_markdown_button(optimized_text, keyword)
        else:
            st.info("No optimized text to download yet.")

    with col_gs:
        st.markdown("**Export to Google Sheets**")
        if "gcp_service_account" not in st.secrets:
            st.info(
                "Add `gcp_service_account` credentials to your `.streamlit/secrets.toml` "
                "to enable Google Sheets export."
            )
        else:
            if st.button("Export to Google Sheets"):
                export_to_gsheet(
                    keyword=keyword,
                    url=your_url,
                    gaps=gaps,
                    audit=audit,
                    edits=edits_result.get("edits", []),
                )

    st.divider()
    st.subheader("SERP Competitor URLs Found")
    for i, u in enumerate(serp_urls, 1):
        st.markdown(f"{i}. {u}")
