# BalanceIQ: Financial Statement Analysis for Laymen

A Retrieval-Augmented Generation (RAG) application that helps non-experts understand company annual reports. Upload a PDF, ask questions in plain English, and get simple explanations backed by the document — plus charts, news, and a financial glossary.

## Tech Stack

| Layer | Technology |
| ----- | ---------- |
| Frontend | Streamlit |
| Orchestration | LangChain |
| LLM | Google Gemini (`gemini-2.5-flash`) |
| Embeddings | Google `models/text-embedding-004` |
| Vector DB | ChromaDB |
| PDF parsing | PyMuPDF (fitz) |
| Text cleaning | `re` (regex) |
| Data | pandas |
| Charts | matplotlib |
| External data | Web scraping (planned) |
| Secrets | python-dotenv (`.env`) |

## Project Structure (18-step pipeline)

```
fin/
├── app/
│   ├── main.py                     # Step 18 — Streamlit entry point
│   └── components/
│       ├── upload.py               # Step 1  — PDF upload UI
│       ├── chat.py                 # Steps 10, 18 — Q&A interface
│       ├── charts.py               # Steps 16, 18 — chart display
│       ├── news.py                 # Steps 8, 18 — related news
│       └── learn.py                # Steps 17, 18 — glossary UI
│
├── src/
│   ├── config.py                   # Settings, paths, API keys
│   │
│   ├── ingestion/                  # Steps 2–6
│   │   ├── pdf_parser.py           #   Step 2 — PDF → text
│   │   ├── preprocessor.py         #   Step 3 — clean text
│   │   ├── chunker.py              #   Step 4 — split into chunks
│   │   ├── embeddings.py           #   Step 5 — Google embeddings
│   │   └── vector_store.py         #   Step 6 — ChromaDB storage
│   │
│   ├── extraction/                 # Steps 7 & 9
│   │   ├── financial_extractor.py  #   Step 7 — metrics → pandas
│   │   └── board_extractor.py      #   Step 9 — CEO, CFO, directors
│   │
│   ├── external/                   # Step 8
│   │   └── news_fetcher.py         #   Yahoo Finance, MoneyControl, NSE…
│   │
│   ├── retrieval/                  # Steps 10–12
│   │   └── retriever.py            #   Embed question → vector search
│   │
│   ├── rag/                        # Steps 13–15
│   │   ├── context_builder.py      #   Step 13 — merge all context
│   │   └── rag_chain.py            #   Steps 14–15 — prompt + GPT
│   │
│   ├── visualization/              # Step 16
│   │   └── charts.py               #   Revenue / profit / debt charts
│   │
│   ├── glossary/                   # Step 17
│   │   └── terms.py                #   EBITDA, EPS, ROE explanations
│   │
│   └── pipeline/                   # Orchestration
│       ├── ingest.py               #   Upload → Steps 2–9
│       └── query.py                #   Question → Steps 10–17
│
├── data/
│   ├── uploads/                    # Uploaded PDFs
│   ├── chroma_db/                  # ChromaDB persisted collections
│   ├── extracted/                  # pandas CSV/JSON (metrics, board)
│   └── cache/                      # Cached external news
│
├── requirements.txt
├── .env.example
└── README.md
```

## Pipeline Overview

| Step | Action | Module |
| ---- | ------ | ------ |
| 1 | User uploads PDF | `app/components/upload.py` |
| 2 | PDF → text | `ingestion/pdf_parser.py` |
| 3 | Clean text | `ingestion/preprocessor.py` |
| 4 | Split into chunks | `ingestion/chunker.py` |
| 5 | Create embeddings | `ingestion/embeddings.py` |
| 6 | Store in ChromaDB | `ingestion/vector_store.py` |
| 7 | Extract financial metrics | `extraction/financial_extractor.py` |
| 8 | Fetch external news | `external/news_fetcher.py` |
| 9 | Extract board info | `extraction/board_extractor.py` |
| 10 | User asks question | `app/components/chat.py` |
| 11–12 | Embed question + search | `retrieval/retriever.py` |
| 13 | Build full context | `rag/context_builder.py` |
| 14–15 | Prompt + GPT answer | `rag/rag_chain.py` |
| 16 | Generate charts | `visualization/charts.py` |
| 17 | Explain financial terms | `glossary/terms.py` |
| 18 | Display everything | `app/main.py` + components |

## Setup

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env         # add your GOOGLE_API_KEY
streamlit run app/main.py
```

## License

Educational / college project — use freely for learning and interviews.
