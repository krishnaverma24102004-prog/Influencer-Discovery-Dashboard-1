# Streamlit Community Cloud Secrets Guide

When deploying this application to Streamlit Community Cloud, you **cannot** commit your `.env` file containing API keys to GitHub for security reasons.

Instead, Streamlit Community Cloud provides a secure way to manage your environment variables via **Secrets Management**.

## How to Configure Secrets

1. Push your repository to GitHub.
2. Log in to [Streamlit Community Cloud](https://share.streamlit.io).
3. Click **New app** and select your repository, branch, and main file path (`app.py`).
4. **Before clicking Deploy**, click on **Advanced settings...**
5. Locate the **Secrets** section.
6. Copy the template below and paste it into the Secrets text box. Replace the placeholder values with your actual API keys.

### Secrets Template (TOML Format)

```toml
OPENROUTER_API_KEY = "sk-or-v1-your-actual-openrouter-key-here"
SERPAPI_API_KEY = "your-actual-serpapi-key-here"
LLM_MODEL = "google/gemini-2.5-flash-lite"
APP_NAME = "AI Influencer Intelligence"
```

7. Click **Save** and then deploy the app.

> **Note:** If you've already deployed the app, you can access the Secrets menu by clicking on the three dots (App Settings) in the bottom right corner of your running app and selecting **Settings > Secrets**.
