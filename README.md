# SEOptimizer AI

AI-powered SEO content gap analysis and optimization tool. Paste a URL and a target keyword — the app scrapes Google's top competitors, finds what your page is missing, and applies precise inline edits via a 3-agent AI pipeline.

## Features

- **Real Google SERP analysis** — fetches actual Google results for your target keyword and location
- **Competitor page scraping** — Scrapling StealthyFetcher bypasses anti-bot on competitor pages
- **Keyword & entity gap analysis** — spaCy NER, YAKE, and KeyBERT surface missing keywords and entities
- **3-agent LangChain pipeline**
  - Agent 1 (Content Auditor) — scores your page and identifies gaps vs SERP top-10
  - Agent 2 (Gap Analyzer) — outputs 8 prioritized, specific edits
  - Agent 3 (Content Editor) — applies edits inline, no full rewrite
- **Before/after diff view** — visual diff of original vs optimized content
- **Export** — download optimized content as Markdown or push results to Google Sheets
- **LLM-agnostic** — runs on Groq (free) today, swap to Claude with one line in `config.py`

## Tech Stack

| Layer | Library |
|---|---|
| UI | Streamlit |
| LLM (default) | `langchain-groq` · llama3-70b (free tier) |
| LLM (upgrade path) | `langchain-anthropic` · Claude 3.5 Sonnet |
| SERP | `googlesearch-python` · real Google results |
| Page scraping | `scrapling` · StealthyFetcher |
| NLP | `spacy` + `yake` + `keybert` |
| Diff | `difflib.HtmlDiff` (stdlib) |
| Export | `gspread` + `pandas` |

## Project Structure

```
SEOptimizer AI/
├── app.py                        # Streamlit entry point
├── config.py                     # LLM factory — change only this to swap models
├── requirements.txt
├── utils.py
├── .streamlit/
│   └── secrets.toml.example      # Copy to secrets.toml and fill in keys
├── tools/
│   ├── serp.py                   # Google SERP → top-10 URLs
│   ├── scraper.py                # Scrapling page fetcher
│   └── analyzer.py               # spaCy + YAKE + KeyBERT gap analysis
├── agents/
│   ├── auditor.py                # Agent 1: content audit JSON
│   ├── gap_analyzer.py           # Agent 2: prioritized edit list
│   └── editor.py                 # Agent 3: apply edits to text
└── ui/
    ├── gap_table.py              # Metrics table
    ├── diff_view.py              # Before/after diff
    └── export.py                 # Markdown download + Google Sheets
```

## Roadmap & TODO

6 phases from code → fully live production app.

---

### Phase 1 — Local Environment Setup
> Goal: get the app running on your machine

- [ ] Install Python 3.10+
- [ ] `pip install -r requirements.txt`
- [ ] `python -m spacy download en_core_web_sm`
- [ ] Copy `.streamlit/secrets.toml.example` → `.streamlit/secrets.toml`
- [ ] Add `GROQ_API_KEY` to `secrets.toml` (get free key at [console.groq.com](https://console.groq.com))

---

### Phase 2 — Local Test Run
> Goal: verify the full pipeline works end-to-end locally

- [ ] `streamlit run app.py`
- [ ] Enter a real URL + keyword and click **Run Analysis**
- [ ] Confirm Google SERP returns 5–10 competitor URLs
- [ ] Confirm competitor pages are scraped (word counts appear)
- [ ] Confirm Gap Analysis tab renders with metrics table
- [ ] Confirm Recommended Edits tab shows 8 prioritized edits
- [ ] Confirm Diff View tab shows before/after changes highlighted
- [ ] Confirm Markdown download works

---

### Phase 3 — Bug Fixes & Prompt Tuning
> Goal: fix any issues found in Phase 2, tighten agent outputs

- [ ] Fix any dependency / import errors
- [ ] Fix any Scrapling scraping failures (switch to `DynamicFetcher` if needed)
- [ ] Fix any LLM JSON parse errors (adjust prompts in `agents/`)
- [ ] Tune Agent 1 prompt if audit score seems off
- [ ] Tune Agent 2 prompt if edits are too vague or too aggressive
- [ ] Tune Agent 3 prompt if editor rewrites instead of making inline edits
- [ ] Handle edge case: page with very little body text

---

### Phase 4 — Google Sheets Export (Optional)
> Goal: enable one-click export to Google Sheets

- [ ] Create a Google Cloud project at [console.cloud.google.com](https://console.cloud.google.com)
- [ ] Enable Google Sheets API and Google Drive API
- [ ] Create a service account and download the JSON key
- [ ] Add the service account JSON to `secrets.toml` under `[gcp_service_account]`
- [ ] Test the **Export to Google Sheets** button in the Export tab
- [ ] Verify rows appear in the generated spreadsheet

---

### Phase 5 — Streamlit Community Cloud Deployment
> Goal: get the app live on a public URL

- [ ] Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
- [ ] Click **New app** → select `ggcldev/seo-optimizer-ai`
- [ ] Set **Main file path** to `app.py`
- [ ] In **Settings → Secrets**, paste your `GROQ_API_KEY` (and `gcp_service_account` if using Sheets)
- [ ] Check **Advanced → Python version** = 3.10 or 3.11
- [ ] Add `packages.txt` if spaCy system deps fail to install (see Notes below)
- [ ] Click **Deploy** and confirm the live URL works
- [ ] Run a full analysis from the live URL to confirm cloud environment works

---

### Phase 6 — Switch to Claude (Upgrade Path)
> Goal: replace Groq with Claude for higher quality outputs

- [ ] Add `langchain-anthropic` to `requirements.txt`
- [ ] Get an Anthropic API key at [console.anthropic.com](https://console.anthropic.com)
- [ ] Add `ANTHROPIC_API_KEY` to `secrets.toml` and Streamlit Cloud Secrets
- [ ] Update `config.py` (replace the `get_llm()` body — see **Switching to Claude** section below)
- [ ] Re-run a full analysis and compare output quality vs Groq
- [ ] Remove `langchain-groq` from `requirements.txt` when satisfied

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/ggcldev/seo-optimizer-ai.git
cd seo-optimizer-ai
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Add your API key

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "your-groq-api-key-here"
```

Get a free Groq API key at [console.groq.com](https://console.groq.com) (no credit card required).

### 4. Run

```bash
streamlit run app.py
```

## Usage

1. Paste your page URL in the sidebar
2. Enter your target keyword
3. Select a location (Philippines, US, UK, etc.)
4. Click **Run Analysis**

The app will:
- Fetch Google top-10 for your keyword
- Scrape your page + all competitors
- Run keyword/entity gap analysis
- Generate a content audit, edit recommendations, and an optimized version of your text

Results are shown across 4 tabs: **Gap Analysis · Recommended Edits · Diff View · Export**

## Deploying to Streamlit Community Cloud

1. Push this repo to GitHub (already done)
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect the repo
3. Set **Main file path** to `app.py`
4. In **Settings → Secrets**, add:

```toml
GROQ_API_KEY = "your-groq-api-key-here"
```

## Switching to Claude

When you're ready to upgrade from Groq to Claude, edit only `config.py`:

```python
# Add to requirements.txt: langchain-anthropic
# Add to secrets.toml: ANTHROPIC_API_KEY = "sk-ant-..."

from langchain_anthropic import ChatAnthropic

def get_llm():
    return ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        api_key=st.secrets["ANTHROPIC_API_KEY"],
    )
```

No changes needed in agents, tools, or UI.

## Google Sheets Export (Optional)

1. Create a Google Cloud service account and download the JSON credentials
2. Add to `.streamlit/secrets.toml`:

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "..."
private_key = "-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----\n"
client_email = "your-sa@your-project.iam.gserviceaccount.com"
client_id = "..."
...
```

## Notes

- Google may rate-limit SERP fetching for high-volume use. If this happens, uncomment the SerpAPI branch in `tools/serp.py` and add a `SERPAPI_KEY` to secrets (100 free searches/month).
- Scrapling's `StealthyFetcher` handles most Cloudflare-protected competitor pages. Very aggressive bot protection may require switching to `DynamicFetcher` (Playwright) in `tools/scraper.py`.
