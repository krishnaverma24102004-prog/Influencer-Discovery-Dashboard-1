import logging
import pandas as pd
import app_config as config
from classifier.keyword_classifier import evaluate_keywords
from classifier.ai_classifier import classify_influencer
from utils.language_detection import detect_language, is_language_match
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

def calculate_scores(df: pd.DataFrame, target_language: str = "All") -> pd.DataFrame:
    """
    Processes the dataframe, applies classification, and calculates the final relevance score.
    Returns the dataframe sorted by relevance score.
    """
    results = []
    
    # Define a helper function for multithreading
    def process_row(row):
        combined_text = f"{row.get('Bio', '')} {row.get('Recent Posts', '')}".strip()
        name = row.get("Name", "Unknown")
        
        # 1. Language Detection & Match (20%)
        detected_lang = detect_language(combined_text)
        if target_language.lower() != "all" and detected_lang.lower() == target_language.lower():
            lang_score = 1.0
        elif target_language.lower() == "all":
            lang_score = 1.0 # If no filter, max score
        else:
            lang_score = 0.0
            
        # 2. Keyword Match (30%)
        kw_result = evaluate_keywords(combined_text)
        kw_score = kw_result["score"]
        
        # 3. AI Classification (40%)
        # Note: classify_influencer is cached via @st.cache_data
        ai_result = classify_influencer(
            name=name,
            bio=row.get("Bio", ""),
            recent_posts=row.get("Recent Posts", "")
        )
        
        ai_confidence = float(ai_result.get("Confidence Score", 0)) / 100.0
        
        # Weigh AI score based on alignment to Government Initiatives
        gov_support = str(ai_result.get("Government Support", "Neutral")).lower()
        orientation = str(ai_result.get("Political Orientation", "Neutral")).lower()
        
        alignment_multiplier = 0.5
        if "pro" in orientation or gov_support in ["high", "medium"]:
            alignment_multiplier = 1.0
        elif "anti" in orientation or gov_support == "low":
            alignment_multiplier = 0.2
            
        ai_score = ai_confidence * alignment_multiplier
        
        # 4. Followers (10%)
        followers = float(row.get("Followers", 0))
        # Normalize followers assuming 1,000,000 is maximum effective cap
        follower_score = min(followers / 1000000.0, 1.0)
        
        # Final Score Calculation
        final_score = (
            (ai_score * config.WEIGHT_AI_CLASSIFICATION) +
            (kw_score * config.WEIGHT_KEYWORD_MATCH) +
            (lang_score * config.WEIGHT_LANGUAGE_MATCH) +
            (follower_score * config.WEIGHT_FOLLOWERS)
        )
        
        # Build Results Row
        reasoning = ai_result.get("Reasoning", "No AI reasoning available.")
        if kw_result["matched_keywords"]:
            reasoning += f" Matched keywords: {', '.join(kw_result['matched_keywords'])}."
            
        return {
            "Name": name,
            "Handle": row.get("Handle", ""),
            "Platform": row.get("Platform", ""),
            "Followers": int(followers),
            "Language": ai_result.get("Language", detected_lang),
            "Content Niche": ai_result.get("Content Niche", "Unknown"),
            "Political Orientation": ai_result.get("Political Orientation", "Neutral"),
            "Confidence": int(ai_result.get("Confidence Score", 0)),
            "Relevance Score": round(final_score * 100, 1),
            "Reason for Selection": reasoning
        }

    # Execute classifications concurrently
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(process_row, row) for _, row in df.iterrows()]
        
        for future in as_completed(futures):
            try:
                result_row = future.result()
                results.append(result_row)
            except Exception as e:
                logger.error(f"Error processing row concurrently: {e}")
                
    result_df = pd.DataFrame(results)
    
    if not result_df.empty:
        result_df = result_df.sort_values(by="Relevance Score", ascending=False).reset_index(drop=True)
        
    return result_df
