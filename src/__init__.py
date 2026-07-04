"""
FinSum core package.

Organized by pipeline stage:
  ingestion  → Steps 2–6  (parse, clean, chunk, embed, ChromaDB)
  extraction → Steps 7, 9 (financial metrics, board info)
  external   → Step 8     (latest news / market data)
  retrieval  → Steps 10–12 (semantic search)
  rag        → Steps 13–15 (context + GPT)
  visualization → Step 16 (charts)
  glossary   → Step 17    (financial literacy)
  pipeline   → orchestration (upload → full ingest)
"""
