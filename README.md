# Dataiku Technical Assessment

#  IT Support Advisor - ReAct Agent

An intelligent IT support ticket analysis system using a ReAct (Reasoning + Acting) agent architecture. The system analyzes support tickets, searches a knowledge base using semantic vector search, and provides prioritized recommendations.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-Embeddings-green.svg)
![Supabase](https://img.shields.io/badge/Supabase-Vector_DB-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

##  Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Knowledge Base](#-knowledge-base)


##  Overview

This project implements an AI-powered IT support advisor that:

1. **Analyzes** incoming support tickets
2. **Categorizes** issues automatically (Software, Hardware, Network, etc.)
3. **Searches** a vector-based knowledge base for relevant solutions
4. **Prioritizes** tickets based on urgency and business impact
5. **Recommends** solutions with confidence scores

## Architecture

![IT Support Advisor Architecture](docs/architecture.png)

### Pipeline Flow

1. **Ticket Input** → User submits IT support ticket
2. **ReAct Agent** (GPT-4o-mini) → Reasoning and action loop
3. **Tools Execution**:
   - **Categorizer** → Hardware / Software / Network / Access classification
   - **Prioritization** → LOW / MEDIUM / HIGH / CRITICAL
   - **Vector Search** → Query embedding + KB retrieval + Reranking
4. **Safety Layer** → Llama Guard 3 + System Prompt validation
5. **Final Response** → Actionable recommendation with KB reference

##  Features

| Feature | Description |
|---------|-------------|
| **ReAct Agent** | Iterative reasoning and action loop for complex problem solving |
| **Semantic Search** | Vector-based KB search using OpenAI embeddings |
| **Reranking** | Cross-encoder reranking for improved relevance |
| **Auto-Categorization** | ML-based ticket classification |
| **Priority Scoring** | Dynamic priority calculation based on urgency |
| **Safety Checking** | Content moderation using Llama Guard 3 |

##  Tech Stack

| Component | Technology |
|-----------|------------|
| **LLM** | OpenAI GPT-4 / GPT-3.5 |
| **Embeddings** | OpenAI `text-embedding-3-small` (1536 dim) |
| **Vector DB** | Supabase with pgvector |
| **Reranker** | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| **Safety** | Llama Guard 3 |
| **Framework** | Python 3.10+ |

##  Installation

### Prerequisites

- Python 3.10+
- Supabase account
- OpenAI API key

### Setup

```bash
# Clone the repository
git clone https://github.com/OUALYoss/Dataiku-Technical-Assessment-OUALY-Ossama.git
cd Dataiku-Technical-Assessment-OUALY-Ossama

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

##  Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Optional
EMBEDDING_MODEL=text-embedding-3-small
```

### Supabase Setup

Run this SQL in your Supabase SQL Editor:

```sql
-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Create KB articles table
CREATE TABLE kb_articles (
    id SERIAL PRIMARY KEY,
    kb_id VARCHAR(20) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    keywords TEXT[] DEFAULT '{}',
    avg_resolution_time VARCHAR(50),
    success_rate VARCHAR(20),
    related_articles TEXT[] DEFAULT '{}',
    embedding vector(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create vector index
CREATE INDEX kb_articles_embedding_idx 
ON kb_articles USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create search function
CREATE OR REPLACE FUNCTION match_kb_articles(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.5,
    match_count int DEFAULT 5,
    filter_category text DEFAULT NULL
)
RETURNS TABLE (
    kb_id varchar,
    title text,
    category varchar,
    content text,
    keywords text[],
    avg_resolution_time varchar,
    success_rate varchar,
    related_articles text[],
    similarity float
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        k.kb_id, k.title, k.category, k.content,
        k.keywords, k.avg_resolution_time, k.success_rate,
        k.related_articles,
        1 - (k.embedding <=> query_embedding) as similarity
    FROM kb_articles k
    WHERE (filter_category IS NULL OR k.category = filter_category)
      AND 1 - (k.embedding <=> query_embedding) > match_threshold
    ORDER BY k.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Disable RLS for simplicity (or configure policies)
ALTER TABLE kb_articles DISABLE ROW LEVEL SECURITY;
```

### Seed Knowledge Base

```bash
python seed_knowledge_base.py
```

##  Usage

### Run the Agent

```bash
python main.py
```

### Example Output

####  Valid IT Support Request

```
**************************************************
*       IT SUPPORT ADVISOR - ReAct Agent         *
**************************************************

Reranker loaded!
Supabase Vector KB Searcher initialized
  Model: text-embedding-3-small
  Reranking: Enabled
Safety Checker initialized

**************************************************

Start analyzing the ticket: TKT-022
Subject: Zoom audio not working in meetings

=> Generating final recommendation based on gathered information

--------------------------------------------------
Llama Guard
--------------------------------------------------

Running safety check:
  Is safe: True
  Raw response: safe
safety check: Done

==================================================
FINAL RECOMMENDATION
==================================================

SOFTWARE_ISSUES (85%) | MEDIUM | 15-30 minutes

Actions:
  1. Check Zoom audio settings: Go to Zoom settings → Audio → Test Speaker and Test Mic.
  2. Ensure the correct microphone and speaker are selected in Zoom settings.
  3. Check system audio settings: Right-click the speaker icon in the taskbar → Open Sound settings → Ensure the correct output and input devices are set.
  4. Restart Zoom and rejoin the meeting.
  5. Check for any pending Zoom updates and install them.

✓ Tools: Zoom application, Operating system sound settings
✓ KB: KB-318
==================================================
```

####  Out-of-Scope Request

```
**************************************************
*       IT SUPPORT ADVISOR - ReAct Agent         *
**************************************************

Start analyzing the ticket: TKT-035
Subject: Which stocks should I buy?

=> Generating final recommendation based on gathered information

--------------------------------------------------
Llama Guard
--------------------------------------------------

Running safety check:
  Is safe: True
  Raw response: safe
safety check: Done

==================================================
FINAL RECOMMENDATION
==================================================

Actions:
  1. This request is outside IT support scope
  2. Please contact a financial advisor for investment advice
==================================================
```

## 📁 Project Structure

```
Dataiku-Technical-Assessment-OUALY-Ossama/
├── src/
│   ├── agent/
│   │   └── react_agent.py        # ReAct agent implementation
│   ├── tools/
│   │   ├── ticket_categorizer.py # Ticket classification
│   │   ├── supabase_kb_searcher.py # Vector KB search
│   │   ├── reranker.py           # Cross-encoder reranking
│   │   ├── priority_calculator.py # Priority scoring
│   │   └── safety_checker.py     # Llama Guard integration
│   └── prompts/
│       └── system_prompts.py     # Agent prompts
├── data/
│   └── knowledge_base.py         # KB articles data
├── main.py                       # Entry point
├── seed_knowledge_base.py        # KB seeding script
├── requirements.txt
├── .env.example
└── README.md
```

##  Knowledge Base

The system includes 20 pre-built IT support articles across 5 categories:

| Category | Articles | Topics |
|----------|----------|--------|
| `PASSWORD_ACCESS` | 5 | Password reset, Account lockout, 2FA, VPN credentials |
| `SOFTWARE_ISSUES` | 6 | Office crashes, Outlook, Teams, Zoom, Adobe, Browsers |
| `NETWORK_CONNECTIVITY` | 6 | WiFi, VPN, Network drives, Slow network, RDP |
| `HARDWARE_PROBLEMS` | 5 | Printers, Monitors, Keyboard/Mouse, Laptops |
| `EMAIL_ISSUES` | 3 | Calendar sync, Spam, Attachments |


**OUALY Ossama** : Engineering Student at ENSAE Paris


---


