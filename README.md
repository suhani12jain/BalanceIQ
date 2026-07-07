# BalanceIQ: Simplifying Financial Statement Analysis with AI

A Retrieval-Augmented Generation (RAG) application that helps non-experts understand company annual reports. Upload a PDF, ask questions in plain English, and get simple explanations backed by the document — plus extracted metrics, charts, and a separate financial glossary.

## Tech Stack

| Layer | Technology |
| ----- | ---------- |
| Frontend | Streamlit |
| Orchestration | LangChain |
| LLM | Groq (`llama-3.1-8b-instant` via `langchain-groq`) |
| Embeddings | Local HuggingFace (`sentence-transformers/all-MiniLM-L6-v2`) |
| Vector DB | ChromaDB |
| PDF parsing | PyMuPDF (fitz) |
| Metrics extraction | regex + pandas |
| Charts | matplotlib |
| Glossary | Static definitions (Learn tab) |
| Secrets | python-dotenv (`.env`) |

## Features (UI tabs)

| Tab | What it does |
| --- | ------------ |
| **Metrics & Data** | Upload PDF, index report, view extracted revenue/profit/debt/assets |
| **Q&A** | RAG answers from the uploaded report (Groq + ChromaDB retrieval) |
| **Charts** | Revenue, profit, and debt trend plots from extracted metrics |
| **Learn** | Beginner-friendly glossary (EBITDA, EPS, ROE, etc.) — separate from Q&A |

## Project Structure

```
BalanceIQ/
├── app.py                          # Main Streamlit entry point (tabs UI)
├── app/
│   ├── main.py                     # Alternate Streamlit entry point
│   └── components/
│       ├── upload.py               # PDF upload UI
│       ├── chat.py                 # Q&A interface
│       ├── charts.py               # Chart display
│       ├── news.py                 # Related news (planned)
│       └── learn.py                # Glossary UI
│
├── src/
│   ├── config.py                   # Settings, paths, API keys
│   ├── ingestion/                  # PDF → chunks → embeddings → ChromaDB
│   ├── extraction/                 # Financial metrics (regex → pandas)
│   ├── retrieval/                  # Question embedding + vector search
│   ├── rag/
│   │   └── chatbot.py              # Retrieve chunks → Groq answer
│   ├── visualization/              # matplotlib charts
│   ├── glossary/                   # Learn tab term definitions
│   └── pipeline/
│       ├── ingest.py               # Upload orchestration
│       └── query.py                # Q&A orchestration
│
├── data/
│   ├── uploads/                    # Uploaded PDFs
│   ├── chroma_db/                  # ChromaDB collections
│   └── extracted/                  # Metrics CSV per report
│
├── requirements.txt
├── .env.example
└── README.md
```

## Pipeline Overview

### On upload

| Step | Action | Module |
| ---- | ------ | ------ |
| 1 | User uploads PDF | `app.py` / `app/components/upload.py` |
| 2 | PDF → text | `ingestion/pdf_parser.py` |
| 3 | Clean text | `ingestion/preprocessor.py` |
| 4 | Split into chunks | `ingestion/chunker.py` |
| 5 | Create embeddings (local) | `ingestion/embeddings.py` |
| 6 | Store in ChromaDB | `ingestion/vector_store.py` |
| 7 | Extract financial metrics | `extraction/financial_extractor.py` |

### On Q&A

| Step | Action | Module |
| ---- | ------ | ------ |
| 1 | User asks question | Q&A tab |
| 2 | Embed question | `ingestion/embeddings.py` |
| 3 | Vector search (top-k chunks) | `retrieval/retriever.py` |
| 4 | Build prompt with context | `rag/chatbot.py` |
| 5 | Generate answer | Groq via `langchain_groq.ChatGroq` |

The LLM receives **retrieved report excerpts only** — not the full PDF. If the answer is not in those chunks, it should say so.

## Setup

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env         # add your GROQ_API_KEY
streamlit run app.py
```

### Environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
```

Get a Groq API key at [console.groq.com/keys](https://console.groq.com/keys).

Embeddings run locally and do **not** require an API key.

## License

Educational / college project — use freely for learning and interviews.
