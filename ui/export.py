"""
Export helpers: Markdown download button + Google Sheets export.
"""
import streamlit as st
import pandas as pd


def download_markdown_button(optimized_text: str, keyword: str):
    """Render a Streamlit download button for the optimized content as Markdown."""
    filename = keyword.lower().replace(" ", "-") + "-optimized.md"
    st.download_button(
        label="Download Optimized Content (.md)",
        data=optimized_text.encode("utf-8"),
        file_name=filename,
        mime="text/markdown",
    )


def export_to_gsheet(
    keyword: str,
    url: str,
    gaps: dict,
    audit: dict,
    edits: list[dict],
    sheet_name: str = "SEOptimizer Exports",
):
    """
    Append the analysis results to a Google Sheet.
    Requires gcp_service_account credentials in st.secrets.
    """
    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError:
        st.error("gspread / google-auth not installed.")
        return

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
    except Exception as e:
        st.error(f"Google Sheets auth failed: {e}")
        return

    try:
        try:
            sheet = client.open(sheet_name)
        except gspread.SpreadsheetNotFound:
            sheet = client.create(sheet_name)
            sheet.share(creds_dict.get("client_email"), perm_type="user", role="writer")

        ws = sheet.sheet1

        # Write header if sheet is empty
        if ws.row_count == 0 or not ws.get_all_values():
            ws.append_row([
                "Keyword", "URL",
                "Your Word Count", "SERP Avg Word Count", "Word Count Gap",
                "Your KW Density", "SERP Avg KW Density",
                "Missing Keywords Count", "Missing Entities Count",
                "Overall Score", "Top Edits",
            ])

        edits_summary = " | ".join(
            e.get("action", "") for e in sorted(edits, key=lambda x: x.get("priority", 99))[:3]
        )

        ws.append_row([
            keyword,
            url,
            gaps.get("word_count_gap", 0) + gaps.get("serp_avg_word_count", 0),
            gaps.get("serp_avg_word_count", 0),
            gaps.get("word_count_gap", 0),
            "",
            "",
            len(gaps.get("missing_keywords", [])),
            len(gaps.get("missing_entities", [])),
            audit.get("overall_score", ""),
            edits_summary,
        ])

        sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet.id}"
        st.success(f"Exported to Google Sheets: [Open Sheet]({sheet_url})")

    except Exception as e:
        st.error(f"Export failed: {e}")
