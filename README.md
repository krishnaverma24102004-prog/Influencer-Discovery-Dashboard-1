# AI Influencer Intelligence Platform

A highly optimized, production-ready Streamlit application that automates the discovery, classification, and ranking of social media influencers for specific campaigns (e.g., government initiatives, brand partnerships). 

The platform seamlessly aggregates live social profiles from the web, leverages Large Language Models (LLMs) to classify their niche and political orientation, and applies deterministic keyword and follower ranking to output a highly relevant list of target influencers.

---

## 🚀 Features

- **Live Profile Discovery**: Generates multiple search query permutations across X, Instagram, YouTube, and LinkedIn, rigorously extracting genuine influencer profiles while ignoring generic webpages and news articles.
- **Offline CSV Support**: Completely decoupled ingestion pipeline allowing users to upload and analyze their own `.csv` or `.xlsx` influencer datasets natively.
- **AI Classification**: Integrates with OpenRouter (using Gemini or any supported model) to semantically analyze influencer bios and recent posts, inferring content niches, languages, and geopolitical orientations.
- **Bulletproof Fallback Logic**: If the AI API fails, times out, or encounters a rate limit, a deterministic local keyword engine automatically takes over without crashing the application.
- **Asynchronous Execution**: Utilizes concurrent thread pools for AI processing and heavy session state caching to ensure a blazing fast, highly responsive dashboard experience.
- **Interactive Dashboard**: Filter influencers natively by platform, follower counts, political alignment, and niche without triggering expensive server reruns. One-click CSV exports.

---

## 🏗 Architecture

The platform follows a modular pipeline design:

```
Live Search (SerpAPI/DuckDuckGo)  OR  CSV Upload
                ↓
          Preprocessing
                ↓
    AI Classification (OpenRouter)
          (Failure Boundary)
                ↓
  Keyword Engine (Local Fallback)
                ↓
        Relevance Ranking
                ↓
     Session Cached Filtering
                ↓
          CSV Export
```

---

## 📂 Folder Structure

```
Influencer-Discovery/
├── app.py                      # Main Streamlit dashboard and session state orchestrator
├── app_config.py               # Centralized environment variable loader
├── requirements.txt            # Python dependencies
├── .env.example                # Template for required environment keys
├── STREAMLIT_SECRETS_EXAMPLE.md # Instructions for cloud deployment secrets
├── DEPLOYMENT_GUIDE.md         # Beginner-friendly guide for deploying to Streamlit Cloud
├── classifier/
│   ├── ai_classifier.py        # LLM integration via OpenRouter
│   └── keyword_classifier.py   # Fallback deterministic scoring engine
├── ranking/
│   └── ranking_engine.py       # Weights, heuristics, and multi-threading execution
├── search/
│   ├── search_manager.py       # Query generator, orchestrator, and deduplicator
│   ├── google_provider.py      # Strict profile regex extractor via SerpAPI
│   ├── duckduckgo_provider.py  # Secondary raw HTML profile extractor
│   ├── csv_provider.py         # File ingestion 
│   └── cache_provider.py       # Avoids redundant API calls per session
├── utils/
│   ├── language_detection.py   # Determines primary spoken language of text
│   └── preprocessing.py        # Validates and cleans pandas dataframes
└── data/
    └── sample_influencers.csv  # Built-in fallback dataset
```

---

## ⚙️ Installation & Running Locally

### Prerequisites
- Python 3.9+
- [SerpAPI Key](https://serpapi.com/)
- [OpenRouter Key](https://openrouter.ai/)

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/influencer-discovery.git
   cd influencer-discovery
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Environment Variables:**
   - Copy `.env.example` to `.env`
   - Fill in your API keys in the `.env` file.

5. **Run the App:**
   ```bash
   streamlit run app.py
   ```

---

## ☁️ Deployment

This repository is strictly structured for easy deployment to **Streamlit Community Cloud**. 

Please refer to the complete, step-by-step [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) included in this repository to learn how to push your code to GitHub and host the application for free. Be sure to configure your secrets as detailed in [STREAMLIT_SECRETS_EXAMPLE.md](STREAMLIT_SECRETS_EXAMPLE.md).

---

## 🔬 Core Workflows

### Live Search Workflow
1. User enters a query (e.g., "Make In India").
2. `search_manager.py` expands this into 5 precise discovery queries targeting domains like `instagram.com` and `youtube.com`.
3. Profiles are extracted, strictly validated against regular expressions, stripped of duplicates, and ordered by baseline confidence.
4. The top candidates are passed to the `ranking_engine.py`.

### CSV Upload Workflow
1. User uploads a `.csv` via the sidebar.
2. The UI bypasses all live search APIs and parses the dataframe using `csv_provider.py`.
3. The dataset merges seamlessly into the exact same AI and ranking pipelines used by live discovery.

### Relevance Ranking Formula
Final scores are computed asynchronously by merging:
- **AI Classification Confidence** (40%) *(weighted by political/topic alignment)*
- **Keyword Matches** (30%)
- **Language Matches** (20%)
- **Normalized Follower Count** (10%)

---

## 🛠 Troubleshooting

- **No profiles found during search:** Check your SerpAPI credits. If depleted, the app gracefully falls back to DuckDuckGo HTML parsing.
- **AI Summary taking too long:** The platform natively restricts threads to `max_workers=3` to respect API rate limits. Ensure your OpenRouter tier supports concurrency.
- **App reloads when downloading CSV:** Streamlit session state is fully implemented. If this occurs, verify you are launching the application using `streamlit run app.py` and not executing it as a standard python script.

---

## 🔮 Future Improvements

While feature-complete, future production passes could include:
- Native OAuth integration with X/Twitter and Instagram Graph API for exact follower counts.
- Database persistence (PostgreSQL/Supabase) to track influencer campaigns across sessions.
- Asynchronous Celery workers for scraping operations exceeding 30-second timeouts.
