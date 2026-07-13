# 🎯 Assignment Submission & Presentation Kit

This document provides a strategic write-up of the development process, a demo walkthrough script, and preparation for technical interview questions. Use this during your presentation or submit it alongside your assignment.

---

## 📝 1. Technical Write-Up: Approach & Architecture

### My Approach
My primary goal was to build a production-ready intelligence platform that prioritized **reliability, explainability, and modularity**. Rather than building a monolithic script, I adopted a layered architecture separating the Data (Search), Logic (Classification/Ranking), and Presentation (Streamlit) layers. This ensures that the codebase can scale easily, and individual components (like the search provider) can be swapped out without breaking the system.

### Assumptions Made
1. **API Volatility:** I assumed that free-tier APIs (like OpenRouter or SerpAPI) would frequently hit rate limits, timeout, or return empty/malformed responses. 
2. **Data Inconsistency:** I assumed that uploaded CSV files would have missing fields, varied casing, and NaN values, requiring strict preprocessing before hitting the logic layer.
3. **Execution Speed:** I assumed that blocking the main thread to run LLM inferences sequentially on 100+ profiles would ruin the UX, hence the strict `max_tokens` limits and reliance on caching.

### Search Strategy
The search strategy relies on a strict **Degradation Hierarchy** implemented in the `SearchManager`:
1. **Live Web Search (SerpAPI):** The primary source of truth for real-time influencer discovery.
2. **DuckDuckGo Scraper:** A zero-cost fallback if SerpAPI exhausts its quota.
3. **Local CSV Upload:** Allows analysts to bypass live search entirely and analyze proprietary data.
4. **Sample Dataset:** An absolute fallback so the UI never crashes or displays a blank screen, guaranteeing a successful demo.

### AI Classification Approach
I utilized OpenRouter (mapped to the OpenAI Python SDK) to interact with `openrouter/free`. The prompt was aggressively optimized using `temperature=0.1` and `max_tokens=250` to force the LLM to act strictly as a data-extraction engine rather than a conversational agent. I enforced a strict JSON schema return, allowing the system to easily map properties like "Political Orientation" and "Content Niche" directly into Pandas DataFrames.

### Keyword Fallback Approach
Because LLMs fail (due to quotas, timeouts, or content filters), I implemented a deterministic **Rule-Based Keyword Classifier**. If the `ai_classifier` throws any exception (e.g., `402 Payment Required`), it gracefully hands the text off to the keyword engine, which scans for predefined domain keywords (e.g., "UPI", "Digital India"). This guarantees 100% classification uptime.

### Ranking Methodology
The ranking engine normalizes scores on a 0–100 scale using a transparent, weighted mathematical formula configured in `app_config.py`:
- **40% AI Confidence:** Heavy emphasis on semantic understanding.
- **30% Keyword Match:** High reward for explicit domain relevance.
- **20% Language Match:** Ensures the influencer speaks the target demographic's language.
- **10% Followers:** A minor boost for reach, ensuring niche-but-relevant micro-influencers can still outrank generic celebrities.

### Why This Design Was Chosen
This design was chosen because it mirrors **Enterprise Reliability Patterns**. In real-world AI engineering, models fail constantly. By wrapping the AI in a `try/except` block and providing a localized, deterministic fallback (keywords + CSVs), the application transforms from a fragile prototype into a resilient, production-ready product.

---

## 🎬 2. Demo Walkthrough Script

*Use this step-by-step guide when presenting the application to evaluators.*

1. **Launch the App:** 
   *"I'll start the application by running `streamlit run app.py`. As you can see, the Streamlit interface boots into a clean, modern layout with a sidebar for configuration."*

2. **Live Search Demonstration:**
   *"Let's look for influencers discussing 'Digital India'. I'll type that into the search query and hit Search. The `SearchManager` connects to SerpAPI to fetch live Google profiles. You'll notice the loader spinning as it extracts the bios."*

3. **Explaining AI vs. Fallback in Real-Time:**
   *"Once the data is fetched, it's sent to the OpenRouter AI model. However, to guarantee uptime, I've built a fallback system. If OpenRouter throws a rate-limit error, you won't see a crash—the backend seamlessly falls back to my native NLP keyword scanner. Right now, you can see the results table populated with Content Niche and Political Orientation data."*

4. **Ranking & Filtering:**
   *"Notice the 'Relevance Score' column. It's not just a random number. I implemented a weighted formula factoring in AI semantic score, keyword density, language, and reach. Using the sidebar, I can filter these results instantly by Platform or Niche without re-running the expensive API calls."*

5. **Data Upload & Export:**
   *"If we wanted to analyze an offline database, we could use the CSV Upload feature here. Finally, we can export the exact filtered views to a CSV using this button, and at the bottom, an AI agent has summarized the entire campaign for us."*

---

## 🧠 3. Common Interview Questions & Answers

**Q: Why did you choose a hybrid AI + rule-based (keyword) approach?**
**A:** "Relying solely on LLMs is risky for production systems due to rate limits, latency, and costs. A hybrid approach ensures resilience. The AI handles nuanced semantic understanding, but the rule-based keyword engine acts as a safety net. If the LLM goes down, the application still functions perfectly."

**Q: Why use OpenRouter instead of connecting to OpenAI directly?**
**A:** "OpenRouter acts as a unified router. By integrating it via the standard OpenAI SDK, I effectively decoupled the application from any single provider. By just changing a string in the `.env` file, this app can instantly switch from Gemini to Llama 3 to GPT-4o without altering a single line of business logic."

**Q: How is the relevance score calculated?**
**A:** "It's a weighted linear combination. I assigned 40% to AI confidence, 30% to keyword matches, 20% to language alignment, and 10% to follower count. This prevents massive celebrities with generic content from outranking highly-relevant micro-influencers."

**Q: How would you scale this application?**
**A:** "Currently, classification is synchronous. For scale, I would refactor the `ai_classifier.py` to use `asyncio` and `aiohttp` for concurrent API calls. I would also introduce a vector database like PostgreSQL with pgvector to cache semantic embeddings, reducing redundant LLM calls for influencers we've already classified."

**Q: What improvements would you make in production?**
**A:** "I'd implement a message queue (like Celery/Redis) to handle heavy CSV uploads asynchronously so the Streamlit UI doesn't block. I'd also expand the web scraping layer using Apify to pull detailed user timelines rather than just short SERP snippets, providing the LLM with richer context."
