# LuXun-RAG-System

A literary personality RAG system for generating texts inspired by Lu Xun's writing style.

This project explores how Retrieval-Augmented Generation (RAG) and metadata-based retrieval can be used to control an LLM's literary personality, narrative perspective, and stylistic consistency.

---

## Overview

Large language models can imitate general writing styles, but maintaining a stable literary personality requires more than prompt engineering.

This project builds a workflow that combines:

- Query analysis
- Metadata extraction
- Semantic retrieval
- Metadata-based retrieval
- Hybrid ranking
- Narrative control
- Prompt engineering
- LLM generation

The goal is not to train a new model, but to build a controllable literary generation system.

---

## System Architecture

```
User Query

      ↓

Query Analyzer

      ↓

Metadata Extraction

      ↓

Hybrid Retrieval
(Semantic Similarity + Metadata Similarity)

      ↓

Retrieved Literary References

      ↓

Personality Control Prompt

      ↓

LLM Generation

      ↓

Generated Text
```

---

## Features

### 1. Query Analyzer

The system first analyzes the user's request instead of directly generating text.

Extracted metadata:

- Tone
- Theme
- Literary devices
- Narrative perspective


Example:

Input:

```
写一段关于看客心理和群体麻木的场景
```

Output:

```json
{
  "tone": [
    "cold",
    "detached",
    "ironic"
  ],
  "theme": [
    "crowd",
    "apathy",
    "spectatorship"
  ],
  "narrative": "observer"
}
```

---

### 2. Hybrid Retrieval

Traditional RAG mainly relies on embedding similarity.

This project combines:

```
Final Score =

0.6 × Semantic Similarity

+

0.4 × Metadata Similarity
```

Metadata similarity considers:

- Tone
- Theme
- Literary device
- Narrative perspective


This allows retrieval results to better match the desired literary personality.

---

### 3. Narrative Control

The system explicitly controls narrative consistency.

For example:

```
Narrative:
observer
```

Generation rules:

- Avoid author-summary endings
- Avoid sentimental reflection
- Avoid philosophical conclusions
- Maintain cold observation
- Use concrete scenes and actions

This reduces common LLM problems:

- AI literary tone
- Excessive emotional expression
- Modern sentimental style

---

## Project Structure

```
LuXun-RAG-System/

├── corpus.json
├── corpus_embeddings.json

├── embedding.py
├── build_embedding.py

├── query_analyzer.py

├── search_score.py

├── rag.py

├── main.py

├── requirements.txt

└── README.md
```

---

## Tech Stack

- Python
- DeepSeek API
- SiliconFlow Embedding API
- OpenAI Python SDK
- NumPy
- FastAPI (planned)


---

## Installation

Clone the repository:

```bash
git clone https://github.com/Heloise-3/LuXun-RAG-System.git

cd LuXun-RAG-System
```

Create virtual environment:

```bash
python3 -m venv .venv

source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Environment Setup

Create a `.env` file:

```
DEEPSEEK_API_KEY=your_api_key
SILICONFLOW_API_KEY=your_api_key
```

The API keys are loaded through environment variables.

---

## Running

Build embeddings:

```bash
python build_embedding.py
```

Run RAG generation:

```bash
python rag.py
```

Example:

```
写一段关于看客心理和群体麻木的场景
```

---

## Current Status

Completed:

- [x] Basic RAG pipeline
- [x] Embedding retrieval
- [x] Query analyzer
- [x] Metadata-based retrieval
- [x] Hybrid retrieval
- [x] Retrieval debugging
- [x] Narrative control prompt


Future improvements:

- [ ] Expand literary corpus
- [ ] Vector database integration
- [ ] Web API deployment
- [ ] Evaluation framework
- [ ] Multi-author personality system


---

## Evaluation

The system evaluates generation quality based on:

- Retrieval relevance
- Narrative consistency
- Personality similarity
- Presence of AI-generated literary patterns
