# Deployment Guide

This guide provides step-by-step instructions on how to take the **AI Influencer Intelligence Platform** from your local machine, push it to GitHub, and deploy it to the world for free using Streamlit Community Cloud.

---

## 1. Creating a GitHub Repository

1. Go to [GitHub.com](https://github.com/) and log in.
2. Click the **`+`** icon in the top right corner and select **New repository**.
3. Name your repository (e.g., `influencer-discovery-platform`).
4. Set it to **Public** or **Private**.
5. Do **NOT** initialize it with a README, .gitignore, or license (we already have those files locally).
6. Click **Create repository**.

---

## 2. Initializing Git Locally

Open a terminal or command prompt in your local project folder (where `app.py` is located) and run:

```bash
git init
```

*This initializes a blank local Git repository.*

---

## 3. Adding Files to Git

Before pushing, we must stage our files. (Our `.gitignore` will ensure that secrets, API keys, and cache files are safely excluded).

```bash
git add .
```

---

## 4. Creating Your First Commit

Save a snapshot of the current state of the code:

```bash
git commit -m "Initial Commit: Ready for deployment"
```

---

## 5. Connecting to the Remote Repository

Link your local code to the GitHub repository you just created. Replace `<repository_url>` with the URL provided by GitHub (e.g., `https://github.com/yourusername/influencer-discovery-platform.git`):

```bash
git remote add origin <repository_url>
```

---

## 6. Pushing to GitHub

Set your main branch and upload the code:

```bash
git branch -M main
git push -u origin main
```

*Your code is now safely backed up on GitHub!*

---

## 7. Deploying to Streamlit Community Cloud

Now that your code is on GitHub, deploying it is easy:

1. Go to [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.
2. Click the **New app** button.
3. Select the repository you just created.
4. Set the **Branch** to `main`.
5. Set the **Main file path** to `app.py`.
6. **Stop! Do not click Deploy yet. Read the next step.**

---

## 8. Adding Streamlit Secrets (API Keys)

Since you did not upload your `.env` file containing API keys (which is the correct, secure practice), you must provide those keys directly to Streamlit's secure server.

1. Click on **Advanced settings...** at the bottom of the deployment window.
2. Scroll down to the **Secrets** text box.
3. Paste in your environment configuration using TOML format:

```toml
OPENROUTER_API_KEY = "sk-or-v1-your-actual-api-key"
SERPAPI_API_KEY = "your-actual-serpapi-key"
LLM_MODEL = "google/gemini-2.5-flash-lite"
APP_NAME = "AI Influencer Intelligence"
```

4. Click **Save**.
5. **Now, click Deploy!**

Streamlit will provision a server, install all packages from `requirements.txt`, and launch your app. 

---

## 9. Updating the App in the Future

If you make changes to the code locally and want them to appear on your live website, just run these three commands:

```bash
git add .
git commit -m "Describe your update here"
git push
```

*Streamlit will automatically detect the changes on GitHub and update your live app within seconds.*

---

## 10. Common Deployment Errors

- **`ModuleNotFoundError: No module named 'xyz'`**
  - **Cause:** A package used in your code is missing from `requirements.txt`.
  - **Fix:** Add the package to `requirements.txt`, push the file to GitHub, and Streamlit will reboot.
  
- **OpenRouter API failures or SerpAPI auth errors in production**
  - **Cause:** The secrets were not entered correctly or were formatted as bash (`KEY=VALUE`) instead of TOML (`KEY = "VALUE"`).
  - **Fix:** Go to your Streamlit dashboard, click the three dots on your app -> Settings -> Secrets, and ensure the keys are formatted with quotes exactly as shown in Step 8.
