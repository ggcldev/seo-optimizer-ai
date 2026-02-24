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
