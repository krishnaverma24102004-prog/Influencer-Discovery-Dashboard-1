import pandas as pd
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def parse_followers(val) -> int:
    if pd.isna(val) or val == "" or val == "-":
        return 0
    
    val_str = str(val).lower().replace(',', '').replace('followers', '').replace('₹', '').strip()
    if not val_str:
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

def validate_and_clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates the schema of the uploaded dataframe, 
    cleans missing values, normalizes text fields, and standardizes follower counts.
    """
    required_columns = [
        "Name", "Handle", "Platform", 
        "Followers", "Language", "Bio", "Recent Posts"
    ]
    
    # 3. Automatically trim whitespace from string values
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(lambda x: str(x).strip() if pd.notna(x) and isinstance(x, str) else x)
        
    # 3. Automatically trim whitespace from column names
    df.columns = df.columns.str.strip()
    
    # 4. Normalize column names regardless of case
    df_columns_lower = {str(col).lower(): col for col in df.columns}
    
    # Add common aliases for followers
    col_aliases = {
        "follower count": "followers",
        "followers count": "followers"
    }
    
    missing_cols = []
    rename_mapping = {}
    
    for required in required_columns:
        req_lower = required.lower()
        
        found = False
        if req_lower in df_columns_lower:
            rename_mapping[df_columns_lower[req_lower]] = required
            found = True
        else:
            for alias, target in col_aliases.items():
                if target == req_lower and alias in df_columns_lower:
                    rename_mapping[df_columns_lower[alias]] = required
                    found = True
                    break
                    
        if not found:
            missing_cols.append(required)
            
    # 9. Preserve strict validation only for missing required columns
    if missing_cols:
        error_msg = f"Missing required columns: {', '.join(missing_cols)}"
        logger.error(error_msg)
        raise ValueError(error_msg)
        
    cleaned_df = df.rename(columns=rename_mapping)
    
    # 6. Attempt recovery instead of rejecting: Fill sensible defaults
    cleaned_df["Name"] = cleaned_df["Name"].fillna("Unknown")
    cleaned_df["Handle"] = cleaned_df["Handle"].fillna("Unknown")
    cleaned_df["Platform"] = cleaned_df["Platform"].fillna("Unknown")
    
    # 2. Normalize follower counts into integers
    cleaned_df["Followers"] = cleaned_df["Followers"].apply(parse_followers)
    
    cleaned_df["Language"] = cleaned_df["Language"].fillna("Unknown")
    cleaned_df["Bio"] = cleaned_df["Bio"].fillna("")
    cleaned_df["Recent Posts"] = cleaned_df["Recent Posts"].fillna("")
    
    cleaned_df["Platform"] = cleaned_df["Platform"].astype(str).str.title()
    cleaned_df["Language"] = cleaned_df["Language"].astype(str).str.title()
    
    # 9. strict validation for empty datasets
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
    combined = f"{bio} {posts}".strip()
    return combined
