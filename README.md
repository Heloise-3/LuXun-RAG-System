# LuXun-RAG-System

A Chinese-language application for generating prose inspired by Lu Xun's writing. It combines semantic retrieval and literary metadata with pretrained language-model APIs. The web interface shows the generated text alongside the passages used as references.

Generated text is not Lu Xun's original writing. This project does not train or fine-tune a model.

## Live demo

[Open the writing app](https://luxun-rag-system.onrender.com/)

Enter a passage or scene, choose 1–3 reference passages, and select **生成文字**. The result appears alongside the retrieved passages and source notes.

The demo runs on Render's free tier. After inactivity, the first visit may take 50 seconds or longer while the service wakes up.

![Writing interface](docs/images/interface.jpg)

## Features

The application brings query analysis, hybrid retrieval and text generation into one workflow, with reference passages available for comparison alongside each result.

- **Chinese writing interface:** enter a passage or scene, choose the number of references, and view the generated text in a responsive layout with loading and error states.
- **Hybrid retrieval:** combine embedding similarity with metadata for tone, theme, literary devices and narrative perspective.
- **Visible reference material:** inspect retrieved passages, source notes, query tags and separate semantic, metadata and combined scores.
- **Consistent tag vocabulary:** analyze each request once and validate its tags against the same vocabulary used to annotate the corpus.
- **Corpus and index management:** validate passage records, detect incompatible indexes and replace rebuilt indexes only after all embedding requests succeed.
- **Server-side configuration:** keep provider credentials in environment variables and handle input limits, provider timeouts and errors through FastAPI.

The current corpus contains 14 passages. Corpus provenance, validation results and the limits of this prototype are described below.

Parts of the implementation were developed with assistance from OpenAI Codex.

## Run locally

Requires Python 3.10+; tested here with Python 3.14.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` locally and fill in `DEEPSEEK_API_KEY` and `SILICONFLOW_API_KEY`. Do not commit real credentials. Then start the application:

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000 in a browser. The page and API use the same origin; do not open `frontend/index.html` directly. `python server.py` is a compatibility launcher for the same application.

The app starts without credentials, but generation requires both providers. Each generation normally makes three API requests: query analysis, query embedding and final generation. They may incur provider charges. SDK retries are disabled; each provider call has a 25-second timeout, and the browser stops waiting after 90 seconds. Closing the browser does not guarantee cancellation of an upstream request.

## How retrieval works

```text
Writing request
  -> query metadata + query embedding
  -> semantic and metadata scoring
  -> ranked reference passages
  -> style prompt
  -> generated text with visible retrieval evidence
```

The existing ranking formula is retained:

```text
combined score = 0.6 × cosine similarity + 0.4 × metadata score
metadata score = 0.25 × tone overlap
               + 0.25 × theme overlap
               + 0.15 × device overlap
               + 0.35 × narrative match
```

These are heuristic weights, not learned or benchmark-validated parameters. A matching score is not a writing-quality score or probability.

## Corpus and embeddings

The active corpus has **14 passages**. Eleven excerpts have been checked against the digital originals linked in each record. Three original passages are retained without further source review and remain `unverified`. The supplied page references for the 1981 print edition of *Lu Xun Quanji* have not been verified and are not presented as confirmed citations.

Embeddings use `Qwen/Qwen3-Embedding-8B`, with 4,096 dimensions in the current index. The index records the model identifier and corpus checksum. Changing corpus text, metadata or model requires rebuilding the index. Tags follow [dictionary.md](dictionary.md) and represent editorial judgments.

Validate the corpus offline:

```bash
python corpus_tools.py corpus.json
```

Rebuilding sends paid embedding requests. The current corpus includes three unverified legacy records, so an intentional full rebuild uses:

```bash
python build_embedding.py --confirm-cost --allow-unverified
```

The prior index is replaced only after all requests complete. Keep the corpus and matching index together when copying or uploading files. See [corpus notes](docs/CORPUS.md).

## API

```http
POST /api/generate
Content-Type: application/json

{"query":"写一段关于看客心理和群体麻木的场景","top_k":2}
```

`query` accepts 1–1,000 characters; whitespace-only input is rejected. `top_k` accepts 1–5 and defaults to 2. The interface offers 1–3 reference passages.

The response contains `query`, `metadata`, `context`, `retrieval` and `output`. Retrieval results include passage IDs, text, provenance notes and all three scores. Embedding vectors are omitted from responses.

`GET /health` checks whether the app is running; it does not check provider credentials or billing. `GET /docs` exposes the API schema. The earlier `GET /generate` interface is replaced by the POST endpoint.

## Validation and limits

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

The automated suite currently has 24 passing cases covering ranking, corpus/index consistency, query vocabulary, API validation and error handling. Automated provider interactions are mocked.

Two separate authorized browser runs used real providers. After restoring the original passages, the same test request retrieved original IDs 1 and 3, and the full request completed in approximately 6.39 seconds. This is one observed run, not a latency benchmark. See [validation notes](docs/VALIDATION_PUBLIC.md).

The public deployment passed HTTP checks for the homepage, static files and health endpoint. The project owner also confirmed a successful generation through the deployed interface. This confirms a working demonstration; it is not a load test or quality evaluation.

The corpus is small and unevenly distributed. The project has no validated benchmark for Lu Xun-style fidelity, general retrieval relevance or educational outcomes. It includes no model training or LoRA.

## Project structure

```text
main.py                 FastAPI routes and frontend serving
rag.py                  retrieval context and generation prompt
query_analyzer.py       query metadata with vocabulary validation
search_score.py         cosine similarity and hybrid ranking
embedding.py            embedding-provider calls
config.py               environment configuration and clients
corpus_tools.py         offline validation and index checks
build_embedding.py      explicit, atomic index rebuild
corpus.json              active passages and tags
corpus_embeddings.json   matching model-labelled index
frontend/                HTML, CSS and browser interaction
tests/                   offline automated tests
docs/                    corpus and validation notes
```

## Hosting

The public demo is hosted on [Render](https://luxun-rag-system.onrender.com/), which serves the FastAPI backend and web interface from the same service. GitHub hosts the source code.

Deployment settings:

- Runtime: Python 3.
- Build command: `pip install -r requirements.txt`.
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`.
- Health check: `/health`.
- Provider credentials: host-side environment variables for `DEEPSEEK_API_KEY` and `SILICONFLOW_API_KEY`.

Free hosting does not cover model-provider charges. Requests to the public demo use the operator's provider accounts. The app limits concurrent generation requests to two per process, but has no visitor authentication or global request quota. Wider sharing should be accompanied by access controls, request rate limits and provider spending controls.
