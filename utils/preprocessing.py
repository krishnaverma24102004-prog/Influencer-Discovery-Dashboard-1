import pandas as pd
import logging
from typing import Optional

logger = logging.getLogger(__name__)

import re

def parse_followers(val) -> int:
    if pd.isna(val) or val is None:
        return 0
    val_str = str(val).lower().replace(',', '').replace('followers', '').replace('₹', '').strip()
    if val_str in ["", "nan", "none", "null", "unknown", "n/a", "blank", "-"]:
        return 0
        
    multiplier = 1
    if val_str.endswith('k'):
        multiplier = 1000
        val_str = val_str[:-1].strip()
    elif val_str.endswith('m'):
        multiplier = 1000000
        val_str = val_str[:-1].strip()
    elif val_str.endswith('b'):
        multiplier = 1000000000
        val_str = val_str[:-1].strip()
        
    try:
        return int(float(val_str) * multiplier)
    except ValueError:
        return 0

def normalize_col_name(col: str) -> str:
    return re.sub(r'[\s_-]+', '', str(col)).lower()

ALIAS_MAP = {
    # Name
    "name": "Name", "creator": "Name", "influencer": "Name", "creatorname": "Name", "fullname": "Name",
    # Handle
    "handle": "Handle", "username": "Handle", "account": "Handle", "profile": "Handle", "url": "Handle", "link": "Handle",
    # Platform
    "platform": "Platform", "channel": "Platform", "source": "Platform", "socialplatform": "Platform",
    # Followers
    "followers": "Followers", "followercount": "Followers", "followerscount": "Followers", "audience": "Followers", "subscribers": "Followers", "subs": "Followers", "reach": "Followers",
    # Language
    "language": "Language", "lang": "Language",
    # Bio
    "bio": "Bio", "description": "Bio", "about": "Bio", "profiledescription": "Bio",
    # Recent Posts
    "recentposts": "Recent Posts", "posts": "Recent Posts", "latestposts": "Recent Posts", "recentcontent": "Recent Posts", "content": "Recent Posts", "tweet": "Recent Posts", "caption": "Recent Posts"
}

def text_to_blank(val):
    if pd.isna(val) or val is None:
        return "Blank"
    val_str = str(val).strip()
    if val_str.lower() in ["", "nan", "none", "null"]:
        return "Blank"
    return val_str

def validate_and_clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates and cleans the uploaded dataframe.
    Normalizes column names, applies blank rules to missing fields,
    and standardizes follower counts without failing on missing optional columns.
    """
    
    # 3. Automatically trim whitespace from all string values globally
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(lambda x: str(x).strip() if pd.notna(x) and isinstance(x, str) else x)
        
    # Normalize column names
    rename_mapping = {}
    for col in df.columns:
        norm_col = normalize_col_name(col)
        if norm_col in ALIAS_MAP:
            rename_mapping[col] = ALIAS_MAP[norm_col]
            
    cleaned_df = df.rename(columns=rename_mapping)
    
    # 5. Only fail if BOTH Name and Handle are missing.
    if "Name" not in cleaned_df.columns and "Handle" not in cleaned_df.columns:
        error_msg = "Dataset is missing both Name and Handle columns. At least one identity field is required."
        logger.error(error_msg)
        raise ValueError(error_msg)
        
    # 4. Missing optional columns should be created automatically.
    # 9. Handle blank or missing values gracefully.
    text_cols = [
        "Name", "Handle", "Platform", "Language", "Bio", "Recent Posts", 
        "Content Niche", "Political Orientation", "Reasoning"
    ]
    
    for col in text_cols:
        if col not in cleaned_df.columns:
            cleaned_df[col] = "Blank"
        cleaned_df[col] = cleaned_df[col].apply(text_to_blank)
        
    # Normalize followers
    if "Followers" not in cleaned_df.columns:
        cleaned_df["Followers"] = 0
    cleaned_df["Followers"] = cleaned_df["Followers"].apply(parse_followers)
    
    # Numeric fields blank to 0
    for col in ["Confidence Score", "Relevance Score"]:
        if col in cleaned_df.columns:
            cleaned_df[col] = cleaned_df[col].apply(lambda x: 0 if pd.isna(x) or str(x).strip().lower() in ["", "nan", "none", "null", "blank"] else x)
            cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce').fillna(0).astype(int)
    
    # Title casing for visual consistency for Platform and Language
    cleaned_df["Platform"] = cleaned_df["Platform"].apply(lambda x: x.title() if x != "Blank" else x)
    cleaned_df["Language"] = cleaned_df["Language"].apply(lambda x: x.title() if x != "Blank" else x)
    
    if len(cleaned_df) == 0:
        raise ValueError("Dataset is empty after preprocessing.")
        
    logger.info(f"Successfully cleaned dataframe with {len(cleaned_df)} rows.")
    return cleaned_df

def extract_combined_text(row: pd.Series) -> str:
    """
    Combines Bio and Recent Posts into a single string for AI/Keyword analysis.
    """
    bio = str(row.get("Bio", ""))
    posts = str(row.get("Recent Posts", ""))
    
    # Clean up whitespace
    combined = f"{bio} {posts}".replace("Blank", "").strip()
    return combined
