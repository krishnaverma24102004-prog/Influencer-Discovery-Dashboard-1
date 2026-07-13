import streamlit as st
import pandas as pd
import tempfile
import os
import logging

from search.search_manager import execute_search
from ranking.ranking_engine import calculate_scores
import app_config as config

logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="AI Influencer Intelligence", 
    page_icon="🔍", 
    layout="wide",
    initial_sidebar_state="expanded"
)

def generate_ai_summary(results_df: pd.DataFrame):
    """Bonus feature: Generate AI summary based on top results."""
    from classifier.ai_classifier import client
    
    if not client or results_df.empty:
        st.info("AI Summary unavailable because OpenRouter is not configured or results are empty.")
        return
        
    top_5 = results_df.head(5).to_dict(orient="records")
    
    prompt = f"""
Based on the following top 5 influencers found for a government campaign, provide a concise 5-8 bullet point summary.
Include:
- Overall observations
- Top matching influencer and why they ranked highest
- Common content themes
- Language distribution
- Suggested improvements for the search

Influencers:
{top_5}
"""
    try:
        response = client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        st.markdown(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"Failed to generate AI summary: {e}")
        st.error("Could not generate AI summary at this time.")

def main():
    st.title("🔍 AI-Powered Influencer Intelligence Platform")
    
    # Initialize Session State
    if 'raw_results_df' not in st.session_state:
        st.session_state.raw_results_df = None
    if 'source' not in st.session_state:
        st.session_state.source = None
    if 'ai_summary_text' not in st.session_state:
        st.session_state.ai_summary_text = None
        
    # Sidebar Filters
    st.sidebar.header("Search Criteria")
    query = st.sidebar.text_input("Search Query", placeholder="e.g. Digital India influencers")
    language_filter = st.sidebar.selectbox("Language", ["All", "English", "Hindi"])
    platform_filter = st.sidebar.selectbox("Platform", ["All", "Twitter", "Instagram", "YouTube", "LinkedIn", "Web"])
    keywords_filter = st.sidebar.text_input("Keywords", placeholder="e.g. UPI, Healthcare")
    niche_filter = st.sidebar.selectbox("Niche", ["All", "Government Schemes", "Technology", "Healthcare", "Education", "Finance", "Lifestyle", "Agriculture"])
    orientation_filter = st.sidebar.selectbox("Political Orientation", ["All", "Pro Government", "Neutral", "Anti Government"])
    follower_range = st.sidebar.slider("Follower Range", 0, 5000000, (0, 5000000), step=10000, format="%d")
    
    st.sidebar.markdown("---")
    st.sidebar.header("Data Upload (Optional)")
    uploaded_file = st.sidebar.file_uploader("Upload CSV/Excel", type=["csv", "xlsx"])
    
    st.sidebar.markdown("---")
    col1, col2 = st.sidebar.columns(2)
    search_pressed = col1.button("Search", type="primary")
    if col2.button("Reset"):
        st.session_state.raw_results_df = None
        st.session_state.source = None
        st.session_state.ai_summary_text = None
        st.rerun()

    # Execution Block
    if search_pressed:
        if not query and not uploaded_file:
            st.warning("Please enter a search query or upload a file.")
            return
            
        with st.status("Analyzing Influencers...", expanded=True) as status:
            temp_path = None
            if uploaded_file:
                status.update(label="Reading uploaded file...")
                ext = uploaded_file.name.split('.')[-1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    temp_path = tmp.name

            try:
                # Independent Workflows
                if uploaded_file:
                    status.update(label="Processing uploaded dataset...")
                    raw_df, source = execute_search("", temp_path)
                else:
                    status.update(label="Searching live profiles...")
                    raw_df, source = execute_search(query, None)
                    
            except Exception as e:
                status.update(label="Search Failed", state="error")
                st.error(f"Error during search execution: {e}")
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)
                return
            
            # Clean up temp file
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception as e:
                    logger.warning(f"Could not remove temp file: {e}")
                
            if raw_df is None or raw_df.empty:
                status.update(label="No Data", state="error")
                st.warning("No data could be retrieved from any source.")
                return
                
            status.update(label="Running AI classification and ranking...")
            try:
                results_df = calculate_scores(raw_df, target_language="All")
                
                # Cache results in session state
                st.session_state.raw_results_df = results_df
                st.session_state.source = source
                st.session_state.ai_summary_text = None # Reset summary for new search
                status.update(label="Analysis Complete!", state="complete", expanded=False)
            except Exception as e:
                status.update(label="Ranking Failed", state="error")
                st.error(f"Error during ranking: {e}")
                return

    # Render Dashboard from Session State
    if st.session_state.raw_results_df is not None:
        results_df = st.session_state.raw_results_df.copy()
        
        # Apply UI filters dynamically to the cached dataframe
        if language_filter != "All":
            results_df = results_df[results_df["Language"].str.contains(language_filter, case=False, na=False)]
        if platform_filter != "All":
            results_df = results_df[results_df["Platform"].str.contains(platform_filter, case=False, na=False)]
        if niche_filter != "All":
            results_df = results_df[results_df["Content Niche"].str.contains(niche_filter, case=False, na=False)]
        if orientation_filter != "All":
            results_df = results_df[results_df["Political Orientation"].str.contains(orientation_filter, case=False, na=False)]
        
        min_f, max_f = follower_range
        results_df = results_df[(results_df["Followers"] >= min_f) & (results_df["Followers"] <= max_f)]
        
        if keywords_filter.strip():
            kws = [k.strip().lower() for k in keywords_filter.split(",")]
            def kw_match(row):
                text = f"{row.get('Reason for Selection', '')} {row.get('Name', '')} {row.get('Content Niche', '')}".lower()
                return any(k in text for k in kws)
            results_df = results_df[results_df.apply(kw_match, axis=1)]

        if results_df.empty:
            st.warning("No influencers matched the selected UI filters.")
            return

        # Display Dashboard
        st.success("Analysis Complete!")
        source = st.session_state.source
        
        if not uploaded_file and source in ["Sample Dataset", "CSV Upload"]:
            st.info("Live search is currently unavailable. Showing locally available influencer data.")
            
        m1, m2, m3 = st.columns(3)
        m1.metric("Current Data Source", source)
        m2.metric("Total Results", len(results_df))
        m3.metric("Language Filter", language_filter)
        
        st.markdown("### Top Influencers")
        display_df = results_df[[
            "Name", "Handle", "Platform", "Followers", "Language", 
            "Content Niche", "Political Orientation", "Confidence", 
            "Relevance Score", "Reason for Selection"
        ]]
        st.dataframe(display_df, use_container_width=True)
        
        # Export CSV (No re-run)
        csv_data = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Export Results (CSV)",
            data=csv_data,
            file_name="influencers.csv",
            mime="text/csv",
        )
        
        # AI Summary (Only run once per search)
        st.markdown("---")
        st.markdown("### 🤖 AI Summary")
        if st.session_state.ai_summary_text is None:
            with st.spinner("Generating AI Summary..."):
                from classifier.ai_classifier import client
                if not client or results_df.empty:
                    st.session_state.ai_summary_text = "AI Summary unavailable because OpenRouter is not configured or results are empty."
                else:
                    top_5 = results_df.head(5).to_dict(orient="records")
                    prompt = f"""
Based on the following top 5 influencers found for a government campaign, provide a concise 5-8 bullet point summary.
Include: Overall observations, top matching influencer, common themes, language distribution, and suggested improvements.
Influencers: {top_5}
"""
                    try:
                        response = client.chat.completions.create(
                            model=config.LLM_MODEL,
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.3
                        )
                        st.session_state.ai_summary_text = response.choices[0].message.content
                    except Exception as e:
                        logger.error(f"Failed to generate AI summary: {e}")
                        st.session_state.ai_summary_text = "Could not generate AI summary at this time."
                        
        st.markdown(st.session_state.ai_summary_text)

    else:
        st.info("Enter a search query or upload data, then click 'Search' in the sidebar.")
        st.markdown("""
        **Features:**
        - **Real-Time Search**: Uses SerpAPI to find live profiles.
        - **CSV Upload**: Analyze your own dataset.
        - **AI Classification**: Uses Gemini (via OpenRouter) to semantically classify influencers.
        - **Fallback**: Automatically degrades to keyword mapping and built-in datasets if APIs fail.
        """)

if __name__ == "__main__":
    main()
