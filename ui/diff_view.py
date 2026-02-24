"""
Before/after diff view using difflib.HtmlDiff.
"""
import difflib
import streamlit as st
import streamlit.components.v1 as components


def render_diff(original: str, optimized: str):
    """Render a side-by-side HTML diff of original vs optimized text."""

    original_lines = original.splitlines(keepends=True)
    optimized_lines = optimized.splitlines(keepends=True)

    html_diff = difflib.HtmlDiff(wrapcolumn=80).make_file(
        original_lines,
        optimized_lines,
        fromdesc="Original",
        todesc="Optimized",
        context=True,
        numlines=3,
    )

    # Inject slightly larger font for readability
    html_diff = html_diff.replace(
        "<body>",
        "<body style='font-family: monospace; font-size: 13px;'>",
    )

    components.html(html_diff, height=650, scrolling=True)

    st.caption("Red = removed / changed   |   Green = added / changed")
